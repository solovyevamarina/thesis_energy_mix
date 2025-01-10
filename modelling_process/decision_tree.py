import pandas as pd
import numpy as np
import math
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import GridSearchCV
import os


def decision_tree_forecast(country_data, start_time, end_time, country, country_configs):
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
    errors_dt = pd.DataFrame(columns=['Year', 'MAE', 'RMSE', 'MdAPE'])
    errors_pdt = pd.DataFrame(columns=['Year', 'MAE', 'RMSE', 'MdAPE'])

    # Initialize DecisionTreeRegressor
    dt = DecisionTreeRegressor(random_state=0)

    # Hyperparameter grid for tuning
    params = {
        'min_samples_split': [10, 20, 30, 50, 70],
        'max_features': [20, 30, 40, 56],
        'max_leaf_nodes': [4, 7, 15, 31, 63, 127]
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

        # Fit the Decision Tree model
        fit = dt.fit(finaldf_train_x, finaldf_train_y)
        test_predict = fit.predict(finaldf_test_x)

        # DataFrame to store predictions and actual values
        yyhat_dt = pd.DataFrame(index=finaldf_test_y.index, columns=['datetime', 'y', 'yhat_dt', 'yhat_pdt'])
        yyhat_dt['datetime'] = finaldf_test.index
        yyhat_dt['y'] = finaldf_test_y
        yyhat_dt['yhat_dt'] = test_predict

        # Calculate error metrics for the "grown" model (without pruning)
        mae = (abs(yyhat_dt['y'] - yyhat_dt['yhat_dt'])).mean()
        mdape = np.nanquantile((100 * (abs(yyhat_dt['y'] - yyhat_dt['yhat_dt']) / yyhat_dt['y'])), 0.5)
        rmse = math.sqrt(((yyhat_dt['y'] - yyhat_dt['yhat_dt']) ** 2).mean())

        # Store errors for the grown decision tree using concat instead of append
        new_row_dt = pd.DataFrame({'Year': [rep], 'MAE': [round(mae, 2)], 'RMSE': [round(rmse, 2)], 'MdAPE': [round(mdape, 2)]})
        errors_dt = pd.concat([errors_dt, new_row_dt], ignore_index=True)

        # Perform hyperparameter tuning using GridSearchCV
        gcv = GridSearchCV(estimator=dt, param_grid=params, cv=2)
        gcv.fit(finaldf_train_x, finaldf_train_y)

        # Get the best pruned model
        model = gcv.best_estimator_
        test_predict_pruned = model.predict(finaldf_test_x)

        # Calculate error metrics for the "pruned" model
        yyhat_dt['yhat_pdt'] = test_predict_pruned

        mae_pdt = (abs(yyhat_dt['y'] - yyhat_dt['yhat_pdt'])).mean()
        mdape_pdt = np.nanquantile((100 * (abs(yyhat_dt['y'] - yyhat_dt['yhat_pdt']) / yyhat_dt['y'])), 0.5)
        rmse_pdt = math.sqrt(((yyhat_dt['y'] - yyhat_dt['yhat_pdt']) ** 2).mean())

        # Store errors for the pruned decision tree using concat instead of append
        new_row_pdt = pd.DataFrame({'Year': [rep], 'MAE': [round(mae_pdt, 2)], 'RMSE': [round(rmse_pdt, 2)], 'MdAPE': [round(mdape_pdt, 2)]})
        errors_pdt = pd.concat([errors_pdt, new_row_pdt], ignore_index=True)

        # Save the yyhat_dt DataFrame for this year
        yyhat_dt.to_csv(f'results/yyhat_dt_{rep}.csv', index=False)

        print(f'Completed Decision Tree for year {rep + 1} / {end_year - start_year} years')

    # Save errors DataFrames to CSV
    errors_dt.to_csv('results/errors_dt.csv', index=False)
    errors_pdt.to_csv('results/errors_pdt.csv', index=False)

    print("Final Error Metrics (Grown Trees):")
    print(errors_dt)
    print("Mean Error Metrics (Grown Trees):")
    print(errors_dt.mean())

    print("Final Error Metrics (Pruned Trees):")
    print(errors_pdt)
    print("Mean Error Metrics (Pruned Trees):")
    print(errors_pdt.mean())

    return finaldf_prep, errors_dt, errors_pdt

# Example usage:
# country_data = your_data
# start_time = '2015-01-01'
# end_time = '2022-12-31'
# country_code = 'PL'  # Example: use 'PL' for Poland
# finaldf, errors_dt, errors_pdt, model_storage = decision_tree_forecast(country_data, start_time, end_time, country_code, country_configs)
