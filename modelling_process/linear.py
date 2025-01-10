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
    errors_mean = pd.DataFrame(columns=['MAE', 'RMSE', 'MdAPE'])

    # Dynamic year range from start_time to end_time
    start_year = int(start_time[:4])
    end_year = int(end_time[:4])

    # Loop for model fitting and prediction for each year
    for rep in range(start_year, end_year):  # Loop through the years
        train_end_idx = 168 * 52 * (rep - start_year + 1)  # Training data ends here
        test_end_idx = 168 * 52 * (rep - start_year + 2)  # Test data ends here

        # Split data into training and testing datasets
        h_shares_train = country_data.loc[:train_end_idx, :].copy()
        h_shares_test = country_data.loc[train_end_idx + 1:test_end_idx, :].copy()

        # Fit GLM model
        model_sha = smf.glm(formula=formula_sha, data=h_shares_train)
        result_sha = model_sha.fit()
        print(f'Year {rep}: {result_sha.summary()}')

        # Predictions on the test dataset
        yyhat_df = pd.DataFrame(index=h_shares_test.index, columns=['y', 'yhat'])
        yyhat_df['y'] = h_shares_test['Price']

        # Predict using the fitted model
        test_predict = result_sha.predict(h_shares_test)
        yyhat_df['yhat'] = test_predict

        # Error Metrics Calculation
        mae = (abs(yyhat_df['y'] - yyhat_df['yhat'])).mean()  # Mean Absolute Error
        mdape = np.quantile((100 * (abs(yyhat_df['y'] - yyhat_df['yhat']) / yyhat_df['y'])),
                            0.5)  # Median Absolute Percentage Error
        rmse = math.sqrt(((yyhat_df['y'] - yyhat_df['yhat']) ** 2).mean())  # Root Mean Square Error

        # Store errors for each year
        errors_mean.loc[rep, 'MAE'] = round(mae, 2)
        errors_mean.loc[rep, 'MdAPE'] = round(mdape, 2)
        errors_mean.loc[rep, 'RMSE'] = round(rmse, 2)

        print(f'Year {rep}: MAE={mae:.2f}, MdAPE={mdape:.2f}, RMSE={rmse:.2f}')

    # Print final error metrics
    print("Final Error Metrics:")
    print(errors_mean)
    print("Mean Error Metrics:")
    print(errors_mean.mean())

    return country_data, errors_mean
