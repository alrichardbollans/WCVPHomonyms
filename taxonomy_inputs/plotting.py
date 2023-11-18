import os

import pandas as pd
from matplotlib import pyplot as plt

from taxonomy_inputs import taxonomy_inputs_output_path


def generic_category_plot(var: str, title: str, figsize=(40, 10), sort_var=False):
    import seaborn as sns
    given_wcvp_data = pd.read_csv(os.path.join(taxonomy_inputs_output_path, 'wcvp_data.csv'), index_col=0, dtype={'publication_year': 'Int64'})
    all_homonyms = pd.read_csv(os.path.join(taxonomy_inputs_output_path, 'all_homonyms', 'homonyms.csv'), dtype={'publication_year': 'Int64'})
    ambiguous_homonyms = pd.read_csv(os.path.join(taxonomy_inputs_output_path, 'ambiguous_homonyms', 'homonyms.csv'),
                                     dtype={'publication_year': 'Int64'})

    given_wcvp_data = given_wcvp_data.dropna(subset=[var])
    all_homonyms = all_homonyms.dropna(subset=[var])
    ambiguous_homonyms = ambiguous_homonyms.dropna(subset=[var])

    given_wcvp_data['Legend'] = 'Non Homonymous Species Names'
    all_homonyms['Legend'] = 'Non-ambiguous Homonymous Species Names'
    ambiguous_homonyms['Legend'] = 'Ambiguous Homonymous Species Names'

    all_data = pd.concat([given_wcvp_data, all_homonyms, ambiguous_homonyms])
    all_data = all_data.drop_duplicates(subset=['plant_name_id'], keep='last')  # Remove duplicates and keep most specific

    if sort_var:
        # Calculate proportions of each value in the 'Legend' column
        var_legend_proportions = all_data.groupby(var)['Legend'].apply(lambda x: (x == 'Ambiguous Homonymous Species Names').mean()).reset_index()
        var_legend_proportions.columns = [var, 'Proportion_Ambiguous']

        # Sort the var column based on the proportions in descending order
        proportion_sorted_vars = var_legend_proportions.sort_values('Proportion_Ambiguous', ascending=False)[var].tolist()

        # Reorder the DataFrame based on the sorted var column
        all_data[var] = pd.Categorical(all_data[var], categories=proportion_sorted_vars, ordered=True)
        all_data = all_data.sort_values(var)

        # Calculate proportions of each value in the 'Legend' column
        var_legend_counts = all_data[all_data['Legend'] == 'Ambiguous Homonymous Species Names'].groupby(var).size().reset_index(name='Count_Ambiguous')

        # Sort the var column based on the proportions in descending order
        count_sorted_vars = var_legend_counts.sort_values('Count_Ambiguous', ascending=False)[var].tolist()

    else:
        count_sorted_vars =None

    plt.figure(figsize=figsize)
    sns.countplot(x=var, data=all_data, hue='Legend', order=count_sorted_vars)
    plt.xticks(rotation=90)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(os.path.join('outputs', 'plots', title + '.jpg'), dpi=300)



    plt.figure(figsize=figsize)
    sns.histplot(data=all_data, x=var, hue='Legend', multiple="fill",
                 stat='proportion', shrink=0.9, discrete=True)

    plt.xticks(rotation=90)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(os.path.join('outputs', 'plots', title + '_normalized.jpg'), dpi=300)


def year_plots():
    generic_category_plot('publication_year', 'WCVP Species Publications and Homonym Occurrence')
    import seaborn as sns
    given_wcvp_data = pd.read_csv(os.path.join(taxonomy_inputs_output_path, 'wcvp_data.csv'), index_col=0, dtype={'publication_year': 'Int64'})
    all_homonyms = pd.read_csv(os.path.join(taxonomy_inputs_output_path, 'all_homonyms', 'homonyms.csv'), dtype={'publication_year': 'Int64'})
    ambiguous_homonyms = pd.read_csv(os.path.join(taxonomy_inputs_output_path, 'ambiguous_homonyms', 'homonyms.csv'),
                                     dtype={'publication_year': 'Int64'})

    given_wcvp_data = given_wcvp_data.dropna(subset=['publication_year'])
    all_homonyms = all_homonyms.dropna(subset=['publication_year'])
    ambiguous_homonyms = ambiguous_homonyms.dropna(subset=['publication_year'])

    given_wcvp_data['Legend'] = 'Non Homonymous Species Names'
    all_homonyms['Legend'] = 'Non-ambiguous Homonymous Species Names'
    ambiguous_homonyms['Legend'] = 'Ambiguous Homonymous Species Names'

    plt.figure(figsize=(40, 10))
    sns.countplot(x='publication_year', data=given_wcvp_data, )
    plt.xticks(rotation=90)
    plt.title('WCVP Species Publications')
    plt.tight_layout()
    plt.savefig(os.path.join('outputs', 'plots', 'WCVP Species Publications.jpg'), dpi=300)

    plt.figure(figsize=(40, 10))
    sns.countplot(x='publication_year', data=all_homonyms, )
    plt.xticks(rotation=90)
    plt.title('WCVP Homonymous Species Publications')
    plt.tight_layout()
    plt.savefig(os.path.join('outputs', 'plots', 'WCVP Homonymous Species Publications.jpg'), dpi=300)

    plt.figure(figsize=(40, 10))
    sns.countplot(x='publication_year', data=ambiguous_homonyms, )
    plt.xticks(rotation=90)
    plt.title('WCVP Ambiguous Homonymous Species Publications')
    plt.tight_layout()
    plt.savefig(os.path.join('outputs', 'plots', 'WCVP Ambiguous Homonymous Species Publications.jpg'), dpi=300)


def family_plots():
    # TODO: maybe change to accepted family?
    generic_category_plot('family', 'WCVP Species Homonyms in Families', figsize=(60, 10), sort_var=True)


if __name__ == '__main__':
    year_plots()
    family_plots()
