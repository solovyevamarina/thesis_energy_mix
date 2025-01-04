import pandas as pd
import holidays
from data_engineering.function_download import download_function
from data_engineering.function_data_cleaning import data_cleaning_function


def feature_engineering(a_dataset, country, s_time, e_time):
    file_name = f"{country}_{s_time}_{e_time}"
    db_all = a_dataset[file_name].copy()

    # ---------------------------------------------------- Time transformations
    db_all['Datetime'] = db_all['Datetime'].str.split('+', n=1, expand=True)[0]

    db_all['Date'] = db_all['Datetime'].str.split(' ', n=1, expand=True)[0]
    db_all['Weekday'] = pd.to_datetime(db_all['Datetime']).dt.strftime('%A')
    db_all[['Year', 'Month', 'Day']] = db_all['Date'].str.split('-', n=2, expand=True)
    db_all['Hour'] = (db_all['Datetime'].str.split(' ', n=1, expand=True)[1]).str.split(':', n=2, expand=True)[0]

    c_holidays = holidays.country_holidays(country)
    def is_holiday(date):
        return int(date in c_holidays)

    db_all['Holiday'] = db_all['Date'].apply(is_holiday)

    a_dataset[file_name] = db_all.copy()

    return a_dataset
