import json
import multiprocessing
import os
import pickle
import tarfile
import time
from typing import Tuple, List

import numpy as np
import pandas as pd

import sys

sys.path.append('..')

from CORE_searches import build_output_dict, core_project_path, filter_dict_pkl, clean_string, clean_paper_text, longest_ambiguous_homonym, \
    longest_potential_disambiguator

scratch_path = os.environ.get('SCRATCH')

core_MPM_project_path = os.path.join(scratch_path, 'MedicinalPlantMining', 'literature_downloads', 'core')
CORE_TAR_FILE = os.path.join(core_MPM_project_path, 'core_2022-03-11_dataset.tar.xz')

core_paper_info_path = os.path.join(core_project_path, 'downloads', 'paper_info')
for p in [core_paper_info_path]:
    if not os.path.exists(p):
        os.mkdir(p)


def get_lists_of_words(words: List[str], largest_phrase: int) -> List[str]:
    out_list = words.copy()
    to_check = range(largest_phrase + 1)[2:]
    for i in to_check:
        add_list = [" ".join([words[j + c] for c in range(i)]) for j in range(len(words) - i + 1)]
        out_list += add_list
    return out_list


def find_ambiguous_uses(text: str) -> Tuple[List[str], List[str], dict]:
    # start_time = time.time()

    # Look for ambiguous uses in body text
    clean_body_text = clean_paper_text(text)
    # clean_time = time.time()
    # time1 = round((clean_time - start_time), 2)

    clean_body_text_list = clean_body_text.split()
    potential_homonym_uses = get_lists_of_words(clean_body_text_list, longest_ambiguous_homonym)

    # Find potentially ambiguous words
    intersection = set(potential_homonym_uses).intersection(homonyms)
    # intersect_time = time.time()
    # time2 = round((intersect_time - clean_time), 2)
    if len(intersection) > 0:
        homonym_uses = list(intersection)
        ambiguous_uses = []
        disambiguators = {}

        # Look for disambiguations anywhere in text
        clean_text_anywhere = clean_string(text)
        clean_text_anywhere_list = clean_text_anywhere.split()
        potential_disambiguators = set(get_lists_of_words(clean_text_anywhere_list, longest_potential_disambiguator))
        # disambg_time = time.time()
        # time3 = round((disambg_time - intersect_time), 2)

        for homonym in homonym_uses:
            disambiguators[homonym] = list(set(loaded_filter_dict[homonym]).intersection(potential_disambiguators))
            if len(disambiguators[homonym]) == 0:
                ambiguous_uses.append(homonym)
                del disambiguators[homonym]

        if len(ambiguous_uses) == 0:
            assert len(list(disambiguators.keys())) > 0
        if len(ambiguous_uses) == len(homonym_uses):
            assert len(list(disambiguators.keys())) == 0

        # end_time = time.time()
        # total_time = end_time - start_time
        # if total_time > 1:
        #     print(f'Took {time1} to clean text of length: {len(text)}.')
        #     print(f'Took {time2} to check intersection with lengths : {len(potential_homonym_uses)}:{len(homonyms)}.')
        #     print(f'Took {time3} to clean strings and get potential disambiguators with text length : {len(text)}.')
        #     print(
        #         f'Took {round((end_time - disambg_time), 2)}  to search through homonyms with {len(potential_disambiguators)} potential disambiguators.')
        #     print(f'Total time: {total_time}')
        return homonym_uses, ambiguous_uses, disambiguators
    else:
        # end_time = time.time()
        # total_time = end_time - start_time
        # if total_time > 1:
        #     print(f'Took {time1} to clean text of length: {len(text)}.')
        #     print(f'Took {time2} to check intersection with lengths : {len(potential_homonym_uses)}:{len(homonyms)}.')
        #     print(f'Total time: {total_time}')
        return [], [], {}


def clean_title_strings(given_title: str) -> str:
    ## Also need to fix encodings e.g. \\u27
    if given_title is not None:
        fixed_whitespace = ' '.join(given_title.split())
        return fixed_whitespace
    else:
        return given_title


