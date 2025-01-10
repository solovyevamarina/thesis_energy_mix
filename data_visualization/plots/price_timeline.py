import pandas as pd
import numpy as np

import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import gc


def generate_price_timeline_plot(a_dataset, country, s_time, e_time, country_configs):
    # Generate the save path with the country name and time range
    save_path = f"plots/price_timeline_plot_{country}_{s_time[:4]}_{e_time[:4]}.jpg"

    # Get the dataset for the specified country and time range
    file_name = f"{country}_{s_time}_{e_time}"
    dataset = a_dataset[file_name].copy()

    # Extract years from start_time and end_time
    start_year = int(s_time[:4])  # First 4 characters of s_time
    end_year = int(e_time[:4])  # First 4 characters of e_time

    # Convert 'Date' column to datetime
    dataset['Date'] = pd.to_datetime(dataset['Date'])

    # Create 'Year' and 'Month' columns only if they do not already exist
    if 'Year' not in dataset.columns:
        dataset['Year'] = dataset['Date'].dt.year
    if 'Month' not in dataset.columns:
        dataset['Month'] = dataset['Date'].dt.month

    # Calculate yearly averages for 'Price'
    GR_y_avg = dataset[['Year', 'Price']].groupby('Year')['Price'].mean().reset_index()

    # Move yearly averages to the middle of each year, except for first and last years
    GR_y_avg['Date'] = pd.to_datetime(GR_y_avg['Year'].astype(str) + '-06-30')
    GR_y_avg.loc[GR_y_avg['Year'] == start_year, 'Date'] = pd.to_datetime(f"{start_year}-01-01")
    GR_y_avg.loc[GR_y_avg['Year'] == end_year, 'Date'] = pd.to_datetime(f"{end_year}-12-31")

    # Calculate monthly averages
    GR_ym_avg = (
        dataset[['Year', 'Month', 'Price']]
        .groupby(['Year', 'Month'])['Price']
        .mean()
        .reset_index()
    )
    GR_ym_avg['Date'] = pd.to_datetime(GR_ym_avg[['Year', 'Month']].assign(Day=1))

    # Prepare data for plotting
    xs = dataset['Date']
    series1 = np.array(dataset['Price']).astype(np.double)
    s1mask = np.isfinite(series1)

    series2 = np.array(GR_ym_avg['Price']).astype(np.double)
    s2mask = np.isfinite(series2)

    series3 = np.array(GR_y_avg['Price']).astype(np.double)
    s3mask = np.isfinite(series3)

    # Plotting the timeline
    fig, ax = plt.subplots(figsize=(12, 8))
    plt.plot(xs[s1mask], series1[s1mask], linestyle='-', color='gold', label='Ωριαίες Τιμές')
    plt.plot(GR_ym_avg['Date'][s2mask], series2[s2mask], linestyle='-', color='darkorange',
             label='Μηνιαίες Τιμές (κατά μέσο όρο)')
    plt.plot(GR_y_avg['Date'][s3mask], series3[s3mask], linestyle='-', color='red', linewidth=2,
             label='Ετήσιες Τιμές (κατά μέσο όρο)')

    plt.title(
        label=f"Η Χρονοσειρά της Οριακής Τιμής Συστήματος στην {country_configs[country]['country_name'][0]} {start_year}-{end_year}")
    plt.xlabel('Έτος')
    plt.ylabel('€ / MWh')
    plt.legend()

    # Set x-ticks to show each year
    years = pd.date_range(start=f'{start_year}-01-01', end=f'{end_year}-01-01', freq='YS')
    ax.set_xticks(years)
    ax.set_xticklabels([str(year.year) for year in years], rotation=0)

    # Save the plot as a JPG file
    plt.savefig(save_path, format='jpg', dpi=300)
    plt.close()
    gc.collect()
