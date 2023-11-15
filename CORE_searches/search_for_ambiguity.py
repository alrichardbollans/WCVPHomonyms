import _lzma
import json
import multiprocessing
import os
import tarfile
import time

import pandas as pd

from CORE_searches import find_ambiguous_uses, build_output_dict, core_project_path

scratch_path = os.environ.get('SCRATCH')

core_MPM_project_path = os.path.join(scratch_path, 'MedicinalPlantMining', 'literature_downloads', 'core')
CORE_TAR_FILE = os.path.join(core_MPM_project_path, 'core_2022-03-11_dataset.tar.xz')

core_paper_info_path = os.path.join(core_project_path, 'downloads', 'paper_info')


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


def process_tar_member(provider):
    start_time = time.time()
    provider_df = pd.DataFrame()
    total_paper_count = 0
    with tarfile.open(CORE_TAR_FILE, 'r') as main_archive:
        provider_file_obj = main_archive.extractfile(provider)
        tar_archive_name = os.path.basename(provider.name)

        with tarfile.open(fileobj=provider_file_obj, mode='r') as sub_archive:
            try:
                members = sub_archive.getmembers()  # Get members will get all files recursively, though deeper archives will need extracting too.
                for i in range(len(members)):
                    m = members[i]
                    if m.name.endswith('.json'):
                        total_paper_count += 1
                        f = sub_archive.extractfile(m)
                        lines = f.readlines()
                        paper = json.loads(lines[0])
                        text = paper['fullText']

                        if text is not None:
                            ambiguous_uses = find_ambiguous_uses(text)
                            if len(ambiguous_uses) > 0:
                                corpusid, language, journals, subjects, topics, year, issn, doi, title, authors, url, oai = get_info_from_core_paper(
                                    paper)

                                info_df = pd.DataFrame(
                                    build_output_dict(corpusid, doi, year, ambiguous_uses, title, authors,
                                                      url, language, journals, issn))

                                provider_df = pd.concat([provider_df, info_df])
                    elif m.name.endswith('.xml'):
                        f = sub_archive.extractfile(m)
                        lines = f.readlines()
                    elif '.tar' in m.name:
                        print('Need more recursion')
                        raise ValueError
            except _lzma.LZMAError:
                print(f'LZMAError for: {sub_archive}')

    if len(provider_df.index) > 0:
        provider_df['tar_archive_name'] = tar_archive_name
        provider_df.set_index(['corpusid'], drop=True).to_csv(os.path.join(core_paper_info_path, tar_archive_name + '.csv'))
    end_time = time.time()
    print(
        f'{len(provider_df)} out of {total_paper_count} papers collected from provider: {tar_archive_name}. Took {round((end_time - start_time) / 60, 2)} mins.')
    return provider_df


def get_relevant_papers_from_download():
    print('unzipping main archive')
    with tarfile.open(CORE_TAR_FILE, 'r') as main_archive:
        # This is slow but useful info. # Main archive length: 10251
        # print(f'Main archive length: {len(main_archive.getnames())}')
        # names = main_archive.getnames()
        # iterate over members then get all members out of these
        # Each member is a Data provider, see here: https://core.ac.uk/data-providers
        print('unzipped main archive')
        with multiprocessing.Pool(64) as pool:
            tasks = [pool.apply_async(process_tar_member, args=(member,)) for member in main_archive]
            # Wait for all tasks to complete
            for task in tasks:
                task.get()


if __name__ == '__main__':
    get_relevant_papers_from_download()
