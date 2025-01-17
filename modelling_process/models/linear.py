import pandas as pd
import numpy as np
import math
import statsmodels.formula.api as smf


def glm_forecast(country_data, start_time, end_time, country, country_configs):

    # Get sources and labels based on the country code from country_configs
    country_config = country_configs[country]

    # Create sources with '_share' suffix
    sources = [f"{source}_share" for source in country_config['sources']]

    # Construct the GLM formula dynamically
    formula_sha = 'Price ~ ' + ' + '.join(sources) + ' + Gas_Price + Load + Holiday + Flow - 1'

    # Create a DataFrame to track errors
    errors_mean = pd.DataFrame(columns=['Year', 'MAE', 'RMSE', 'MdAPE'])

    # Create a DataFrame to store all yhat values
    all_predictions = pd.DataFrame(columns=['Datetime', 'y', 'yhat'])

    # Dynamic year range from start_time to end_time
    start_year = int(start_time[:4])
    end_year = int(end_time[:4])

    # Loop for model fitting and prediction for each year
    for rep in range(start_year+1, end_year+1):  # Loop through the years
        train_years = [str(year) for year in range(start_year, rep)]
        test_year = str(rep)

        # Split data into training and testing datasets
        h_shares_train = country_data.loc[country_data['Year'].isin(train_years), :].copy()
        h_shares_test = country_data.loc[country_data['Year'] == test_year, :].copy()

        # Fit GLM model
        model_sha = smf.glm(formula=formula_sha, data=h_shares_train)
        result_sha = model_sha.fit()
        print(f'Year {rep}: {result_sha.summary()}')

        # Predictions on the test dataset
        yyhat_df = pd.DataFrame(index=h_shares_test.index, columns=['Datetime', 'y', 'yhat'])
        yyhat_df['Datetime'] = h_shares_test['Datetime']
        yyhat_df['y'] = h_shares_test['Price']

        # Predict using the fitted model
        test_predict = result_sha.predict(h_shares_test)
        yyhat_df['yhat'] = test_predict

        # Append predictions to all_predictions DataFrame
        all_predictions = pd.concat([all_predictions, yyhat_df], ignore_index=True)

        # Error Metrics Calculation
        mae = (abs(yyhat_df['y'] - yyhat_df['yhat'])).mean()  # Mean Absolute Error
        mdape = np.nanquantile((100 * (abs(yyhat_df['y'] - yyhat_df['yhat']) / yyhat_df['y'])), 0.5)  # MdAPE
        rmse = math.sqrt(((yyhat_df['y'] - yyhat_df['yhat']) ** 2).mean())  # RMSE

        # Store errors for each year
        errors_mean = pd.concat(
            [errors_mean, pd.DataFrame({'Year': [rep], 'MAE': [round(mae, 2)], 'MdAPE': [round(mdape, 2)], 'RMSE': [round(rmse, 2)]})],
            ignore_index=True,
        )

        print(f'Year {rep}: MAE={mae:.2f}, MdAPE={mdape:.2f}, RMSE={rmse:.2f}')

    # Print final error metrics
    print("Final Error Metrics:")
    print(errors_mean)
    print("Mean Error Metrics:")
    print(errors_mean.mean())

    # Return the expected 4 values: all_predictions DataFrame, errors, None for additional errors, None for model storage
    return all_predictions, errors_mean, None, None
