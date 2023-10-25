import os

import pandas as pd
from wcvp_download import get_all_taxa, wcvp_columns, wcvp_accepted_columns, clean_whitespaces_in_names

_output_path = os.path.join('outputs')

RANKS_TO_CONSIDER = ['Species']
wcvp_given_data = get_all_taxa(ranks=RANKS_TO_CONSIDER)


def summarise_homonym_df(df: pd.DataFrame, outpath: str):
    duplicates = df.drop(
        columns=['nomenclatural_remarks', 'geographic_area', 'lifeform_description', 'climate_description',
                 'accepted_parent',
                 'accepted_parent_w_author', 'accepted_parent_id', 'accepted_parent_ipni_id',
                 'accepted_parent_rank'
                 ])
    duplicates = duplicates.sort_values(by=wcvp_columns['name'])

    add_authors_to_names(duplicates)

    duplicates.to_csv(os.path.join(outpath, 'homonyms.csv'))
    duplicates.describe(include='all').to_csv(os.path.join(outpath, 'homonyms_summary.csv'))

    non_accepted_homonyms = duplicates[duplicates[wcvp_columns['status']] != 'Accepted']
    non_accepted_homonyms.to_csv(os.path.join(outpath, 'non_accepted_homonyms.csv'))
    non_accepted_homonyms.describe(include='all').to_csv(
        os.path.join(outpath, 'non_accepted_homonyms_summary.csv'))

    accepted_homonyms = duplicates[duplicates[wcvp_columns['status']] == 'Accepted']
    accepted_homonyms.to_csv(os.path.join(outpath, 'accepted_with_homonyms.csv'))
    accepted_homonyms.describe(include='all').to_csv(
        os.path.join(outpath, 'accepted_with_homonyms_summary.csv'))


def get_homonym_files():
    # Gets all homonymns
    outpath = os.path.join(_output_path, 'all_homonyms')
    homonyms = wcvp_given_data[wcvp_given_data[wcvp_columns['name']].duplicated(keep=False)]

    summarise_homonym_df(homonyms, outpath)


def get_problem_homonym_files():
    # Gets homonymns that can resolve to different names
    outpath = os.path.join(_output_path, 'problem_homonyms')
    # groupby name and return a boolean of whether each has more than 1 unique accepted name
    multinames = wcvp_given_data.groupby([wcvp_columns['name']])[wcvp_accepted_columns['name']].nunique().gt(
        1)
    # use loc to only see those values that have `True` in `multi_country`:
    duplicates = wcvp_given_data.loc[wcvp_given_data[wcvp_columns['name']].isin(multinames[multinames].index)]
    summarise_homonym_df(duplicates, outpath)


def add_authors_to_names(df: pd.DataFrame):
    df['taxon_names_with_authors'] = df[wcvp_columns['name']].str.cat(
        df[wcvp_columns['authors']].fillna(''),
        sep=' ').apply(clean_whitespaces_in_names)

    column_series = [df[c].fillna('') for c in
                     [wcvp_columns['paranthet_author'], wcvp_columns['primary_author']]]
    df['taxon_names_with_paranthet_authors'] = df[wcvp_columns['name']].str.cat(column_series,
                                                                                sep=' ').apply(
        clean_whitespaces_in_names)

    df['taxon_names_with_primary_author'] = df[wcvp_columns['name']].str.cat(
        df[wcvp_columns['primary_author']].fillna(''),
        sep=' ').apply(clean_whitespaces_in_names)


def main():
    get_homonym_files()
    get_problem_homonym_files()

if __name__ == '__main__':
    main()
