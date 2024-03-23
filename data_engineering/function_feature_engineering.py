import pandas as pd

# from data_engineering.function_download import download_function
# from data_engineering.function_data_cleaning import data_cleaning_function
# country = 'GR'
# timezone = 'Europe/Athens'
# s_time = '20150101'
# e_time = '20221101'
# my_api_key = '611caff8-769f-4d12-8a5e-838efb1f684a'
# my_path = 'E:/Study/Diploma/csv'
# raw_datasets = {}
# a_dataset = {}
# download_function(country, timezone, s_time, e_time, raw_datasets, my_path, my_api_key)
# data_cleaning_function(country, s_time, e_time, timezone, raw_datasets, a_dataset)


def feature_engineering(a_dataset, country, s_time, e_time):
    file_name = f"{country}_{s_time}_{e_time}"
    db_all = a_dataset[file_name].copy()

    # ---------------------------------------------------- Time transformations
    db_all['Datetime'] = db_all['Datetime'].str.split('+', n=1, expand=True)[0]

    db_all['Date'] = db_all['Datetime'].str.split(' ', n=1, expand=True)[0]
    db_all['Weekday'] = pd.to_datetime(db_all['Datetime']).dt.strftime('%A')
    db_all[['Year', 'Month', 'Day']] = db_all['Date'].str.split('-', n=2, expand=True)
    db_all['Hour'] = (db_all['Datetime'].str.split(' ', n=1, expand=True)[1]).str.split(':', n=2, expand=True)[0]

    # ---------------------------------------------------- Holidays
    fixed_holidays = []
    moving_holidays = []
    if country == 'GR':
        fixed_holidays = ['01-01', '01-06', '03-25', '05-01', '09-15', '10-28', '12-25', '12-26']
        moving_holidays = ['2015-02-23', '2015-04-10', '2015-04-11', '2015-04-12', '2015-04-13', '2015-06-01',
                           '2016-03-14', '2016-04-29', '2016-04-30', '2016-05-01', '2016-05-02', '2016-06-20',
                           '2017-02-27', '2017-04-14', '2017-04-15', '2017-04-16', '2017-04-17', '2017-06-05',
                           '2018-02-19', '2018-04-06', '2018-04-07', '2018-04-08', '2018-04-09', '2018-05-28',
                           '2019-03-11', '2019-04-26', '2019-04-27', '2019-04-28', '2019-04-29', '2019-06-17',
                           '2020-03-02', '2020-04-17', '2020-04-18', '2020-04-19', '2020-04-20', '2020-06-08',
                           '2021-03-15', '2021-04-28', '2021-05-01', '2021-05-02', '2021-05-03', '2021-06-21',
                           '2021-03-07', '2022-04-22', '2022-04-23', '2022-04-24', '2022-04-25', '2022-06-13']
    elif country == 'PL':
        fixed_holidays = ['01-01', '01-06', '05-01', '05-03', '08-15', '11-01', '11-11', '12-25', '12-26']
        moving_holidays = ['2015-04-05', '2015-04-06', '2015-05-24', '2015-06-04',
                           '2016-03-27', '2016-03-28', '2016-05-15', '2016-05-26',
                           '2017-04-16', '2017-04-17', '2017-06-04', '2017-06-15',
                           '2018-04-01', '2018-04-02', '2018-05-20', '2018-05-31',
                           '2019-04-21', '2019-04-22', '2019-06-09', '2019-06-20',
                           '2020-04-12', '2020-04-13', '2020-05-31', '2020-06-11',
                           '2021-04-04', '2021-04-05', '2021-05-23', '2021-06-06',
                           '2021-04-17', '2022-04-18', '2022-06-05', '2022-06-16']
    elif country == 'SE':
        fixed_holidays = ['01-01', '01-06', '03-25', '05-01', '09-15', '10-28', '12-25', '12-26']
        moving_holidays = ['2015-02-23', '2015-04-10', '2015-04-11', '2015-04-12', '2015-04-13', '2015-06-01',
                           '2016-03-14', '2016-04-29', '2016-04-30', '2016-05-01', '2016-05-02', '2016-06-20',
                           '2017-02-27', '2017-04-14', '2017-04-15', '2017-04-16', '2017-04-17', '2017-06-05',
                           '2018-02-19', '2018-04-06', '2018-04-07', '2018-04-08', '2018-04-09', '2018-05-28',
                           '2019-03-11', '2019-04-26', '2019-04-27', '2019-04-28', '2019-04-29', '2019-06-17',
                           '2020-03-02', '2020-04-17', '2020-04-18', '2020-04-19', '2020-04-20', '2020-06-08',
                           '2021-03-15', '2021-04-28', '2021-05-01', '2021-05-02', '2021-05-03', '2021-06-21',
                           '2021-03-07', '2022-04-22', '2022-04-23', '2022-04-24', '2022-04-25', '2022-06-13']

    db_all['Holiday'] = \
        (db_all[['Month', 'Day']].astype(str).apply('-'.join, axis=1).isin(fixed_holidays) |
         db_all[['Year', 'Month', 'Day']].astype(str).apply('-'.join, axis=1).isin(moving_holidays)).astype(int)

    # Combine in a dataset
    a_dataset[file_name] = db_all.copy()

    return a_dataset
