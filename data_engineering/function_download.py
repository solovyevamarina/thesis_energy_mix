import pandas as pd
import os.path
from entsoe import EntsoePandasClient


def download_function(country, timezone, s_time, e_time, d_dataset, path, api_key):

    client = EntsoePandasClient(api_key=api_key)

    # Transform dates to timestamps
    start_timestamp = pd.Timestamp(s_time, tz=timezone)
    end_timestamp = pd.Timestamp(e_time, tz=timezone)

    #---------------------------------------------------- Energy generation
    file_name_gen = f"{country}_gen_{start_timestamp.strftime('%Y%m%d')}_{end_timestamp.strftime('%Y%m%d')}"
    file_path = path + '/' + file_name_gen + '.csv'
    file_already_downloaded = os.path.isfile(file_path)

    if file_already_downloaded:
        print('Already downloaded', file_name_gen)
        d_dataset[file_name_gen] = pd.read_csv(file_path)

    else:
        print('Start downloading energy generation data', country, s_time, '-', e_time)
        gen_df = client.query_generation(country, start=start_timestamp, end=end_timestamp)
        gen_df.to_csv(path + '/' + country + '_gen_' + s_time + '_' + e_time + '.csv')
        print('Finish downloading energy generation data', country, s_time, '-', e_time)

    #---------------------------------------------------- Energy prices
    file_name_price = f"{country}_price_{start_timestamp.strftime('%Y%m%d')}_{end_timestamp.strftime('%Y%m%d')}"
    file_path = path + '/' + file_name_price + '.csv'
    file_already_downloaded = os.path.isfile(file_path)

    if file_already_downloaded:
        print('Already downloaded', file_name_price)
        d_dataset[file_name_price] = pd.read_csv(file_path)

    else:
        print('Start downloading energy prices data', country, s_time, '-', e_time)

        if country == 'SE':
            se_zones = ['SE_1', 'SE_2', 'SE_3', 'SE_4']
            price_df = pd.DataFrame()
            for zone in se_zones:
                price_df_zone = client.query_day_ahead_prices(zone, start=start_timestamp, end=end_timestamp)
                price_df = pd.concat([price_df, price_df_zone], axis=1)
            price_df = price_df.sum(axis='columns')
            price_df.to_csv(path + '/' + country + '_price_' + s_time + '_' + e_time + '.csv')
            print('Finish downloading energy price data', country, s_time, '-', e_time)

        else:
            price_df = client.query_day_ahead_prices(country, start=start_timestamp, end=end_timestamp)
            price_df.to_csv(path + '/' + country + '_price_' + s_time + '_' + e_time + '.csv')
            print('Finish downloading energy price data', country, s_time, '-', e_time)

    # ---------------------------------------------------- Energy load
    file_name_load = f"{country}_load_{start_timestamp.strftime('%Y%m%d')}_{end_timestamp.strftime('%Y%m%d')}"
    file_path = path + '/' + file_name_load + '.csv'
    file_already_downloaded = os.path.isfile(file_path)

    if file_already_downloaded:
        print('Already downloaded', file_name_load)
        d_dataset[file_name_load] = pd.read_csv(file_path)

    else:
        print('Start downloading energy load data', country, s_time, '-', e_time)
        if country == 'SE':
            se_zones = ['SE_1', 'SE_2', 'SE_3', 'SE_4']
            price_df = pd.DataFrame()
            for zone in se_zones:
                price_df_zone = client.query_day_ahead_prices(zone, start=start_timestamp, end=end_timestamp)
                price_df = pd.concat([price_df, price_df_zone], axis=1)
            price_df = price_df.sum(axis='columns')
            price_df.to_csv(path + '/' + country + '_load_' + s_time + '_' + e_time + '.csv')
        else:
            price_df = client.query_day_ahead_prices(country, start=start_timestamp, end=end_timestamp)
            price_df.to_csv(path + '/' + country + '_load_' + s_time + '_' + e_time + '.csv')

        # TTF prices already exist in the folder

        print('Finished downloading', country, s_time, '-', e_time)

    return d_dataset
