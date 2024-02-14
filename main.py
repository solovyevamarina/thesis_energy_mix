import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd
from data_engineering.function_download import download_function
from data_engineering.function_data_cleaning import data_cleaning_function

############################################### KEY PARAMETERS #########################################################

# Choose the set of countries and their respective time zones
countries = ['GR', 'PL', 'SE']
time_zones = ['Europe/Athens', 'Europe/Warsaw', 'Europe/Stockholm']

start_time = '20150101'
end_time = '20221101'

my_api_key = '611caff8-769f-4d12-8a5e-838efb1f684a'
my_path = 'E:/Study/Diploma/csv'

################################################ DOWNLOAD DATA #########################################################
raw_datasets = {}
all_datasets = {}

for country, timezone in zip(countries, time_zones):
    download_function(country, timezone, start_time, end_time, raw_datasets, my_path, my_api_key)
    data_cleaning_function(country, start_time, end_time, timezone, raw_datasets, all_datasets)



############################################## CLEAN & UNITE DATA ######################################################

