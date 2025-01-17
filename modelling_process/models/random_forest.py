import pandas as pd
import numpy as np
import math
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV
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

    # Create DataFrames to track errors and best parameters
    errors_rf = pd.DataFrame(columns=['Year', 'MAE', 'RMSE', 'MdAPE'])
    errors_trf = pd.DataFrame(columns=['Year', 'MAE', 'RMSE', 'MdAPE'])
    best_params_rf = pd.DataFrame(columns=['Year', 'Best_Params'])

    # Initialize RandomForestRegressor
    rf = RandomForestRegressor(random_state=0)

    # Hyperparameter grid for tuning
    params = {
        'n_estimators': [100, 200, 300],
        'max_leaf_nodes': [15, 31, 63],
        'min_samples_split': [20, 30, 50]
    }

    # Initialize a DataFrame to track all predictions
    all_predictions = pd.DataFrame(columns=['Datetime', 'y', 'yhat', 'yhat_tuned'])

    # Loop for model fitting and prediction for each year
    start_year = int(start_time[:4])
    end_year = int(end_time[:4])

    # Loop for model fitting and prediction for each year
    for rep in range(start_year+1, end_year+1):  # Loop through the years
        train_years = [str(year) for year in range(start_year, rep)]
        test_year = str(rep)

        # Split data into training and testing datasets
        train_end_idx = country_data.loc[country_data['Year'].isin(train_years), :].index[-1]
        test_end_idx = country_data.loc[country_data['Year'] == test_year, :].index[-1]

        # Split data into training and testing datasets
        finaldf_train = finaldf_prep.loc[:train_end_idx, :].copy()
        finaldf_train_x = finaldf_train.loc[:, finaldf_train.columns != 'Price']
        finaldf_train_y = finaldf_train['Price']

        finaldf_test = finaldf_prep.loc[train_end_idx + 1:test_end_idx, :].copy()
        finaldf_test_x = finaldf_test.loc[:, finaldf_test.columns != 'Price']
        finaldf_test_y = finaldf_test['Price']

        # Fit the Random Forest model (grown model)
        fit = rf.fit(finaldf_train_x, finaldf_train_y)
        test_predict = fit.predict(finaldf_test_x)

        # DataFrame to store predictions and actual values
        yyhat = pd.DataFrame(index=finaldf_test_y.index, columns=['Datetime', 'y', 'yhat', 'yhat_tuned'])
        yyhat['Datetime'] = country_data.loc[finaldf_test.index, 'Datetime']
        yyhat['y'] = finaldf_test_y
        yyhat['yhat'] = test_predict

        # Calculate error metrics for the "grown" model (without tuning)
        mae = (abs(yyhat['y'] - yyhat['yhat'])).mean()
        mdape = np.nanquantile((100 * (abs(yyhat['y'] - yyhat['yhat']) / yyhat['y'])), 0.5)
        rmse = ((yyhat['y'] - yyhat['yhat']) ** 2).mean() ** 0.5

        # Store errors for the grown random forest using pd.concat
        errors_rf = pd.concat([errors_rf, pd.DataFrame(
            {'Year': [rep], 'MAE': [round(mae, 2)], 'RMSE': [round(rmse, 2)], 'MdAPE': [round(mdape, 2)]})],
                              ignore_index=True)

        # Perform hyperparameter tuning using GridSearchCV
        gcv = GridSearchCV(estimator=rf, param_grid=params, cv=2)
        gcv.fit(finaldf_train_x, finaldf_train_y)

        # Get the best tuned model and best parameters
        model = gcv.best_estimator_
        test_predict_tuned = model.predict(finaldf_test_x)

        # Save the best parameters for the tuned model
        best_params_rf = pd.concat([best_params_rf, pd.DataFrame({'Year': [rep], 'Best_Params': [gcv.best_params_]})],
                                   ignore_index=True)

        # Add tuned predictions to the DataFrame
        yyhat['yhat_tuned'] = test_predict_tuned

        # Calculate error metrics for the "tuned" model
        mae_trf = (abs(yyhat['y'] - yyhat['yhat_tuned'])).mean()
        mdape_trf = np.nanquantile((100 * (abs(yyhat['y'] - yyhat['yhat_tuned']) / yyhat['y'])), 0.5)
        rmse_trf = ((yyhat['y'] - yyhat['yhat_tuned']) ** 2).mean() ** 0.5

        # Store errors for the tuned random forest using pd.concat
        errors_trf = pd.concat([errors_trf, pd.DataFrame(
            {'Year': [rep], 'MAE': [round(mae_trf, 2)], 'RMSE': [round(rmse_trf, 2)], 'MdAPE': [round(mdape_trf, 2)]})],
                               ignore_index=True)

        # Append predictions to the all_predictions DataFrame
        all_predictions = pd.concat([all_predictions, yyhat], ignore_index=True)

        # Save the yyhat DataFrame for this year
        yyhat.to_csv(f'results/yyhat_{rep}.csv', index=False)

        print(f'Completed Random Forest for year {rep + 1} / {end_year - start_year} years')

    # Save errors DataFrames to CSV
    errors_rf.to_csv('results/errors_rf.csv', index=False)
    errors_trf.to_csv('results/errors_trf.csv', index=False)

    # Save best parameters to CSV
    best_params_rf.to_csv('results/best_params_rf.csv', index=False)

    print("Final Error Metrics (Grown RF):")
    print(errors_rf)
    print("Mean Error Metrics (Grown RF):")
    print(errors_rf.mean())

    print("Final Error Metrics (Tuned RF):")
    print(errors_trf)
    print("Mean Error Metrics (Tuned RF):")
    print(errors_trf.mean())

    # Return all predictions, errors, and best parameters
    return all_predictions, errors_rf, errors_trf, best_params_rf
