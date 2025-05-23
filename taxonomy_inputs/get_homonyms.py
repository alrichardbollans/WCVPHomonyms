import os

import numpy as np
import pandas as pd
from wcvpy.wcvp_download import get_all_taxa, wcvp_columns, wcvp_accepted_columns, clean_whitespaces_in_names
from datetime import datetime

scratch_path = os.environ.get('KEWSCRATCHPATH')
project_path = os.path.join(scratch_path, 'WCVPHomonyms')
taxonomy_inputs_output_path = os.path.join(project_path, 'taxonomy_inputs', 'outputs')

RANKS_TO_CONSIDER = ['Species']
WCVP_VERSION = None


def summarise_homonym_df(df: pd.DataFrame, outpath: str):
    duplicates = df.drop(
        columns=['nomenclatural_remarks', 'geographic_area', 'lifeform_description', 'climate_description',
                 'accepted_parent',
                 'accepted_parent_w_author', 'accepted_parent_id', 'accepted_parent_ipni_id',
                 'accepted_parent_rank'
                 ])
    duplicates = duplicates.sort_values(by=wcvp_columns['name'])

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
    """
    Identifies and processes homonyms from the provided dataset, then stores the
    results in a specified output file.

    Homonyms are records that share the same name but might differ in other data
    fields. This function filters the dataset for such records, processes them,
    and writes a summary to an output file.

    :return: None
    """
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


def add_authors_to_given_col(df: pd.DataFrame, col):
    df[col + '_with_authors'] = df[col].str.cat(
        df[wcvp_columns['authors']].fillna(''),
        sep=' ').apply(clean_whitespaces_in_names)

    column_series = [df[c].fillna('') for c in
                     [wcvp_columns['paranthet_author'], wcvp_columns['primary_author']]]
    df[col + '_with_paranthet_authors'] = df[col].str.cat(column_series,
                                                          sep=' ').apply(
        clean_whitespaces_in_names)

    df[col + '_with_primary_author'] = df[col].str.cat(
        df[wcvp_columns['primary_author']].fillna(''),
        sep=' ').apply(clean_whitespaces_in_names)


def add_authors_to_names(df: pd.DataFrame):
    add_authors_to_given_col(df, wcvp_columns['name'])

    df['abbreviated_genus'] = df[wcvp_columns['genus']].apply(lambda x: x[0] + '.')
    df['sp_binomial_with_abbreviated_genus'] = df['abbreviated_genus'].str.cat(
        df['species'].fillna(''),
        sep=' ').apply(clean_whitespaces_in_names)

    add_authors_to_given_col(df, 'sp_binomial_with_abbreviated_genus')


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


def assess_duplicates(df):
    ## There shouldn't be any duplicated names inc. authors so just check here
    duplicate_issues = df[df['taxon_name_with_authors'].duplicated(keep=False)]
    if len(duplicate_issues) > 0:
        if len(duplicate_issues) > 1524:
            raise ValueError
        else:
            print(f'There are {len(duplicate_issues)} duplicate names with authors. These will be saved to file and removed.')
            duplicate_issues.sort_values(by='taxon_name_with_authors').to_csv(
                os.path.join(taxonomy_inputs_output_path, 'duplicate_names_with_authors.csv'))
            multinames = duplicate_issues.groupby(['taxon_name_with_authors'])[wcvp_accepted_columns['name']].nunique(dropna=True).gt(
                1)
            # use loc to only see those values that have `True` in `accepted_name`:
            duplicates_with_different_accepted_names = duplicate_issues.loc[
                duplicate_issues['taxon_name_with_authors'].isin(multinames[multinames].index)]
            if len(duplicates_with_different_accepted_names) > 0:
                print(f'There are {len(duplicates_with_different_accepted_names)} duplicate names with authors which resolve to different names.')

                duplicates_with_different_accepted_names.sort_values(by='taxon_name_with_authors').to_csv(
                    os.path.join(taxonomy_inputs_output_path, 'duplicates_with_different_accepted_names.csv'))


def main():
    get_homonym_files()
    get_ambiguous_homonym_files()


if __name__ == '__main__':
    wcvp_given_data = get_all_taxa(ranks=RANKS_TO_CONSIDER, version=WCVP_VERSION)
    wcvp_given_data = wcvp_given_data[
        ~wcvp_given_data[wcvp_columns['status']].isin(['Artificial Hybrid', 'Unplaced', 'Invalid', 'Misapplied', 'Orthographic'])]
    wcvp_given_data = wcvp_given_data[(wcvp_given_data[wcvp_columns['rank']].isin(RANKS_TO_CONSIDER))]  # restrict to just homonyms being species
    wcvp_given_data = wcvp_given_data.dropna(subset=[wcvp_accepted_columns['species']])
    add_authors_to_names(wcvp_given_data)
    assess_duplicates(wcvp_given_data)
    wcvp_given_data = wcvp_given_data.drop_duplicates(subset=['taxon_name_with_authors'], keep='first')

    wcvp_given_data['publication_year'] = wcvp_given_data['first_published'].apply(parse_publication_year)
    wcvp_given_data[['plant_name_id', 'taxon_name', 'parenthetical_author', 'primary_author', 'taxon_rank',
                     'publication_author', 'first_published', 'publication_year',wcvp_accepted_columns['species'], wcvp_accepted_columns['family'], wcvp_columns['status']]].to_csv(
        os.path.join(taxonomy_inputs_output_path, 'wcvp_data.csv'))
    wcvp_given_data.describe(include='all').to_csv(os.path.join(taxonomy_inputs_output_path, 'summaries', 'wcvp_data_summary.csv'))
    main()
