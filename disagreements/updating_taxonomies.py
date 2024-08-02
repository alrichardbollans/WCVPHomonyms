import os

import pandas as pd
from pkg_resources import resource_filename
from wcvpy.wcvp_download import get_all_taxa, add_authors_to_col

_output_path = resource_filename(__name__, 'outputs')

if not os.path.isdir(_output_path):
    os.mkdir(_output_path)


def get_accepted_name_from_record(record: pd.DataFrame, reported_name: str):
    if len(record.index) == 0:
        print(f'{reported_name} has no taxon record')
        raise ValueError
    else:
        accepted_names = record['accepted_name_w_author'].dropna().unique().tolist()

        if len(set(accepted_names)) > 1:
            print(f'{reported_name} resolves to more than one taxon record')
            print(record)
            print(accepted_names)
            raise ValueError
        if len(accepted_names) == 1:
            return accepted_names[0]
        else:
            return None


def compare_two_versions(v12_taxa: pd.DataFrame, v13_taxa: pd.DataFrame, out_dir: str):
    # For all taxa with author strings in old taxon database
    # If the name resolves to a non-nan accepted name in both the old and new database
    # Find the accepted name resolution when the name is resolved first to the old taxonnomy then the new taxonomy
    # If no such name exists, add to cases_that_cant_update
    # else, check if this name is the same as the name when directly resolved using the new database. If not, store in out_dict

    os.makedirs(out_dir, exist_ok=True)

    v12_taxa['taxon_name_w_authors'] = add_authors_to_col(v12_taxa, 'taxon_name')
    v13_taxa['taxon_name_w_authors'] = add_authors_to_col(v13_taxa, 'taxon_name')
    # out_dict = {'reported_name': [], 'v12_accepted_name': [], 'v13_accepted_name': [], 'v12_accepted_name_in_v13': []}
    # cases_that_cant_update = {'reported_name': [], 'v12_accepted_name': [], 'v13_accepted_name': []}
    # cases_that_cant_update_because_of_multiples = {'reported_name': [], 'v12_accepted_name': [], 'v13_accepted_name': []}
    # names_in_old_with_multiple_resolutions = []

    # Pick non-duplicated names
    unique_names = v12_taxa['taxon_name_w_authors'].dropna().unique().tolist()

    # Collect the records in the old and new database directly
    # relevant records
    v12_records = v12_taxa[v12_taxa['taxon_name_w_authors'].isin(unique_names)][
        ['taxon_name_w_authors', 'accepted_name_w_author']]
    v12_records = v12_records.drop_duplicates(keep='first')
    v12_records = v12_records.drop_duplicates(subset=['taxon_name_w_authors'],
                                              keep=False)  # Ignore cases with multiple resolutions, as these are ambiguous anyway
    # accepted names in old database
    relevant_v13_names = v12_records['accepted_name_w_author'].dropna().unique().tolist()
    # names in new database where taxon name is accepted name in old database
    v13_records_for_chaining = v13_taxa[v13_taxa['taxon_name_w_authors'].isin(relevant_v13_names)][
        ['taxon_name_w_authors', 'accepted_name_w_author']]
    v13_records_for_chaining = v13_records_for_chaining.drop_duplicates(keep='first')
    v13_records_for_chaining = v13_records_for_chaining.drop_duplicates(subset=['taxon_name_w_authors'],
                                                                        keep=False)  # Ignore cases with multiple resolutions, as these are ambiguous anyway
    v13_records_for_chaining = v13_records_for_chaining.rename(
        columns={'taxon_name_w_authors': 'v13_taxon_name_w_authors', 'accepted_name_w_author': 'v13_chained_accepted_name_w_author'})
    # chained result where taxon_name_w_authors are resolved to v13_chained_accepted_name_w_author, mediated by old database
    chained_updated_records = pd.merge(v12_records, v13_records_for_chaining, left_on='accepted_name_w_author',
                                       right_on='v13_taxon_name_w_authors')

    # relevant names in new database where taxon name is taxon name in old database
    v13_updated_records = v13_taxa[v13_taxa['taxon_name_w_authors'].isin(unique_names)][['taxon_name_w_authors', 'accepted_name_w_author']]
    v13_updated_records = v13_updated_records.drop_duplicates(keep='first')
    v13_updated_records = v13_updated_records.drop_duplicates(subset=['taxon_name_w_authors'],
                                                              keep=False)  # Ignore cases with multiple resolutions, as these are ambiguous anyway
    v13_updated_records = v13_updated_records.rename(
        columns={'accepted_name_w_author': 'v13_direct_accepted_name_w_author'})

    # direct result where taxon_name_w_authors are resolved directly to the new databse
    merged_df = pd.merge(chained_updated_records, v13_updated_records, on='taxon_name_w_authors')

    results_df = merged_df[merged_df['v13_direct_accepted_name_w_author'] != merged_df['v13_chained_accepted_name_w_author']]
    results_df = results_df.dropna(subset=['v13_direct_accepted_name_w_author'])
    # TODO: add rank info
    # Cases like Cubeba Raf. and Lamottea Pomel are only here because of the multiple resolutions -- which is interesting in itself

    # for reported_name in tqdm(unique_names):
    #
    #     v12_record = v12_records[v12_records['taxon_name_w_authors'] == reported_name]
    #     try:
    #         v12_accepted_name_w_author = get_accepted_name_from_record(v12_record, reported_name)
    #         if v12_accepted_name_w_author is not None:  # If there is a resolution to an accepted name
    #             v13_record = v13_records[v13_records['taxon_name_w_authors'] == reported_name]
    #             if len(v13_record.index) > 0:  # Only consider cases where the reported name is in both taxonomies
    #                 v13_accepted_name_w_author = get_accepted_name_from_record(v13_record, reported_name)
    #
    #                 v12_accepted_name_updated_record = v13_records[v13_records['taxon_name_w_authors'] == v12_accepted_name_w_author]
    #                 if len(v12_accepted_name_updated_record.index) == 0:
    #                     cases_that_cant_update['reported_name'].append(reported_name)
    #                     cases_that_cant_update['v12_accepted_name'].append(v12_accepted_name_w_author)
    #                     cases_that_cant_update['v13_accepted_name'].append(v13_accepted_name_w_author)
    #
    #                 else:
    #                     # Name Diplazium lonchophyllum Kunze resolves to two different taxa!
    #                     try:
    #                         v12_updated_accepted_name = get_accepted_name_from_record(v12_accepted_name_updated_record, reported_name)
    #                         if v12_updated_accepted_name != v13_accepted_name_w_author:
    #                             print('Found one!')
    #                             out_dict['reported_name'].append(reported_name)
    #                             out_dict['v12_accepted_name'].append(v12_accepted_name_w_author)
    #                             out_dict['v13_accepted_name'].append(v13_accepted_name_w_author)
    #                             out_dict['v12_accepted_name_in_v13'].append(v12_updated_accepted_name)
    #                             print(out_dict)
    #                     except ValueError:
    #                         cases_that_cant_update_because_of_multiples['reported_name'].append(reported_name)
    #                         cases_that_cant_update_because_of_multiples['v12_accepted_name'].append(v12_accepted_name_w_author)
    #                         cases_that_cant_update_because_of_multiples['v13_accepted_name'].append(v13_accepted_name_w_author)
    #     except:
    #         names_in_old_with_multiple_resolutions.append(reported_name)

    # print(out_dict)
    # out_df = pd.DataFrame.from_dict(out_dict)
    # cases_that_cant_update_df = pd.DataFrame.from_dict(cases_that_cant_update)
    # names_in_old_with_multiple_resolutions_df = pd.DataFrame.from_dict(
    #     {'names_in_old_with_multiple_resolutions': names_in_old_with_multiple_resolutions})

    results_df.to_csv(os.path.join(out_dir, 'results.csv'))
    # cases_that_cant_update_df.to_csv(os.path.join(out_dir, 'v12_v13_cases_cant_update.csv'))
    # names_in_old_with_multiple_resolutions_df.to_csv(os.path.join(out_dir, 'v12_v13_names_in_old_with_multiple_resolutions.csv'))

    return results_df  # , cases_that_cant_update_df, names_in_old_with_multiple_resolutions_df


def main():
    v12_taxa = get_all_taxa(version='12')
    v13_taxa = get_all_taxa(version=None)
    compare_two_versions(v12_taxa, v13_taxa,
                         os.path.join(_output_path,
                                      'v12_v13'))
    v10_taxa = get_all_taxa(version='10')
    compare_two_versions(v10_taxa, v13_taxa,
                         os.path.join(_output_path,
                                      'v10_v13'))
    v11_taxa = get_all_taxa(version='11')
    compare_two_versions(v11_taxa, v13_taxa,
                         os.path.join(_output_path,
                                      'v11_v13'))


if __name__ == '__main__':
    main()
