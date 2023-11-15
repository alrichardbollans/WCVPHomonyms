import os
import pickle
import string
from typing import List

import pandas as pd
from tqdm import tqdm
from wcvp_download import infraspecific_chars, hybrid_characters, wcvp_columns

from taxonomy_inputs import taxonomy_inputs_output_path, project_path

scratch_path = os.environ.get('SCRATCH')

homonym_df = pd.read_csv(os.path.join(taxonomy_inputs_output_path, 'ambiguous_homonyms', 'homonyms.csv'))

names_to_search = sorted(homonym_df[wcvp_columns['name']].unique().tolist())
core_project_path = os.path.join(project_path, 'CORE_searches')
filter_dict_pkl = os.path.join(core_project_path, 'temp_outputs', 'saved_dictionary.pkl')


def clean_string(given_string) -> str:
    # Clean strings so that matches aren't missed based on punctuation, extra whitespace, or casing.
    to_strip = string.punctuation
    for h in hybrid_characters:
        to_strip = to_strip.replace(h, '')
    if given_string is not None:
        words = [w.strip(to_strip).lower() for w in given_string.split()]
        if '' in words:
            words.remove('')
        out = ' '.join(words)
        return out
    else:
        return given_string


def build_output_dict(corpusid: str, doi: str, year: str, title: str, authors: List[str],
                      url: str, language: str, journals: str, issn: str, homonym_uses: List[str], ambiguous_uses: List[str],
                      disambiguators: dict):
    out_dict = {'corpusid': [corpusid], 'DOI': [doi], 'year': year, 'language': language, 'journals': journals, 'issn': issn,
                'title': [title], 'authors': [str(authors)], 'oaurl': [url], 'homonym_uses': [str(homonym_uses)],
                'ambiguous_uses': [str(ambiguous_uses)], 'disambiguators': [str(disambiguators)]}

    return out_dict


def _get_filter_dict():
    name_terms_dict = {}
    for i in tqdm(range(len(names_to_search))):
        taxon_name = names_to_search[i]
        out_list = []

        # Add strings that indicate binomial not used on its own.
        for ch in infraspecific_chars + hybrid_characters:
            out_list.append(taxon_name + ' ' + ch)

        relevant_taxa = homonym_df[homonym_df[wcvp_columns['name']] == taxon_name]
        out_list += relevant_taxa['taxon_names_with_authors'].unique().tolist()
        out_list += relevant_taxa['taxon_names_with_paranthet_authors'].unique().tolist()
        out_list += relevant_taxa['taxon_names_with_primary_author'].unique().tolist()

        unique_out_list = list(set(out_list))
        cleaned = [clean_string(v) for v in unique_out_list]

        name_terms_dict[clean_string(taxon_name)] = cleaned
    with open(filter_dict_pkl, 'wb') as f:
        pickle.dump(name_terms_dict, f)


def _find_longest_search_terms():
    with open(filter_dict_pkl, 'rb') as f:
        loaded_filter_dict = pickle.load(f)
        longest = 0
        longest_ambiguous = 0
        for key in loaded_filter_dict:
            num_words_in_key = len(key.split())
            if num_words_in_key > longest_ambiguous:
                longest_ambiguous = num_words_in_key
                biggest_ambiguous = key

            for item in loaded_filter_dict[key]:
                num_words = len(item.split())
                if num_words > longest:
                    longest = num_words
                    biggest = item
        print(f'Longest disambiguator: {longest} words: {biggest}')
        print(f'Longest ambiguous term: {longest_ambiguous} words: {biggest_ambiguous}')
    if longest_ambiguous > 3:
        raise ValueError('Need to fix searching for more than 5 words')


if __name__ == '__main__':
    _get_filter_dict()
    _find_longest_search_terms()
