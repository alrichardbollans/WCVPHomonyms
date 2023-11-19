import os

import pandas as pd
from pkg_resources import resource_filename
from wcvp_download import wcvp_columns

from taxonomy_inputs import taxonomy_inputs_output_path

summary_path = os.path.join(taxonomy_inputs_output_path, 'summaries')


def proportion_of_homonyms_in_wcvp():
    num_ambiguous_records = len(ambiguous_homonyms['plant_name_id'].unique().tolist())
    num_ambiguous_homonymous_names = len(ambiguous_homonyms['taxon_name'].unique().tolist())

    num_records = len(given_wcvp_data['plant_name_id'].unique().tolist())
    num_names = len(given_wcvp_data['taxon_name'].unique().tolist())

    pd.DataFrame([[num_records, num_names], [num_ambiguous_records, num_ambiguous_homonymous_names]], columns=['records', 'names'],
                 index=['all species', 'ambiguous_homonyms']).to_csv(
        os.path.join(summary_path, 'number_of_homonyms.csv'))


def proportion_of_homonyms_which_are_also_accepted():
    pass


def number_of_homonyms_resolving_to_different_genus():
    pass


if __name__ == '__main__':
    given_wcvp_data = pd.read_csv(os.path.join(taxonomy_inputs_output_path, 'wcvp_data.csv'), index_col=0, dtype={'publication_year': 'Int64'})
    all_homonyms = pd.read_csv(os.path.join(taxonomy_inputs_output_path, 'all_homonyms', 'homonyms.csv'), dtype={'publication_year': 'Int64'})
    ambiguous_homonyms = pd.read_csv(os.path.join(taxonomy_inputs_output_path, 'ambiguous_homonyms', 'homonyms.csv'),
                                     dtype={'publication_year': 'Int64'})
    proportion_of_homonyms_in_wcvp()
