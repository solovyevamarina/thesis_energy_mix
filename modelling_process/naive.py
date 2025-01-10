import pandas as pd
import numpy as np
import math


def naive_forecast(country_data, start_time, end_time):

    # Ensure that the 'YM' column exists (Year-Month) for easy selection
    country_data['YM'] = country_data['Date'].dt.to_period('M').astype(str)

    # Create an empty column for the Naive forecast
    country_data['Naive'] = np.nan

    # Create a dynamic list of years from start_time to end_time
    start_year = int(start_time[:4])
    end_year = int(end_time[:4])
    ym_list = country_data['YM'].unique()

    # Loop for generating Naive forecast based on previous year's mean
    for rep in range(12, len(ym_list)):  # Skip the first 12 months
        country_data.loc[country_data['YM'] == ym_list[rep], 'Naive'] = round(
            country_data.loc[country_data['YM'] == ym_list[rep - 12], 'Price'].mean(), 2
        )

    for rep in range(0, 12):  # For first 12 months, use the mean of the same month in the same year
        country_data.loc[country_data['YM'] == ym_list[rep], 'Naive'] = round(
            country_data.loc[country_data['YM'] == ym_list[rep], 'Price'].mean(), 2
        )

    # Creating a DataFrame to track errors
    errors_bn = pd.DataFrame(columns=['MAE', 'RMSE', 'MdAPE'])

    # Dynamic year range from start_year to end_year
    for rep in range(start_year, end_year + 1):  # From start_year to end_year
        # Split data by year
        train_start = country_data.index[country_data['YM'] == f'{rep}-01'][0]
        val_end = country_data.index[country_data['YM'] == f'{rep}-12'][-1]

        # Train and Validation DataFrames
        finaldf_train = country_data.loc[:train_start, :].copy()
        finaldf_train_x = finaldf_train.drop(columns=['Price'])
        finaldf_train_y = finaldf_train['Price']

        finaldf_test = country_data.loc[train_start:val_end, :].copy()
        finaldf_test_x = finaldf_test.drop(columns=['Price'])
        finaldf_test_y = finaldf_test['Price']

        # Generating Naive Forecast
        yhat = country_data.loc[train_start:val_end, 'Naive']

        # Creating DataFrame to track forecast results
        yyhat_rf = pd.DataFrame(index=finaldf_test_x.index, columns=['y', 'yhat_rf'])
        yyhat_rf['y'] = finaldf_test_y
        yyhat_rf['yhat_rf'] = yhat

        # Calculating error metrics
        mae = (abs(yyhat_rf['y'] - yyhat_rf['yhat_rf'])).mean()
        mdape = np.nanquantile((100 * (abs(yyhat_rf['y'] - yyhat_rf['yhat_rf']) / yyhat_rf['y'])), 0.5)
        rmse = math.sqrt(((yyhat_rf['y'] - yyhat_rf['yhat_rf']) ** 2).mean())

        # Storing errors for each year
        errors_bn.loc[rep, 'MAE'] = round(mae, 2)
        errors_bn.loc[rep, 'MdAPE'] = round(mdape, 2)
        errors_bn.loc[rep, 'RMSE'] = round(rmse, 2)

        print(f'Benchmarked for year {rep}')

    # Print final error metrics
    print(errors_bn)
    print(errors_bn.mean())

    return country_data, errors_bn