def get_info_from_core_paper(paper: dict):
    corpusid = paper['coreId']
    try:
        language = paper['language']['code']
    except TypeError:
        language = None

    if len(paper['journals']) >= 1:
        journals = str(paper['journals'])
    else:
        journals = None
    if len(paper['subjects']) >= 1:
        subjects = str(paper['subjects'])
    else:
        subjects = None
    if len(paper['topics']) >= 1:
        topics = str(paper['topics'])
    else:
        topics = None

    year = paper['year']
    issn = paper['issn']
    doi = paper['doi']
    oai = paper['oai']
    title = clean_title_strings(paper['title'])
    authors = paper['authors']
    url = paper['downloadUrl']
    return corpusid, language, journals, subjects, topics, year, issn, doi, title, authors, url, oai


def process_tar_paper_member_lines(lines):
    paper = json.loads(lines[0])
    if len(lines) > 1:
        raise ValueError('Unexpected number of lines in archive')

    text = paper['fullText']
    if text is not None:
        homonym_uses, ambiguous_uses, disambiguators = find_ambiguous_uses(text)
        if len(homonym_uses) > 0:
            corpusid, language, journals, subjects, topics, year, issn, doi, title, authors, url, oai = get_info_from_core_paper(
                paper)

            info_df = pd.DataFrame(
                build_output_dict(corpusid, doi, year, title, authors,
                                  url, language, journals, issn, homonym_uses, ambiguous_uses, disambiguators))
            return info_df


def get_relevant_papers_from_download():
    print('unzipping main archive')
    with tarfile.open(CORE_TAR_FILE, 'r') as main_archive:
        # This is slow but useful info. # Main archive length: 10251
        # print(f'Main archive length: {len(main_archive.getnames())}')
        # names = main_archive.getnames()
        # iterate over members then get all members out of these
        # Each member is a Data provider, see here: https://core.ac.uk/data-providers
        print('unzipped main archive')
        for provider in main_archive:
            provider_file_obj = main_archive.extractfile(provider)
            tar_archive_name = os.path.basename(provider.name)
            provider_csv = os.path.join(core_paper_info_path, tar_archive_name + '.csv')

            # Check if already done. Useful for when e.g. cluster fails
            if not os.path.isfile(provider_csv):
                start_time = time.time()

                with tarfile.open(fileobj=provider_file_obj, mode='r') as sub_archive:
                    # members = sub_archive.getmembers()  # Get members will get all files recursively, though deeper archives will need extracting too.

                    tasks = []
                    provider_outputs = []
                    with multiprocessing.Pool(128) as pool:
                        for paper_member in sub_archive:
                            if paper_member.name.endswith('.json'):
                                # Cannot serialize these objects, so get lines out before adding to process
                                f = sub_archive.extractfile(paper_member)
                                lines = f.readlines()
                                tasks.append(pool.apply_async(process_tar_paper_member_lines, args=(lines,)))
                            elif '.tar' in paper_member.name:
                                print('Need more recursion')
                                raise ValueError

                        for task in tasks:
                            paper_df = task.get()
                            if paper_df is not None:
                                provider_outputs.append(paper_df)

                if len(provider_outputs) > 0:
                    provider_df = pd.concat(provider_outputs)
                else:
                    provider_df = pd.DataFrame()
                    provider_df['corpusid'] = np.nan

                provider_df['tar_archive_name'] = tar_archive_name
                provider_df.set_index(['corpusid'], drop=True).to_csv(provider_csv)
                end_time = time.time()
                print(
                    f'{len(provider_df)} papers collected from provider: {tar_archive_name}. Took {round((end_time - start_time) / 60, 2)} mins.')

            else:
                print(f'Already checked: {provider_csv}')


if __name__ == '__main__':
    with open(filter_dict_pkl, 'rb') as f:
        loaded_filter_dict = pickle.load(f)
        homonyms = set(loaded_filter_dict.keys())
        get_relevant_papers_from_download()
