import pandas as pd

# Rename columns
country = 'PL'
s_time = '20150101'
e_time = '20221101'
file_name_gen = f"{country}_gen_{s_time}_{e_time}"


def clean_gen_columns(file_name_gen, raw_datasets):

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

    sources_list = gen_db.columns[1:]
    gen_db['Sum'] = gen_db[sources_list].sum(axis=1)

    return raw_datasets


clean_gen_datasets = clean_gen_columns(file_name_gen, raw_datasets)

