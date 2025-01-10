import pandas as pd


def clean_columns(file_name_gen, file_name_price, file_name_load, file_name_flow, file_name_ttf, raw_datasets, timezone):
    # Energy generation
    gen_db = raw_datasets[file_name_gen]
    gen_db.rename(columns={'Unnamed: 0': 'Datetime'}, inplace=True)

    # Renaming columns for energy sources
    if 'Fossil Brown coal/Lignite' in gen_db.columns:
        gen_db.rename(columns={'Fossil Brown coal/Lignite': 'Coal'}, inplace=True)
    if 'Fossil Coal-derived gas' in gen_db.columns:
        gen_db.rename(columns={'Fossil Coal-derived gas': 'Coal Gas'}, inplace=True)
    if 'Fossil Gas' in gen_db.columns:
        gen_db.rename(columns={'Fossil Gas': 'Gas'}, inplace=True)
    if 'Fossil Hard coal' in gen_db.columns:
        gen_db.rename(columns={'Fossil Hard coal': 'Hard Coal'}, inplace=True)
    if 'Fossil Oil' in gen_db.columns:
        gen_db.rename(columns={'Fossil Oil': 'Oil'}, inplace=True)
    if 'Hydro Pumped Storage' in gen_db.columns \
            and 'Hydro Water Reservoir' in gen_db.columns \
            and 'Hydro Run-of-river and poundage' in gen_db.columns:
        gen_db['Hydro'] = gen_db['Hydro Pumped Storage'] + \
                          gen_db['Hydro Water Reservoir'] + \
                          gen_db['Hydro Run-of-river and poundage']
        del gen_db['Hydro Pumped Storage']
        del gen_db['Hydro Water Reservoir']
        del gen_db['Hydro Run-of-river and poundage']
    if 'Hydro Pumped Storage' in gen_db.columns \
            and 'Hydro Water Reservoir' in gen_db.columns:
        gen_db['Hydro'] = gen_db['Hydro Pumped Storage'] + \
                          gen_db['Hydro Water Reservoir']
        del gen_db['Hydro Pumped Storage']
        del gen_db['Hydro Water Reservoir']
    if 'Hydro Water Reservoir' in gen_db.columns:
        gen_db.rename(columns={'Hydro Water Reservoir': 'Hydro'}, inplace=True)
    if 'Wind Onshore' in gen_db.columns:
        gen_db.rename(columns={'Wind Onshore': 'Wind'}, inplace=True)

    # Remove empty sources
    for c in gen_db.columns:
        if gen_db[c].notna().mean() < 0.1:
            del gen_db[c]

    sources_list = gen_db.columns[1:]
    gen_db['Sum'] = gen_db[sources_list].sum(axis=1)

    # Energy prices
    price_db = raw_datasets[file_name_price]
    price_db.rename(columns={'Unnamed: 0': 'Datetime'}, inplace=True)
    price_db.rename(columns={'0': 'Price'}, inplace=True)

    # Energy load
    load_db = raw_datasets[file_name_load]
    load_db.rename(columns={'Unnamed: 0': 'Datetime'}, inplace=True)
    if '0' in load_db.columns:
        load_db.rename(columns={'0': 'Load'}, inplace=True)
    if 'Actual Load' in load_db.columns:
        load_db.rename(columns={'Actual Load': 'Load'}, inplace=True)

    # Energy flow
    flow_db = raw_datasets[file_name_flow]
    flow_db.rename(columns={'Unnamed: 0': 'Datetime'}, inplace=True)
    flow_db.rename(columns={'0': 'Flow'}, inplace=True)

    # Convert 'Datetime' column in flow_db from UTC to Europe/Athens (UTC+2)
    flow_db['Datetime'] = pd.to_datetime(flow_db['Datetime'])  # Ensure it's datetime
    flow_db['Datetime'] = flow_db['Datetime'].dt.tz_convert('UTC').dt.tz_localize(None)  # Remove timezone info
    flow_db['Datetime'] = flow_db['Datetime'].dt.tz_localize('UTC').dt.tz_convert(timezone)  # Convert to UTC+2
    flow_db['Datetime'] = flow_db['Datetime'].astype(str)

    # TTF (Gas Prices)
    ttf_db = raw_datasets[file_name_ttf]
    ttf_db.rename(columns={'Date': 'Datetime'}, inplace=True)
    ttf_db['Datetime'] = pd.to_datetime(ttf_db['Datetime'], format='%d.%m.%Y')  # Convert to datetime
    ttf_db = ttf_db.drop_duplicates(subset='Datetime')  # Remove duplicate rows based on Datetime
    ttf_db.set_index('Datetime', inplace=True)  # Set Datetime as the index
    ttf_db = ttf_db.resample('H').ffill().reset_index()  # Resample hourly and forward-fill missing values
    ttf_db['Datetime'] = ttf_db['Datetime'].dt.tz_localize('UTC').dt.tz_convert(timezone)  # Match timezone
    ttf_db['Datetime'] = ttf_db['Datetime'].astype(str)  # Convert to string to match all_db
    ttf_db = ttf_db.drop(columns=['Unnamed: 0'])

    # Merge TTF back into raw_datasets
    raw_datasets[file_name_ttf] = ttf_db

    return raw_datasets


def data_cleaning_function(country, start_time, end_time, timezone, raw_datasets, all_datasets, country_configs):
    # File names for datasets
    file_name = f"{country}_{start_time}_{end_time}"
    file_name_gen = f"{country}_gen_{start_time}_{end_time}"
    file_name_price = f"{country}_price_{start_time}_{end_time}"
    file_name_load = f"{country}_load_{start_time}_{end_time}"
    file_name_flow = f"{country}_flow_{start_time}_{end_time}"
    file_name_ttf = f"TTF_{start_time}_{end_time}"

    # Clean datasets
    c_dataset = clean_columns(file_name_gen, file_name_price, file_name_load, file_name_flow, file_name_ttf, raw_datasets, timezone)

    # Define the time range
    start_timestamp = pd.Timestamp(start_time, tz=timezone)
    end_timestamp = pd.Timestamp(end_time, tz=timezone)

    # Create a base DataFrame with hourly time intervals
    all_db = pd.DataFrame()
    all_db['Datetime'] = pd.date_range(start=start_timestamp, end=end_timestamp, freq='h')[0:-1].astype(str)

    # Merge data
    all_db = pd.merge(all_db, c_dataset[file_name_gen].copy(), on='Datetime', how='left')
    all_db = pd.merge(all_db, c_dataset[file_name_price].copy(), on='Datetime', how='left')
    all_db = pd.merge(all_db, c_dataset[file_name_load].copy(), on='Datetime', how='left')
    all_db = pd.merge(all_db, c_dataset[file_name_flow].copy(), on='Datetime', how='left')
    all_db = pd.merge(all_db, c_dataset[file_name_ttf].copy(), on='Datetime', how='left')
    all_db.drop_duplicates(subset='Datetime', keep="last")

    # Fill missing values
    for n in list(all_db.columns):
        all_db[n] = all_db[n].infer_objects(copy=False)
        all_db[n] = all_db[n].bfill()
        all_db[n] = all_db[n].ffill()
        all_db[n] = all_db[n].fillna(0)

    # Get specific sources from country_configs
    config = country_configs.get(country, {})
    sources = config.get('sources', [])

    # Calculate sum for energy sources
    if sources:
        all_db['Sum'] = all_db[sources].sum(axis=1)

    # Combine into the dataset
    all_datasets[file_name] = all_db.copy()

    return all_datasets