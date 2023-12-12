import os
import pickle
import string
from typing import List
import re

import pandas as pd
from tqdm import tqdm
from wcvp_download import infraspecific_chars, hybrid_characters, wcvp_columns

from taxonomy_inputs import taxonomy_inputs_output_path, project_path

scratch_path = os.environ.get('SCRATCH')

homonym_df = pd.read_csv(os.path.join(taxonomy_inputs_output_path, 'ambiguous_homonyms', 'homonyms.csv'))

names_to_search = sorted(homonym_df[wcvp_columns['name']].unique().tolist())
core_project_path = os.path.join(project_path, 'CORE_searches')
filter_dict_pkl = os.path.join(core_project_path, 'temp_outputs', 'saved_dictionary.pkl')

longest_ambiguous_homonym = 3
longest_potential_disambiguator = 10


def retrieve_text_before_simple_phrase(given_text: str, simple_string: str) -> str:
    my_regex = r"(?:(?:^\s*\d*\s*" + re.escape(simple_string) + r"\n)|(?:^\s*" + re.escape(simple_string) + r"\s*\n))"
    # Split by looking for an instance of simple_string (ignoring case) begins a line on its own (or with line numbers) followed by any amount of whitespace and then a new line
    # Must use re.MULTILINE flag such that the pattern character '^' matches at the beginning of the string and at the beginning of each line (immediately following each newline)
    text_split = re.split(my_regex, given_text, maxsplit=1, flags=re.IGNORECASE | re.MULTILINE)
    pre_split = text_split[0]
    if len(text_split) > 1:
        post_split = text_split[
            1]  # If maxsplit is nonzero, at most maxsplit splits occur, and the remainder of the string is returned as the final element of the list
        # if text after split point is longer than before, then revert.
        if len(post_split) > len(pre_split):
            pre_split = given_text

    return pre_split


def clean_paper_text(text: str) -> str:
    if text is None:
        return None

    # Split by looking for an instance of 'Supplementary material' (ignoring case)
    # begins a line on its own (followed by any amount of whitespace and then a new line)
    pre_reference = retrieve_text_before_simple_phrase(text, 'References')
    pre_supplementary = retrieve_text_before_simple_phrase(pre_reference, 'Supplementary material')
    pre_conflict = retrieve_text_before_simple_phrase(pre_supplementary, 'Conflict of interest')
    pre_acknowledgement = retrieve_text_before_simple_phrase(pre_conflict, 'Acknowledgments')

    return clean_string(pre_acknowledgement)


def clean_string(given_string) -> str:
    # Clean strings so that matches aren't missed based on punctuation, extra whitespace, or casing (but leaving hybrid characters.

    if given_string is not None:
        to_strip = string.punctuation
        for h in hybrid_characters:
            to_strip = to_strip.replace(h, '')
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
    '''
    Returns a dictionary of disambiugating phrases for each homonym
    :return:
    '''
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

        out_list += relevant_taxa['sp_binomial_with_abbreviated_genus_with_authors'].unique().tolist()
        out_list += relevant_taxa['sp_binomial_with_abbreviated_genus_with_paranthet_authors'].unique().tolist()
        out_list += relevant_taxa['sp_binomial_with_abbreviated_genus_with_primary_author'].unique().tolist()

        unique_out_list = list(set(out_list))
        cleaned = [clean_string(v) for v in unique_out_list]

        name_terms_dict[clean_string(taxon_name)] = cleaned
    with open(filter_dict_pkl, 'wb') as f:
        pickle.dump(name_terms_dict, f)


if __name__ == '__main__':
    _get_filter_dict()
