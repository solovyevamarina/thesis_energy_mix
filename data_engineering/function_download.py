import pandas as pd
import os.path
from entsoe import EntsoePandasClient


def download_function(country, timezone, s_time, e_time, d_dataset, path, api_key):
    client = EntsoePandasClient(api_key=api_key)

    # Transform dates to timestamps
    start_timestamp = pd.Timestamp(s_time, tz=timezone)
    end_timestamp = pd.Timestamp(e_time, tz=timezone)

    # ---------------------------------------------------- Energy generation
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
        d_dataset[file_name_gen] = pd.read_csv(file_path)

    # ---------------------------------------------------- Energy prices
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
            d_dataset[file_name_price] = pd.read_csv(file_path)

        else:
            price_df = client.query_day_ahead_prices(country, start=start_timestamp, end=end_timestamp)
            price_df.to_csv(path + '/' + country + '_price_' + s_time + '_' + e_time + '.csv')
            print('Finish downloading energy price data', country, s_time, '-', e_time)
            d_dataset[file_name_price] = pd.read_csv(file_path)

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
            load_df = pd.DataFrame()
            for zone in se_zones:
                load_df_zone = client.query_load(zone, start=start_timestamp, end=end_timestamp)
                load_df = pd.concat([load_df, load_df_zone], axis=1)
            load_df = load_df.sum(axis='columns')
            load_df.to_csv(path + '/' + country + '_load_' + s_time + '_' + e_time + '.csv')
            print('Finish downloading energy load data', country, s_time, '-', e_time)
            d_dataset[file_name_load] = pd.read_csv(file_path)

        else:
            load_df = client.query_load(country, start=start_timestamp, end=end_timestamp)
            load_df.to_csv(path + '/' + country + '_load_' + s_time + '_' + e_time + '.csv')
            print('Finish downloading energy load data', country, s_time, '-', e_time)
            d_dataset[file_name_load] = pd.read_csv(file_path)

        # ---------------------------------------------------- Energy flows
        file_name_flow = f"{country}_flow_{start_timestamp.strftime('%Y%m%d')}_{end_timestamp.strftime('%Y%m%d')}"
        file_path = path + '/' + file_name_flow + '.csv'
        file_already_downloaded = os.path.isfile(file_path)

        if file_already_downloaded:
            print('Already downloaded', file_name_flow)
            d_dataset[file_name_flow] = pd.read_csv(file_path)

        else:
            print('Start downloading energy flow data', country, s_time, '-', e_time)
            flow_partners = []

            if country == 'GR':
                flow_partners = ['AL', 'BG', 'IT', 'TR', 'MK']
            elif country == 'PL':
                flow_partners = ['CZ', 'DE', 'LT', 'SK', 'SE', 'UA']
            elif country == 'SE':
                flow_partners = ['DK', 'FI', 'DE', 'LT', 'NO', 'PL']

            flow_df = pd.DataFrame()
            for partner in flow_partners:
                flow_in = \
                    client.query_crossborder_flows(country, partner, start=start_timestamp, end=end_timestamp)
                flow_out = \
                    client.query_crossborder_flows(partner, country, start=start_timestamp, end=end_timestamp)
                flow_df = pd.concat([flow_df, (flow_in - flow_out).fillna(0).rename(partner)], axis=1)

                flow_df = flow_df.sum(axis='columns')
                flow_df.to_csv(path + '/' + country + '_flow_' + s_time + '_' + e_time + '.csv')
                print('Finish downloading energy flow data', country, s_time, '-', e_time)
                d_dataset[file_name_flow] = pd.read_csv(file_path)

        # TTF prices already exist in the folder

    return d_dataset
