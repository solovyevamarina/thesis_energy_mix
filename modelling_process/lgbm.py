import pandas as pd
import numpy as np
import math
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import PredefinedSplit
import lightgbm as lgb


import os

def lightgbm_forecast(country_data, start_time, end_time, country, country_configs):
    # Ensure results directory exists
    os.makedirs('results', exist_ok=True)

    # Get sources and labels based on the country code from country_configs
    country_config = country_configs[country]

    # Create sources with '_share' suffix dynamically
    sources = [f"{source}_share" for source in country_config['sources']]

    # Dynamically select columns based on patterns
    month_columns = [col for col in country_data.columns if col.startswith('Month_')]
    weekday_columns = [col for col in country_data.columns if col.startswith('Weekday_')]
    hour_columns = [col for col in country_data.columns if col.startswith('Hour_')]

    # Define other important columns explicitly
    other_columns = ['Load', 'Price', 'Gas_Price', 'Holiday', 'Flow']

    # Combine all relevant columns
    relevant_columns = sources + month_columns + weekday_columns + hour_columns + other_columns

    # Prepare the data by selecting the relevant columns
    finaldf_prep = country_data[relevant_columns].copy()

    # Create DataFrames to track errors
    errors_lgbm = pd.DataFrame(list(), columns=['Year', 'MAE', 'RMSE', 'MdAPE'])
    errors_tlgbm = pd.DataFrame(list(), columns=['Year', 'MAE', 'RMSE', 'MdAPE'])

    # Initialize LightGBM Regressor
    lgbm = lgb.LGBMRegressor(random_state=0)

    # Hyperparameter grid for tuning
    params = {
        'n_estimators': [500, 1000, 1500],
        'learning_rate': [0.01, 0.1, 0.2],
        'num_leaves': [15, 31, 63, 127]
    }

    # Loop for model fitting and prediction for each year
    start_year = int(start_time[:4])
    end_year = int(end_time[:4])

    for rep in range(start_year, end_year):  # Loop through the years
        train_end_idx = 168 * 52 * (rep - start_year + 1)  # Training data ends here
        test_end_idx = 168 * 52 * (rep - start_year + 2)  # Test data ends here

        # Split data into training and testing datasets
        finaldf_train = finaldf_prep.loc[:train_end_idx, :].copy()
        finaldf_train_x = finaldf_train.loc[:, finaldf_train.columns != 'Price']
        finaldf_train_y = finaldf_train['Price']

        finaldf_test = finaldf_prep.loc[train_end_idx + 1:test_end_idx, :].copy()
        finaldf_test_x = finaldf_test.loc[:, finaldf_test.columns != 'Price']
        finaldf_test_y = finaldf_test['Price']

        # Fit the LightGBM model
        fit = lgbm.fit(finaldf_train_x, finaldf_train_y)
        test_predict = fit.predict(finaldf_test_x)

        # DataFrame to store predictions and actual values
        yyhat_lgbm = pd.DataFrame(index=finaldf_test_y.index, columns=['datetime', 'y', 'yhat_lgbm', 'yhat_tlgbm'])
        yyhat_lgbm['datetime'] = finaldf_test.index
        yyhat_lgbm['y'] = finaldf_test_y
        yyhat_lgbm['yhat_lgbm'] = test_predict

        # Calculate error metrics for the "grown" model (without tuning)
        mae = (abs(yyhat_lgbm['y'] - yyhat_lgbm['yhat_lgbm'])).mean()
        mdape = np.nanquantile((100 * (abs(yyhat_lgbm['y'] - yyhat_lgbm['yhat_lgbm']) / yyhat_lgbm['y'])), 0.5)
        rmse = ((yyhat_lgbm['y'] - yyhat_lgbm['yhat_lgbm']) ** 2).mean() ** 0.5

        # Store errors for the grown LightGBM
        errors_lgbm = errors_lgbm.append({'Year': rep, 'MAE': round(mae, 2), 'RMSE': round(rmse, 2), 'MdAPE': round(mdape, 2)}, ignore_index=True)

        # Perform hyperparameter tuning using GridSearchCV
        gcv = GridSearchCV(estimator=lgbm, param_grid=params, cv=2, verbose=2)
        gcv.fit(finaldf_train_x, finaldf_train_y)

        # Get the best tuned model
        model = gcv.best_estimator_
        test_predict_tuned = model.predict(finaldf_test_x)

        # Calculate error metrics for the "tuned" model
        yyhat_lgbm['yhat_tlgbm'] = test_predict_tuned

        mae_tlgbm = (abs(yyhat_lgbm['y'] - yyhat_lgbm['yhat_tlgbm'])).mean()
        mdape_tlgbm = np.nanquantile((100 * (abs(yyhat_lgbm['y'] - yyhat_lgbm['yhat_tlgbm']) / yyhat_lgbm['y'])), 0.5)
        rmse_tlgbm = ((yyhat_lgbm['y'] - yyhat_lgbm['yhat_tlgbm']) ** 2).mean() ** 0.5

        # Store errors for the tuned LightGBM
        errors_tlgbm = errors_tlgbm.append({'Year': rep, 'MAE': round(mae_tlgbm, 2), 'RMSE': round(rmse_tlgbm, 2), 'MdAPE': round(mdape_tlgbm, 2)}, ignore_index=True)

        # Save the yyhat_lgbm DataFrame for this year
        yyhat_lgbm.to_csv(f'results/yyhat_lgbm_{rep}.csv', index=False)

        print(f'Completed LightGBM for year {rep + 1} / {end_year - start_year} years')

    # Save errors DataFrames to CSV
    errors_lgbm.to_csv('results/errors_lgbm.csv', index=False)
    errors_tlgbm.to_csv('results/errors_tlgbm.csv', index=False)

    print("Final Error Metrics (Grown LGBM):")
    print(errors_lgbm)
    print("Mean Error Metrics (Grown LGBM):")
    print(errors_lgbm.mean())

    print("Final Error Metrics (Tuned LGBM):")
    print(errors_tlgbm)
    print("Mean Error Metrics (Tuned LGBM):")
    print(errors_tlgbm.mean())

    return finaldf_prep, errors_lgbm, errors_tlgbm

# Example usage:
# country_data = your_data
# start_time = '2015-01-01'
# end_time = '2022-12-31'
# country_code = 'PL'  # Example: use 'PL' for Poland
# finaldf, errors_lgbm, errors_tlgbm, model_storage = lightgbm_forecast(country_data, start_time, end_time, country_code, country_configs)
