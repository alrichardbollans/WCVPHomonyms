import os

import numpy as np
import pandas as pd
from wcvp_download import get_all_taxa, wcvp_columns, wcvp_accepted_columns, clean_whitespaces_in_names
from datetime import datetime

scratch_path = os.environ.get('SCRATCH')
project_path = os.path.join(scratch_path, 'WCVPHomonyms')
taxonomy_inputs_output_path = os.path.join(project_path, 'taxonomy_inputs', 'outputs')

RANKS_TO_CONSIDER = ['Species']


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
    outpath = os.path.join(taxonomy_inputs_output_path, 'all_homonyms')
    homonyms = wcvp_given_data[wcvp_given_data[wcvp_columns['name']].duplicated(keep=False)]

    summarise_homonym_df(homonyms, outpath)


def get_ambiguous_homonym_files():
    # Gets homonymns that can resolve to different *species*
    outpath = os.path.join(taxonomy_inputs_output_path, 'ambiguous_homonyms')
    # groupby name and return a boolean of whether each has more than 1 unique accepted name
    multinames = wcvp_given_data.groupby([wcvp_columns['name']])[wcvp_accepted_columns['species']].nunique(dropna=True).gt(
        1)
    # use loc to only see those values that have `True` in `accepted_name`:
    duplicates = wcvp_given_data.loc[wcvp_given_data[wcvp_columns['name']].isin(multinames[multinames].index)]
    summarise_homonym_df(duplicates, outpath)


def add_authors_to_given_col(df: pd.DataFrame, col, name_tag: str):
    df[name_tag + '_with_authors'] = df[col].str.cat(
        df[wcvp_columns['authors']].fillna(''),
        sep=' ').apply(clean_whitespaces_in_names)

    column_series = [df[c].fillna('') for c in
                     [wcvp_columns['paranthet_author'], wcvp_columns['primary_author']]]
    df[name_tag + '_with_paranthet_authors'] = df[col].str.cat(column_series,
                                                               sep=' ').apply(
        clean_whitespaces_in_names)

    df[name_tag + '_with_primary_author'] = df[col].str.cat(
        df[wcvp_columns['primary_author']].fillna(''),
        sep=' ').apply(clean_whitespaces_in_names)


def add_authors_to_names(df: pd.DataFrame):
    add_authors_to_given_col(df, wcvp_columns['name'], 'taxon_names')

    df['abbreviated_genus'] = df[wcvp_columns['genus']].apply(lambda x: x[0] + '.')
    df['sp_binomial_with_abbreviated_genus'] = df['abbreviated_genus'].str.cat(
        df['species'].fillna(''),
        sep=' ').apply(clean_whitespaces_in_names)

    add_authors_to_given_col(df, 'sp_binomial_with_abbreviated_genus', 'sp_binomial_with_abbreviated_genus')


def parse_publication_year(given_string: str):
    if given_string == '(1981 publ. 1082)':  # An exception that returns a valid date
        return '1982'
    elif given_string in ['(19166)',
                          '(19543)',
                          '(19553)',
                          '(19667)',
                          '(19983)',
                          ]:  # Some obivous errors that return valid dates
        return np.nan

    try:
        out = given_string[-5:-1]
    except TypeError:
        out = given_string
    finally:
        return test_year_parsing(out)


def test_year_parsing(given_str):
    format = "%Y"
    if given_str == '' or given_str is None or given_str != given_str:
        return np.nan
    else:
        try:
            datetime.strptime(given_str, format)
            return given_str
        except ValueError:
            return np.nan


def main():
    get_homonym_files()
    get_ambiguous_homonym_files()


if __name__ == '__main__':
    wcvp_given_data = get_all_taxa(ranks=RANKS_TO_CONSIDER)
    wcvp_given_data = wcvp_given_data[(wcvp_given_data[wcvp_columns['rank']].isin(RANKS_TO_CONSIDER))]  # restrict to just homonyms being species
    wcvp_given_data = wcvp_given_data.dropna(subset=[wcvp_accepted_columns['species']])
    wcvp_given_data['publication_year'] = wcvp_given_data['first_published'].apply(parse_publication_year)
    wcvp_given_data[['plant_name_id', 'taxon_name', 'parenthetical_author', 'primary_author', 'taxon_rank',
                     'publication_author', 'first_published', 'publication_year', 'family']].to_csv(
        os.path.join(taxonomy_inputs_output_path, 'wcvp_data.csv'))
    wcvp_given_data.describe(include='all').to_csv(os.path.join(taxonomy_inputs_output_path, 'wcvp_data_summary.csv'))
    main()
