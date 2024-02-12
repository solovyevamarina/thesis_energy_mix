import pandas as pd
import os.path
from entsoe import EntsoePandasClient


def entsoe_download(country, start, end, api_key, path):

    # Download the data for specific country for a specific time period
    # It takes quite some time

    client = EntsoePandasClient(api_key=api_key)
    gen_df = client.query_generation(country, start=start, end=end)
    gen_df.to_csv(path + '/' + country + '_raw_' + start + '_' + end + '.csv')

    return


def download_data(country, timezone, s_time, e_time, d_dataset, path, api_key):

    # Transform dates to timestamps
    start_timestamp = pd.Timestamp(s_time, tz=timezone)
    end_timestamp = pd.Timestamp(e_time, tz=timezone)

    # Set main name of dataset (country - type - start - end)
    variable_name = f"{country}_raw_{start_timestamp.strftime('%Y%m%d')}_{end_timestamp.strftime('%Y%m%d')}"

    # Downloading takes quite some time, so first check if it is already downloaded
    file_path = path + '/' + variable_name + '.csv'
    file_already_downloaded = os.path.isfile(file_path)

    if file_already_downloaded:  # if already downloaded, read it and put into dictionary
        print('Already downloaded', country, s_time, '-', e_time)
        d_dataset[variable_name] = pd.read_csv(file_path)
        print('Ready', country, s_time, '-', e_time)
    else:  # otherwise, download, save in csv, read it and put into dictionary
        print('Start downloading', country, s_time, '-', e_time)
        entsoe_download(country, start_timestamp, end_timestamp, api_key, path)
        print('Finished downloading', country, s_time, '-', e_time)
        d_dataset[variable_name] = pd.read_csv(file_path)
        print('Ready', country, s_time, '-', e_time)

    return d_dataset
