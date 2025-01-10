import pandas as pd
import holidays
from data_engineering.function_download import download_function
from data_engineering.function_data_cleaning import data_cleaning_function


def feature_engineering(a_dataset, country, s_time, e_time, country_configs):
    file_name = f"{country}_{s_time}_{e_time}"
    db_all = a_dataset[file_name].copy()

    # ---------------------------------------------------- Time transformations
    db_all['Datetime'] = db_all['Datetime'].str.split('+', n=1, expand=True)[0]

    db_all['Date'] = db_all['Datetime'].str.split(' ', n=1, expand=True)[0]
    db_all['Weekday'] = pd.to_datetime(db_all['Datetime']).dt.strftime('%A')
    db_all[['Year', 'Month', 'Day']] = db_all['Date'].str.split('-', n=2, expand=True)
    db_all['Hour'] = (db_all['Datetime'].str.split(' ', n=1, expand=True)[1]).str.split(':', n=2, expand=True)[0]

    # Add Year-Month column
    db_all['Year-Month'] = db_all['Year'] + '-' + db_all['Month']

    # ---------------------------------------------------- Add holidays
    c_holidays = holidays.country_holidays(country)

    def is_holiday(date):
        return int(date in c_holidays)

    db_all['Holiday'] = db_all['Date'].apply(is_holiday)

    # ---------------------------------------------------- Calculate Gas_Price
    if 'TTF' in db_all.columns and 'Gas' in db_all.columns:
        db_all['Gas_Price'] = db_all['TTF'] * db_all['Gas']
    else:
        raise KeyError("Columns 'TTF' and 'Gas' are required to calculate 'Gas_Price'.")

    # ---------------------------------------------------- Create dummies
    d_month = pd.get_dummies(db_all['Month'], prefix='Month')
    d_weekday = pd.get_dummies(db_all['Weekday'], prefix='Weekday')
    d_hour = pd.get_dummies(db_all['Hour'], prefix='Hour')

    db_all = pd.concat([db_all, d_month, d_weekday, d_hour], axis=1)

    # ---------------------------------------------------- Calculate shares
    if country not in country_configs:
        raise KeyError(f"Country {country} not found in country_configs.")

    sources = country_configs[country]['sources']
    for source in sources:
        if source in db_all.columns:
            db_all[f"{source}_share"] = db_all[source] / db_all['Sum']
        else:
            db_all[f"{source}_share"] = 0  # If the source doesn't exist in the data, set share to 0.

    # Save updated dataset
    a_dataset[file_name] = db_all.copy()

    return a_dataset
