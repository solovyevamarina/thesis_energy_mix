import pandas as pd
import os

from modelling_process.models.naive import naive_forecast
from modelling_process.models.linear import glm_forecast
from modelling_process.models.decision_tree import decision_tree_forecast
from modelling_process.models.random_forest import random_forest_forecast
from modelling_process.models.lgbm import lightgbm_forecast


def combined_forecasting_function(all_datasets, start_time, end_time, country, country_configs):

    file_name = f"{country}_{start_time}_{end_time}"
    country_data = all_datasets[file_name].copy()

    # Ensure output directories exist
    os.makedirs('results', exist_ok=True)

    # Initialize a DataFrame to store all results
    combined_results = pd.DataFrame(columns=['datetime', 'original', 'naive_result',
                                             'glm_result', 'dt_result',
                                             'rf_result', 'lgbm_result'])

    # Initialize a dictionary to store error metrics for all models
    all_errors = {'naive': [], 'glm': [], 'dt': [], 'rf': [], 'lgbm': []}

    # Models to call
    models = [
        ('naive', naive_forecast),
        ('glm', glm_forecast),
        ('dt', decision_tree_forecast),
        ('rf', random_forest_forecast),
        ('lgbm', lightgbm_forecast)
    ]

    # Loop through models and execute them
    for model_name, model_function in models:
        print(f"Running {model_name} model...")

        # Call the model function
        finaldf, errors, errors_tuned, model_storage = model_function(country_data, start_time, end_time, country, country_configs)

        # Save errors to the all_errors dictionary
        errors['Model'] = model_name
        all_errors[model_name] = errors

        # Extract unpruned model predictions
        model_results = finaldf[['Datetime', 'yhat']].rename(columns={'yhat': f'Result_{model_name}'})

        # Merge unpruned model results into the combined DataFrame
        if combined_results.empty:
            combined_results = model_results.rename(columns={'Price': 'Original_Price'})
        else:
            combined_results = pd.merge(combined_results, model_results, on='Datetime', how='outer')

        # Save unpruned predictions
        model_results.to_csv(f'results/{model_name}_{country}_results.csv', index=False)

        # Check if tuned errors are not null
        if errors_tuned is not None and not errors_tuned.empty:
            # Save tuned errors
            errors_tuned['Model'] = f"{model_name}_{country}_tuned"
            all_errors[f"{model_name}_{country}_tuned"] = errors_tuned

            # Extract tuned model predictions
            tuned_results = finaldf[['Datetime', 'yhat_tuned']].rename(columns={'yhat_tuned': f'Result_{model_name}_tuned'})

            # Merge tuned results into the combined DataFrame
            combined_results = pd.merge(combined_results, tuned_results, on='Datetime', how='outer')

            # Save tuned predictions
            tuned_results.to_csv(f'results/{model_name}_{country}_tuned_results.csv', index=False)

    # Save combined results
    combined_results.to_csv(f'results/combined_results_{country}.csv', index=False)

    # Convert all_errors values to DataFrames, if not already
    all_errors = {k: pd.DataFrame(v) if isinstance(v, list) else v for k, v in all_errors.items()}

    # Combine all errors into a single DataFrame
    error_summary = pd.concat(all_errors.values(), ignore_index=True)

    # Save error summary
    error_summary.to_csv(f'results/error_summary_{country}.csv', index=False)

    print("Forecasting completed. Results and errors saved.")
    return combined_results, error_summary
