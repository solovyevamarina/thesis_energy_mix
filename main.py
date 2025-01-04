import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd
from data_engineering.function_download import download_function
from data_engineering.function_data_cleaning import data_cleaning_function
from data_engineering.function_feature_engineering import feature_engineering
from data_visualization.county_data_graphs import (generate_energy_mix_pie_chart, generate_energy_stack_plot,
                                                   generate_timeline_plot)

# Choose the set of countries and their respective time zones
countries = ['GR', 'PL', 'SE']
time_zones = ['Europe/Athens', 'Europe/Warsaw', 'Europe/Stockholm']

start_time = '20150101'
end_time = '20241231'

my_api_key = '611caff8-769f-4d12-8a5e-838efb1f684a'
my_path = 'csv'

# Prepare datasets where the data will be stored
raw_datasets = {}
all_datasets = {}

# for country, timezone in zip(countries, time_zones):
#     download_function(country, timezone, start_time, end_time, raw_datasets, my_path, my_api_key)
#     data_cleaning_function(country, start_time, end_time, timezone, raw_datasets, all_datasets)
#     feature_engineering(all_datasets, country, start_time, end_time)


country = 'GR'
timezone = 'Europe/Athens'

download_function(country, timezone, start_time, end_time, raw_datasets, my_path, my_api_key)
data_cleaning_function(country, start_time, end_time, timezone, raw_datasets, all_datasets)
feature_engineering(all_datasets, country, start_time, end_time)
generate_energy_mix_pie_chart(all_datasets, country, start_time, end_time)
generate_energy_stack_plot(all_datasets, country, start_time, end_time)
generate_timeline_plot(all_datasets, country, start_time, end_time)
