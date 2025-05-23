import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.api as sm
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from wcvpy.wcvp_download import plot_native_number_accepted_taxa_in_regions, wcvp_accepted_columns

from taxonomy_inputs import taxonomy_inputs_output_path, WCVP_VERSION

ambiguous_homonyms = pd.read_csv(os.path.join(taxonomy_inputs_output_path, 'ambiguous_homonyms', 'homonyms.csv'),
                                 dtype={'publication_year': 'Int64'})
wcvp_given_data = pd.read_csv(
    os.path.join(taxonomy_inputs_output_path, 'wcvp_data.csv'))


def plot_distributions():
    # the global distributions of the accepted species that are resolved to by ambiguous binomial homonyms
    plot_native_number_accepted_taxa_in_regions(ambiguous_homonyms, wcvp_accepted_columns['species'], os.path.join('outputs'),
                                                'ambiguous_homonyms_dists.jpg', include_extinct=True, wcvp_version=WCVP_VERSION)
    # global distribution of underlying population
    plot_native_number_accepted_taxa_in_regions(wcvp_given_data, wcvp_accepted_columns['species'], os.path.join('outputs'),
                                                'underlying_species_distributions.jpg', include_extinct=True, wcvp_version=WCVP_VERSION)


def get_analysis_data():
    x_var = 'All Accepted Species'
    y_var = 'Accepted Species with Ambiguity'
    ambiguous_homonyms_region_counts = pd.read_csv(os.path.join('outputs', 'ambiguous_homonyms_dists.jpg_regions.csv'), index_col=0)
    ambiguous_homonyms_region_counts = ambiguous_homonyms_region_counts.rename(columns={'Number of Taxa': 'Accepted Species with Ambiguity'})
    underlying_species_region_counts = pd.read_csv(os.path.join('outputs', 'underlying_species_distributions.jpg_regions.csv'), index_col=0)
    underlying_species_region_counts = underlying_species_region_counts.rename(columns={'Number of Taxa': 'All Accepted Species'})

    analysis_df = pd.merge(ambiguous_homonyms_region_counts, underlying_species_region_counts, on='Region')
    # analysis_df = analysis_df.sort_values(by=x_var) # LOESS is affected by order..
    return analysis_df, x_var, y_var


