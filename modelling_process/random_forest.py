import pandas as pd
import numpy as np
import math
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import PredefinedSplit
import os


def random_forest_forecast(country_data, start_time, end_time, country, country_configs):
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
    errors_rf = pd.DataFrame(columns=['Year', 'MAE', 'RMSE', 'MdAPE'])
    errors_trf = pd.DataFrame(columns=['Year', 'MAE', 'RMSE', 'MdAPE'])

    # Initialize RandomForestRegressor
    rf = RandomForestRegressor(random_state=0)

    # Hyperparameter grid for tuning
    params = {
        'n_estimators': [100, 200, 300],
        'max_leaf_nodes': [15, 31, 63],
        'min_samples_split': [20, 30, 50]
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

        # Fit the Random Forest model
        fit = rf.fit(finaldf_train_x, finaldf_train_y)
        test_predict = fit.predict(finaldf_test_x)

        # DataFrame to store predictions and actual values
        yyhat_rf = pd.DataFrame(index=finaldf_test_y.index, columns=['datetime', 'y', 'yhat_rf', 'yhat_trf'])
        yyhat_rf['datetime'] = finaldf_test.index
        yyhat_rf['y'] = finaldf_test_y
        yyhat_rf['yhat_rf'] = test_predict

        # Calculate error metrics for the "grown" model (without tuning)
        mae = (abs(yyhat_rf['y'] - yyhat_rf['yhat_rf'])).mean()
        mdape = np.nanquantile((100 * (abs(yyhat_rf['y'] - yyhat_rf['yhat_rf']) / yyhat_rf['y'])), 0.5)
        rmse = ((yyhat_rf['y'] - yyhat_rf['yhat_rf']) ** 2).mean() ** 0.5

        # Store errors for the grown random forest
        errors_rf = errors_rf.append({'Year': rep, 'MAE': round(mae, 2), 'RMSE': round(rmse, 2), 'MdAPE': round(mdape, 2)}, ignore_index=True)

        # Perform hyperparameter tuning using GridSearchCV
        gcv = GridSearchCV(estimator=rf, param_grid=params, cv=2)
        gcv.fit(finaldf_train_x, finaldf_train_y)

        # Get the best tuned model
        model = gcv.best_estimator_
        test_predict_tuned = model.predict(finaldf_test_x)

        # Calculate error metrics for the "tuned" model
        yyhat_rf['yhat_trf'] = test_predict_tuned

        mae_trf = (abs(yyhat_rf['y'] - yyhat_rf['yhat_trf'])).mean()
        mdape_trf = np.nanquantile((100 * (abs(yyhat_rf['y'] - yyhat_rf['yhat_trf']) / yyhat_rf['y'])), 0.5)
        rmse_trf = ((yyhat_rf['y'] - yyhat_rf['yhat_trf']) ** 2).mean() ** 0.5

        # Store errors for the tuned random forest
        errors_trf = errors_trf.append({'Year': rep, 'MAE': round(mae_trf, 2), 'RMSE': round(rmse_trf, 2), 'MdAPE': round(mdape_trf, 2)}, ignore_index=True)

        # Save the yyhat_rf DataFrame for this year
        yyhat_rf.to_csv(f'results/yyhat_rf_{rep}.csv', index=False)

        print(f'Completed Random Forest for year {rep + 1} / {end_year - start_year} years')

    # Save errors DataFrames to CSV
    errors_rf.to_csv('results/errors_rf.csv', index=False)
    errors_trf.to_csv('results/errors_trf.csv', index=False)

    print("Final Error Metrics (Grown RF):")
    print(errors_rf)
    print("Mean Error Metrics (Grown RF):")
    print(errors_rf.mean())

    print("Final Error Metrics (Tuned RF):")
    print(errors_trf)
    print("Mean Error Metrics (Tuned RF):")
    print(errors_trf.mean())

    return finaldf_prep, errors_rf, errors_trf

# Example usage:
# country_data = your_data
# start_time = '2015-01-01'
# end_time = '2022-12-31'
# country_code = 'PL'  # Example: use 'PL' for Poland
# finaldf, errors_rf, errors_trf, model_storage = random_forest_forecast(country_data, start_time, end_time, country_code, country_configs)
