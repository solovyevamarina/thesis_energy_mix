import pandas as pd


def clean_columns(file_name_gen, file_name_price, file_name_load, file_name_flow, raw_datasets):

    # Energy generation
    gen_db = raw_datasets[file_name_gen]
    gen_db.rename(columns={'Unnamed: 0': 'Datetime'}, inplace=True)

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
        gen_db['Hydro'] = gen_db['Hydro Pumped Storage'] +\
                          gen_db['Hydro Water Reservoir'] +\
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
        else:
            continue

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

    return raw_datasets


def data_cleaning_function(country,  s_time, e_time, timezone, d_dataset, a_dataset):

    # Unite generation, prices and load in one dataset
    file_name = f"{country}_{s_time}_{e_time}"
    file_name_gen = f"{country}_gen_{s_time}_{e_time}"
    file_name_price = f"{country}_price_{s_time}_{e_time}"
    file_name_load = f"{country}_load_{s_time}_{e_time}"
    file_name_flow = f"{country}_flow_{s_time}_{e_time}"

    c_dataset = clean_columns(file_name_gen, file_name_price, file_name_load, file_name_flow, d_dataset)

    start_timestamp = pd.Timestamp(s_time, tz=timezone)
    end_timestamp = pd.Timestamp(e_time, tz=timezone)

    all_db = pd.DataFrame()
    all_db['Datetime'] = pd.date_range(start=start_timestamp, end=end_timestamp, freq='H')[0:-1].astype(str)

    all_db = pd.merge(all_db, c_dataset[file_name_gen].copy(), on='Datetime', how='left')
    all_db = pd.merge(all_db, c_dataset[file_name_price].copy(), on='Datetime', how='left')
    all_db = pd.merge(all_db, c_dataset[file_name_load].copy(), on='Datetime', how='left')
    all_db = pd.merge(all_db, c_dataset[file_name_flow].copy(), on='Datetime', how='left')
    all_db.drop_duplicates(subset='Datetime', keep="last")

    # Missing values handling
    for n in list(all_db.columns):
        all_db[n] = all_db[n].interpolate()
        all_db[n] = all_db[n].fillna(0)
        continue
    all_db['Price'] = all_db['Price'].fillna(method='bfill')

    # Recalculate sum:
    all_db['Sum'] = all_db[list(all_db.columns)[1:-3]].sum(axis=1)

    # Combine in a dataset
    a_dataset[file_name] = all_db.copy()

    return a_dataset
