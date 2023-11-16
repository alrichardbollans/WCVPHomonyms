import os

import pandas as pd
from matplotlib import pyplot as plt

from taxonomy_inputs import taxonomy_inputs_output_path


def main():
    import seaborn as sns
    given_wcvp_data = pd.read_csv(os.path.join(taxonomy_inputs_output_path, 'wcvp_data.csv'), index_col=0, dtype={'publication_year': 'Int64'})
    all_homonyms = pd.read_csv(os.path.join(taxonomy_inputs_output_path, 'all_homonyms', 'homonyms.csv'), dtype={'publication_year': 'Int64'})
    ambiguous_homonyms = pd.read_csv(os.path.join(taxonomy_inputs_output_path, 'ambiguous_homonyms', 'homonyms.csv'),
                                     dtype={'publication_year': 'Int64'})

    given_wcvp_data = given_wcvp_data.dropna(subset=['publication_year'])
    all_homonyms = all_homonyms.dropna(subset=['publication_year'])
    ambiguous_homonyms = ambiguous_homonyms.dropna(subset=['publication_year'])

    plt.figure(figsize=(40, 10))
    sns.countplot(x='publication_year', data=given_wcvp_data, )
    plt.xticks(rotation=90)
    plt.title('WCVP Species Publications')
    plt.tight_layout()
    plt.savefig(os.path.join('outputs', 'plots', 'WCVP Species Publications.png'), dpi=600)

    plt.figure(figsize=(40, 10))
    sns.countplot(x='publication_year', data=all_homonyms, )
    plt.xticks(rotation=90)
    plt.title('WCVP Homonymous Species Publications')
    plt.tight_layout()
    plt.savefig(os.path.join('outputs', 'plots', 'WCVP Homonymous Species Publications.png'), dpi=600)

    plt.figure(figsize=(40, 10))
    sns.countplot(x='publication_year', data=ambiguous_homonyms, )
    plt.xticks(rotation=90)
    plt.title('WCVP Ambiguous Homonymous Species Publications')
    plt.tight_layout()
    plt.savefig(os.path.join('outputs', 'plots', 'WCVP Ambiguous Homonymous Species Publications.png'), dpi=600)


if __name__ == '__main__':
    main()
