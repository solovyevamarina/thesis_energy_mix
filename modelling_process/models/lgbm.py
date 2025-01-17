import pandas as pd
import numpy as np
import os
import lightgbm as lgb
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import PredefinedSplit

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

    # Create DataFrames to track errors and best parameters
    errors_lgbm = pd.DataFrame(columns=['Year', 'MAE', 'RMSE', 'MdAPE'])
    errors_tlgbm = pd.DataFrame(columns=['Year', 'MAE', 'RMSE', 'MdAPE'])
    best_params_lgbm = pd.DataFrame(columns=['Year', 'Best_Params'])

    # Initialize LightGBM Regressor
    lgbm = lgb.LGBMRegressor(random_state=0)

    # Hyperparameter grid for tuning
    params = {
        'n_estimators': [500, 1000, 1500],
        'learning_rate': [0.01, 0.1, 0.2],
        'num_leaves': [15, 31, 63, 127]
    }

    # Initialize a DataFrame to track all predictions
    all_predictions = pd.DataFrame(columns=['Datetime', 'y', 'yhat', 'yhat_tuned'])

    # Loop for model fitting and prediction for each year
    start_year = int(start_time[:4])
    end_year = int(end_time[:4])

    # Loop for model fitting and prediction for each year
    for rep in range(start_year + 1, end_year + 1):  # Loop through the years
        train_idx = country_data.index[country_data['Year'] == str(rep)][0]
        val_idx = country_data.index[country_data['Year'] == str(rep)][-1]

        finaldf_train = finaldf_prep.loc[:train_idx, :].copy()
        finaldf_train_x = finaldf_train.loc[:, finaldf_train.columns != 'Price']
        finaldf_train_y = finaldf_train['Price']

        finaldf_val = finaldf_prep.loc[train_idx:val_idx, :].copy()
        finaldf_val_x = finaldf_val.loc[:, finaldf_val.columns != 'Price']
        finaldf_val_y = finaldf_val['Price']

        train_indices = np.full((train_idx,), -1, dtype=int)
        val_indices = np.full((val_idx - train_idx,), 0, dtype=int)
        val_fold = np.append(train_indices, val_indices)

        ps = PredefinedSplit(val_fold)

        fit = lgbm.fit(finaldf_train_x, finaldf_train_y)
        test_predict = fit.predict(finaldf_val_x)

        yyhat = pd.DataFrame(index=finaldf_val_y.index, columns=['Datetime', 'y', 'yhat', 'yhat_tuned'])
        yyhat['Datetime'] = country_data.loc[finaldf_val.index, 'Datetime']
        yyhat['y'] = finaldf_val_y
        yyhat['yhat'] = test_predict

        mae = (abs(yyhat['y'] - yyhat['yhat'])).mean()
        mdape = np.nanquantile((100 * (abs(yyhat['y'] - yyhat['yhat']) / yyhat['y'])), 0.5)
        rmse = ((yyhat['y'] - yyhat['yhat']) ** 2).mean() ** 0.5

        errors_lgbm = pd.concat([errors_lgbm, pd.DataFrame(
            {'Year': [rep], 'MAE': [round(mae, 2)], 'RMSE': [round(rmse, 2)], 'MdAPE': [round(mdape, 2)]})],
                                ignore_index=True)

        finaldf_valtrain = finaldf_prep.loc[:val_idx, :].copy()
        finaldf_valtrain_x = finaldf_valtrain.loc[:, finaldf_valtrain.columns != 'Price']
        finaldf_valtrain_y = finaldf_valtrain['Price']

        gcv = GridSearchCV(estimator=lgbm, param_grid=params, cv=ps, verbose=2)
        gcv.fit(finaldf_valtrain_x, finaldf_valtrain_y)

        model = gcv.best_estimator_
        test_predict_tuned = model.predict(finaldf_val_x)

        yyhat['yhat_tuned'] = test_predict_tuned

        # Calculate error metrics for the "tuned" model
        mae_tlgbm = (abs(yyhat['y'] - yyhat['yhat_tuned'])).mean()
        mdape_tlgbm = np.nanquantile((100 * (abs(yyhat['y'] - yyhat['yhat_tuned']) / yyhat['y'])), 0.5)
        rmse_tlgbm = ((yyhat['y'] - yyhat['yhat_tuned']) ** 2).mean() ** 0.5

        # Store errors for the tuned LightGBM
        errors_tlgbm = pd.concat([errors_tlgbm, pd.DataFrame(
            {'Year': [rep], 'MAE': [round(mae_tlgbm, 2)], 'RMSE': [round(rmse_tlgbm, 2)], 'MdAPE': [round(mdape_tlgbm, 2)]})],
                                 ignore_index=True)

        # Append predictions to the all_predictions DataFrame
        all_predictions = pd.concat([all_predictions, yyhat], ignore_index=True)

        # Save the yyhat DataFrame for this year
        yyhat.to_csv(f'results/yyhat_{rep}.csv', index=False)

        print(f'Completed LightGBM for year {rep + 1} / {end_year - start_year} years')

    # Save errors DataFrames to CSV
    errors_lgbm.to_csv('results/errors_lgbm.csv', index=False)
    errors_tlgbm.to_csv('results/errors_tlgbm.csv', index=False)

    # Save best parameters to CSV
    best_params_lgbm.to_csv('results/best_params_lgbm.csv', index=False)

    print("Final Error Metrics (Grown LGBM):")
    print(errors_lgbm)
    print("Mean Error Metrics (Grown LGBM):")
    print(errors_lgbm.mean())

    print("Final Error Metrics (Tuned LGBM):")
    print(errors_tlgbm)
    print("Mean Error Metrics (Tuned LGBM):")
    print(errors_tlgbm.mean())

    # Return all predictions, errors, and best parameters
    return all_predictions, errors_lgbm, errors_tlgbm, best_params_lgbm
