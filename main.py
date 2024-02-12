import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

from data_engineering.function_download import download_data

############################################### KEY PARAMETERS #########################################################

# Choose the set of countries and their respective time zones
countries = ['GR', 'PL', 'SE']
time_zones = ['Europe/Athens', 'Europe/Warsaw', 'Europe/Stockholm']

start_time = '20150101'
end_time = '20221101'

my_api_key = 'my_api_key'
my_path = 'E:/Study/Diploma/csv'

raw_datasets = {}

################################################ DOWNLOAD DATA #########################################################

# Data will be saved in csv format in the path folder
# It takes quite some time (several hours depending on the time window)
# If file already exists, read pre-downloaded data

for country, timezone in zip(countries, time_zones):
    download_data(country, timezone, start_time, end_time, raw_datasets, my_path, my_api_key)
