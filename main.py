import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
from data_engineering.function_download import download_function
from data_engineering.function_data_cleaning import data_cleaning_function
from data_engineering.function_feature_engineering import feature_engineering
from data_visualization.function_generate_plots import generate_descriptive_plots

# Choose the set of countries and their respective time zones
countries = ['GR', 'PL', 'SE']
time_zones = ['Europe/Athens', 'Europe/Warsaw', 'Europe/Stockholm']

start_time = '20150101'
end_time = '20241231'

my_api_key = '611caff8-769f-4d12-8a5e-838efb1f684a'
my_path = 'F:/Study/Diploma/csv'

# Prepare datasets where the data will be stored
raw_datasets = {}
all_datasets = {}


country_configs = {
    'GR': {
        'country_name': ['Ελλάδα'],
        'sources': ['Coal', 'Gas', 'Oil', 'Solar', 'Wind', 'Hydro'],
        'labels': ('Λινίτης', 'Φυσικό Αέριο', 'Πετρέλαιο', 'Φωτοβολταϊκά', 'Αιολικά', 'Ύδροηλεκτρικά'),
        'colors': ['brown', 'teal', 'black', 'yellow', 'skyblue', 'blue'],
        'fossil_sources': ['Coal', 'Gas', 'Oil'],
        'renewable_sources': ['Solar', 'Wind', 'Hydro']
    },
    'PL': {
        'country_name': ['Πολωνία'],
        'sources': ['Biomass', 'Coal', 'Hard Coal', 'Coal Gas', 'Gas', 'Oil', 'Solar', 'Wind', 'Hydro'],
        'labels': ('Βιομάζα', 'Λινίτης', 'Άνθρακας', 'Ανθρακαέριο', 'Φυσικό Αέριο', 'Πετρέλαιο', 'Φωτοβολταϊκά', 'Αιολικά', 'Ύδροηλεκτρικά'),
        'colors': ['olive', 'brown', 'dimgray', 'slategrey', 'teal', 'black', 'yellow', 'skyblue', 'blue'],
        'fossil_sources': ['Coal', 'Hard Coal', 'Coal Gas', 'Gas', 'Oil'],
        'renewable_sources': ['Biomass', 'Hydro', 'Solar', 'Wind']
    },
    'SE': {
        'country_name': ['Σουηδία'],
        'sources': ['Gas', 'Nuclear', 'Hydro', 'Solar', 'Wind', 'Other'],
        'labels': ('Φυσικό Αέριο', 'Πυρηνικά', 'Ύδροηλεκτρικά', 'Φωτοβολταϊκά', 'Αιολικά', 'Λοιπά ΑΕΠ'),
        'colors': ['teal', 'purple', 'blue', 'yellow', 'skyblue', 'gray'],
        'fossil_sources': ['Gas'],
        'renewable_sources': ['Hydro', 'Solar', 'Wind', 'Other']
    }
}


# for country, timezone in zip(countries, time_zones):
#     download_function(country, timezone, start_time, end_time, raw_datasets, my_path, my_api_key)
#     data_cleaning_function(country, start_time, end_time, timezone, raw_datasets, all_datasets)
#     feature_engineering(all_datasets, country, start_time, end_time)


country = 'GR'
timezone = 'Europe/Athens'

download_function(country, timezone, start_time, end_time, raw_datasets, my_path, my_api_key)
data_cleaning_function(country, start_time, end_time, timezone, raw_datasets, all_datasets,country_configs)
feature_engineering(all_datasets, country, start_time, end_time, country_configs)
generate_descriptive_plots(all_datasets, country, start_time, end_time, country_configs)

# generate_energy_mix_pie_chart(all_datasets, country, start_time, end_time)
# generate_energy_stack_plot(all_datasets, country, start_time, end_time)
# generate_price_timeline_plot(all_datasets, country, start_time, end_time)
