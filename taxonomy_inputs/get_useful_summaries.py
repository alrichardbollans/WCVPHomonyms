import os

import pandas as pd
from wcvpy.wcvp_download import wcvp_columns, wcvp_accepted_columns

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
    ambiguous_homonymous_names = ambiguous_homonyms['taxon_name'].unique().tolist()

    ambiguous_homonyms_that_are_also_accepted = given_wcvp_data[given_wcvp_data[wcvp_columns['status']] == 'Accepted']
    ambiguous_homonyms_that_are_also_accepted = ambiguous_homonyms_that_are_also_accepted[
        ambiguous_homonyms_that_are_also_accepted['taxon_name'].isin(ambiguous_homonymous_names)]['taxon_name'].unique().tolist()

    pd.DataFrame([[len(ambiguous_homonyms_that_are_also_accepted), len(ambiguous_homonymous_names)]],
                 columns=['ambiguous_homonyms_that_are_also_accepted', 'ambiguous_homonymous_names'],
                 index=['counts']).to_csv(
        os.path.join(summary_path, 'proportion_of_homonyms_which_are_also_accepted.csv'))


def number_of_homonyms_resolving_to_different_genus():
    pass


def get_most_common_names():
    # most_common_accepted_name = all_homonyms[wcvp_accepted_columns['name_w_author']].mode()
    # common_acc_df = all_homonyms[all_homonyms[wcvp_accepted_columns['name_w_author']].isin(most_common_accepted_name.values)]
    # common_acc_df.to_csv(os.path.join(summary_path, 'most_common_accepted_name_with_homonyms.csv'))

    most_common_homonym = all_homonyms['taxon_name'].mode()
    common_homonym_df = all_homonyms[all_homonyms['taxon_name'].isin(most_common_homonym.values)]
    common_homonym_df.to_csv(os.path.join(summary_path, 'most_common_homonym.csv'))

    homonym_that_refers_to_most_different_species = ambiguous_homonyms.groupby([wcvp_columns['name']])[wcvp_accepted_columns['species']].nunique(
        dropna=True).sort_values(ascending=False).index[0]
    worst_homonym_df = all_homonyms[all_homonyms['taxon_name'] == homonym_that_refers_to_most_different_species]
    worst_homonym_df.sort_values(by='accepted_name').to_csv(os.path.join(summary_path, 'homonym_that_refers_to_most_different_species.csv'))


if __name__ == '__main__':
    given_wcvp_data = pd.read_csv(os.path.join(taxonomy_inputs_output_path, 'wcvp_data.csv'), index_col=0, dtype={'publication_year': 'Int64'})
    all_homonyms = pd.read_csv(os.path.join(taxonomy_inputs_output_path, 'all_homonyms', 'homonyms.csv'), dtype={'publication_year': 'Int64'})
    ambiguous_homonyms = pd.read_csv(os.path.join(taxonomy_inputs_output_path, 'ambiguous_homonyms', 'homonyms.csv'),
                                     dtype={'publication_year': 'Int64'})
    proportion_of_homonyms_in_wcvp()
    proportion_of_homonyms_which_are_also_accepted()
    get_most_common_names()
