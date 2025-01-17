import pandas as pd
import numpy as np
import math


def naive_forecast(country_data, start_time, end_time, country, country_configs):
    """
    Generate a naive forecast using the previous year's monthly averages and calculate error metrics.
    Returns a DataFrame with Datetime, Price, and yhat for all years.
    """
    # Add the 'Naive' column for forecasts
    country_data['yhat'] = np.nan

    # Create a dynamic list of years from start_time to end_time
    start_year = int(start_time[:4])
    end_year = int(end_time[:4])
    ym_list = country_data['Year-Month'].unique()

    # Generate naive forecasts
    for rep in range(12, len(ym_list)):  # Skip the first 12 months
        country_data.loc[country_data['Year-Month'] == ym_list[rep], 'yhat'] = round(
            country_data.loc[country_data['Year-Month'] == ym_list[rep - 12], 'Price'].mean(), 2
        )

    for rep in range(0, 12):  # For the first 12 months, use the mean of the same month in the same year
        country_data.loc[country_data['Year-Month'] == ym_list[rep], 'yhat'] = round(
            country_data.loc[country_data['Year-Month'] == ym_list[rep], 'Price'].mean(), 2
        )

    # Create a DataFrame to track errors
    errors_bn = pd.DataFrame(columns=['Year', 'MAE', 'RMSE', 'MdAPE'])

    # Dynamic year range from start_year to end_year
    for rep in range(start_year+1, end_year+1):
        # Filter data for the current year
        year_data = country_data[country_data['Year-Month'].str.startswith(f'{rep}-')]

        # Validation Data
        finaldf_test_y = year_data['Price']
        yhat = year_data['yhat']

        # Calculate error metrics
        mae = (abs(finaldf_test_y - yhat)).mean()
        mdape = np.nanquantile((100 * abs((finaldf_test_y - yhat) / finaldf_test_y)), 0.5)
        rmse = math.sqrt(((finaldf_test_y - yhat) ** 2).mean())

        # Create a temporary DataFrame for this year's errors
        temp_error_df = pd.DataFrame({
            'Year': [rep],
            'MAE': [round(mae, 2)],
            'RMSE': [round(rmse, 2)],
            'MdAPE': [round(mdape, 2)]
        })

        # Concatenate the errors to the main DataFrame
        errors_bn = pd.concat([errors_bn, temp_error_df], ignore_index=True)

        print(f'Benchmarked for year {rep}')

    # Print final error metrics
    print(errors_bn)
    print(errors_bn.mean())

    # Create the final DataFrame with Datetime, Price, and yhat for all data
    final_output = country_data[['Datetime', 'Price', 'yhat']].copy()

    # Return the final DataFrame, error metrics, None for additional errors, and None for model storage
    return final_output, errors_bn, None, None