def find_regression_model():
    analysis_df, x_var, y_var = get_analysis_data()
    # Step 1: Fit a linear regression model
    X = analysis_df[[x_var]].values  # Independent variable (species richness)
    X_to_plot = analysis_df[x_var].values  # Independent variable (species richness)
    # scaled_data[metric] = np.log(scaled_data[metric])
    y = analysis_df[y_var].values  # Dependent variable (diversity)

    model = LinearRegression()
    model.fit(X, y)

    r_squared = model.score(X, y)
    best_model_r_sqaured = 0
    data = [['Linear', r_squared]]
    sns.scatterplot(x=X_to_plot, y=y, edgecolor="black", alpha=0.8)
    expected_diversity = model.predict(X)
    if r_squared > best_model_r_sqaured:
        best_model_prediction = expected_diversity
        best_model_r_sqaured = r_squared
    sns.lineplot(x=X_to_plot, y=expected_diversity, color='black', linestyle='--')
    plt.savefig(os.path.join('outputs', 'regressions', 'linear_regression.jpg'), dpi=300)
    plt.close()

    # Fit LOESS with outlier robustness (iterations downweight outliers)
    loess_prediction = sm.nonparametric.lowess(exog=X_to_plot, endog=y,return_sorted=False)
    expected_diversity = loess_prediction
    residuals = y - expected_diversity
    # Calculate R² (coefficient of determination)
    ss_res = np.sum(residuals ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r_squared = 1 - (ss_res / ss_tot)
    print(f"R² (Coefficient of Determination): {r_squared:.3f}")
    if r_squared > best_model_r_sqaured:
        best_model_prediction = expected_diversity
        best_model_r_sqaured = r_squared
    sns.scatterplot(x=X_to_plot, y=y, edgecolor="black", alpha=0.8)
    sns.lineplot(x=X_to_plot, y=expected_diversity, color='black', linestyle='--')
    plt.savefig(os.path.join('outputs', 'regressions', 'LOESS.jpg'), dpi=300)
    plt.close()
    data.append([f'LOESS', r_squared])

    for deg in range(2, 8):
        poly = PolynomialFeatures(degree=deg)
        X_poly = poly.fit_transform(X)

        poly.fit(X_poly, y)
        lin2 = LinearRegression()
        lin2.fit(X_poly, y)
        r_squared = lin2.score(X_poly, y)

        data.append([f'Polynomial {deg}', r_squared])

        sns.scatterplot(x=X_to_plot, y=y, edgecolor="black", alpha=0.8)
        expected_diversity = lin2.predict(X_poly)
        if r_squared > best_model_r_sqaured:
            best_model_prediction = expected_diversity
            best_model_r_sqaured = r_squared
        sns.lineplot(x=X_to_plot, y=expected_diversity, color='black', linestyle='--')
        plt.savefig(os.path.join('outputs', 'regressions', f'poly_{deg}_regression.jpg'), dpi=300)
        plt.close()

    df = pd.DataFrame(data, columns=['Model', 'R-squared'])
    df.to_csv(os.path.join('outputs', 'regressions', 'model_comparison.csv'))
    return best_model_prediction, loess_prediction


def analyse_region_count_data():
    analysis_df, x_var, y_var = get_analysis_data()
    sns.set_theme()
    sns.scatterplot(data=analysis_df, x=x_var, y=y_var)
    plt.savefig(os.path.join('outputs', 'region_count_scatter.jpg'), dpi=300)
    plt.close()

    outpath = os.path.join('outputs', 'regressions')
    Path(outpath).mkdir(parents=True, exist_ok=True)
    analysis_df = analysis_df.dropna(subset=[x_var, y_var])

    # Use loess as its robust to outliers
    best_model_prediction, loess_prediction = find_regression_model()

    # Step 2: Predict the expected diversity based on species richness
    analysis_df['expected_diversity'] = loess_prediction

    # Step 3: Calculate the residuals (observed - expected)
    analysis_df[f'{y_var}_residuals'] = analysis_df[y_var] - analysis_df['expected_diversity']

    # Step 4: Highlight cases with large residuals
    # Let's consider residuals greater than 2 standard deviations as "large differences"

    std_residual = analysis_df[f'{y_var}_residuals'].std()
    mean_residual = analysis_df[f'{y_var}_residuals'].mean()
    analysis_df['highlight_high'] = analysis_df[f'{y_var}_residuals'] > ((2 * std_residual) + mean_residual)
    analysis_df['highlight_low'] = analysis_df[f'{y_var}_residuals'] < (mean_residual - (2 * std_residual))

    # Print the cases with large differences
    # print("Cases with large differences (residuals):")
    # print(working_data[working_data['highlight']])

    analysis_df.to_csv(os.path.join(outpath, f'analysis_df.csv'))

    plot_annotated_regression_data(analysis_df, outpath, x_var, y_var)


    plot_dist_of_metric(analysis_df, f'{y_var}_residuals', out_path=os.path.join(outpath, f'residuals_distributions.jpg'))


def plot_annotated_regression_data(data, outpath, x_var, y_var):
    # Set up the plot
    import seaborn as sns
    from pypalettes import load_cmap
    # plt.figure(figsize=(10, 6))
    # sns.set_style("whitegrid")
    # Scatter plot for APWD vs phylogenetic_diversity
    # colors = load_cmap('inferno').hex
    # print(colors)
    data['color'] = np.where((data['highlight_high'] == True), '#d12020', 'grey')
    data['color'] = np.where((data['highlight_low'] == True), '#5920ff', data['color'])

    sns.scatterplot(x=x_var, y=y_var, data=data, color=data['color'], edgecolor="black", alpha=0.8)

    # Highlight points where 'highlight' is True

    highlighted_data = data[(data['highlight_high'] == True) | (data['highlight_low'] == True)]

    for _, row in highlighted_data.iterrows():
        #     if row['highlight_high']:  # in ['COR', 'KZN', 'ALD', 'AZO', 'ROD', 'SEY', 'LDV']:
        #         upshift = 0
        #         left_shift = 0.05
        #         if row['Group'] in ['ALD', 'SEY']:
        #             upshift = 0.09
        #         if row['Group'] in ['AZO']:
        #             upshift = -0.2
        #         if row['Group'] in ['SEY']:
        #             left_shift = 0
        #
        #         if row['Group'] in ['COR']:
        #             left_shift = -0.05
        #             upshift = 0.11
        #     if row['highlight_low']:
        #         upshift = 0
        #         left_shift = -0.45
        #         if row['Group'] in ['CLS']:
        #             left_shift = -0.38
        #         if row['Group'] in ['CLS', 'MSO']:
        #             upshift = -0.2
        #         if row['Group'] in ['AGS']:
        #             upshift = -0.13
        #         if row['Group'] in ['NZN']:
        #             upshift = 0.04
        #             left_shift = -0.50
        plt.annotate(row['Region'], (row[x_var], row[y_var]), ha='right', color='black')

    # Line plot for expected_diversity vs phylogenetic_diversity

    sns.lineplot(x=x_var, y='expected_diversity', color='black', linestyle='--', data=data)

    # Labels and legend

    plt.xlabel(x_var)

    plt.ylabel(y_var)

    plt.title('')

    # plt.legend(loc='upper right')

    plt.savefig(os.path.join(outpath, f'outliers.jpg'), dpi=300)
    plt.close()
    sns.reset_orig()


def plot_dist_of_metric(df_with_region_data, metric, colormap: str = 'inferno', out_path: str = None):
    import matplotlib.pyplot as plt
    import matplotlib as mpl
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    import cartopy.io.shapereader as shpreader

    tdwg3_shp = shpreader.Reader(
        os.path.join('inputs', 'wgsrpd-master', 'level3', 'level3.shp'))
    tdwg3_region_codes = df_with_region_data['Region'].values

    ## Colour maps range is 0 - 1, so the values are standardised for this
    max_val = df_with_region_data[metric].max()
    min_val = df_with_region_data[metric].min()
    norm = plt.Normalize(min_val, max_val)
    print('plotting countries')

    plt.figure(figsize=(15, 9.375))
    ax = plt.axes(projection=ccrs.Mollweide())
    ax.coastlines(resolution='10m')
    ax.add_feature(cfeature.BORDERS, linewidth=2)

    cmap = mpl.colormaps[colormap]
    for country in tdwg3_shp.records():

        tdwg_code = country.attributes['LEVEL3_COD']
        if tdwg_code in tdwg3_region_codes:
            ax.add_geometries([country.geometry], ccrs.PlateCarree(),
                              facecolor=cmap(
                                  norm(df_with_region_data.loc[df_with_region_data['Region'] == tdwg_code, metric].iloc[
                                           0])),
                              label=tdwg_code)

        else:
            ax.add_geometries([country.geometry], ccrs.PlateCarree(),
                              facecolor='white',
                              label=tdwg_code)

    all_map_isos = [country.attributes['LEVEL3_COD'] for country in tdwg3_shp.records()]
    missed_names = [x for x in tdwg3_region_codes if x not in all_map_isos]
    print(f'iso codes not plotted on map: {missed_names}')
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm._A = []
    plt.tight_layout()
    fig = plt.gcf()
    fig.subplots_adjust(right=0.8)
    cbar_ax = fig.add_axes([0.85, 0.175, 0.02, 0.65])
    cbar1 = fig.colorbar(sm, cax=cbar_ax)
    cbar1.ax.tick_params(labelsize=30)


    Path(os.path.dirname(out_path)).mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=400, bbox_inches='tight')
    plt.close()
    plt.cla()
    plt.clf()

if __name__ == '__main__':
    # plot_distributions()
    analyse_region_count_data()
