import pandas as pd
import numpy as np

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt


def generate_energy_mix_pie_chart(a_dataset, country, s_time, e_time, save_path='energy_mix_pie_chart.jpg'):
    file_name = f"{country}_{s_time}_{e_time}"
    dataset = a_dataset[file_name].copy()

    # Extract relevant columns
    piges_list = ['Coal', 'Gas', 'Oil', 'Solar', 'Wind', 'Hydro']

    # Calculate mean shares
    GR_mean_share = dataset[piges_list].mean(axis=0)

    # Create DataFrame for all fossil and renewables
    GR_mean_share_all = pd.DataFrame(list(), index=('All Fossil', 'All Renewables'), columns=['1'])

    all_fossil = GR_mean_share.loc['Coal'] + GR_mean_share.loc['Gas'] + GR_mean_share.loc['Oil']
    all_renewable = GR_mean_share.loc['Hydro'] + GR_mean_share.loc['Solar'] + GR_mean_share.loc['Wind']
    all_all = all_fossil + all_renewable

    GR_mean_share_all.loc['All Fossil'] = (all_fossil / all_all) * 100
    GR_mean_share_all.loc['All Renewables'] = (all_renewable / all_all) * 100

    # Labels for the pie chart
    labels_greek = ('Λινίτης', 'Φυσικό Αέριο', 'Πετρέλαιο', 'Ύδροηλεκτρικά', 'Φωτοβολταϊκά', 'Αιολικά')

    # Plotting the pie chart
    plt.figure(figsize=(10, 8))
    plt.pie(GR_mean_share, labels=labels_greek, labeldistance=1.15,
            wedgeprops={'linewidth': 1.5, 'edgecolor': 'white'}, autopct='%1.1f%%',
            colors=['brown', 'teal', 'black', 'blue', 'yellow', 'skyblue'])
    plt.title(label=f"Πηγές Παραγωγής Ηλεκτρισμού στην Ελλάδα {s_time[:4]}-{e_time[:4]}")

    # Adding text annotations
    plt.text(-1.5, -1.3, 'Σύνολο από μη-ΑΠΕ:', fontsize=12)
    plt.text(-1.25, -1.5, f"{GR_mean_share_all.loc['All Fossil', '1'].round(1)}%", fontweight='bold', fontsize=12)
    plt.text(-1.4, -1.4, '                          ', bbox={'facecolor': 'red', 'alpha': 0.3, 'pad': 36})

    plt.text(0.6, -1.3, 'Σύνολο από ΑΠΕ:', fontsize=12)
    plt.text(0.85, -1.5, f"{GR_mean_share_all.loc['All Renewables', '1'].round(1)}%", fontweight='bold', fontsize=12)
    plt.text(0.7, -1.4, '                     ', bbox={'facecolor': 'green', 'alpha': 0.3, 'pad': 36})

    # Save the plot as a JPG file
    plt.savefig(save_path, format='jpg', dpi=300)
    plt.close()


def generate_energy_stack_plot(a_dataset, country, s_time, e_time, save_path='energy_stack_plot.jpg'):
    file_name = f"{country}_{s_time}_{e_time}"
    dataset = a_dataset[file_name].copy()

    # Extract relevant columns
    piges_list = ['Coal', 'Gas', 'Oil', 'Solar', 'Wind', 'Hydro']

    # Group by year and calculate the mean for each energy source
    GR_y_avg = dataset.groupby('Year')[piges_list].mean().reset_index()

    # Labels for the stack plot
    labels_greek = ('Λινίτης', 'Φυσικό Αέριο', 'Πετρέλαιο', 'Ύδροηλεκτρικά', 'Φωτοβολταϊκά', 'Αιολικά')

    # Plotting the stack plot
    fig, ax = plt.subplots(figsize=(16, 8))
    plt.stackplot(GR_y_avg['Year'], GR_y_avg['Coal'], GR_y_avg['Gas'], GR_y_avg['Oil'],
                  GR_y_avg['Hydro'], GR_y_avg['Solar'], GR_y_avg['Wind'],
                  baseline='zero', colors=['brown', 'teal', 'black', 'blue', 'yellow', 'skyblue'],
                  labels=labels_greek)

    plt.legend(loc='lower left')
    plt.title(label=f"Πηγές Παραγωγής Ηλεκτρισμού στην Ελλάδα {s_time[:4]}-{e_time[:4]}")
    plt.xlabel('Year')
    plt.ylabel('Average Production')

    # Save the plot as a JPG file
    plt.savefig(save_path, format='jpg', dpi=300)
    plt.close()


def generate_timeline_plot(a_dataset, country, s_time, e_time, save_path='timeline_plot.jpg'):
    file_name = f"{country}_{s_time}_{e_time}"
    dataset = a_dataset[file_name].copy()

    # Extract years from start_time and end_time
    start_year = int(s_time[:4])  # First 4 characters of s_time
    end_year = int(e_time[:4])    # First 4 characters of e_time

    # Convert 'Date' column to datetime
    dataset['Date'] = pd.to_datetime(dataset['Date'])

    # Extract 'Year' and 'Month' from 'Date'
    dataset['Year'] = dataset['Date'].dt.year
    dataset['Month'] = dataset['Date'].dt.month

    # Calculate yearly averages for 'Sum'
    GR_y_avg = dataset[['Year', 'Sum']].groupby('Year')['Sum'].mean().reset_index()

    # Adjust for leap years
    for year in GR_y_avg['Year']:
        days_in_year = 366 if pd.Timestamp(year=year, month=1, day=1).is_leap_year else 365
        GR_y_avg.loc[GR_y_avg['Year'] == year, 'Sum'] = GR_y_avg.loc[GR_y_avg['Year'] == year, 'Sum'].div(days_in_year * 24).round(2)

    # Calculate monthly averages
    GR_ym_avg = (
        dataset[['Year', 'Month', 'Sum']]
        .groupby(['Year', 'Month'])['Sum']
        .mean()
        .reset_index()
    )
    GR_ym_avg['Date'] = pd.to_datetime(GR_ym_avg[['Year', 'Month']].assign(Day=1))

    # Prepare data for plotting
    xs = dataset['Date']
    series1 = np.array(dataset['Sum']).astype(np.double)
    s1mask = np.isfinite(series1)

    series2 = np.array(GR_ym_avg['Sum']).astype(np.double)
    s2mask = np.isfinite(series2)

    series3 = np.array(GR_y_avg['Sum']).astype(np.double)
    s3mask = np.isfinite(series3)

    # Plotting the timeline
    fig, ax = plt.subplots(figsize=(12, 8))
    plt.plot(xs[s1mask], series1[s1mask], linestyle='-', label='Συνολική Ωριαία Παραγωγή')
    plt.plot(GR_ym_avg['Date'][s2mask], series2[s2mask], linestyle='-', label='Συνολική Μηνιαία Παραγωγή (κατά μέσο όρο)')
    plt.plot(pd.to_datetime(GR_y_avg['Year'], format='%Y')[s3mask], series3[s3mask], linestyle='-', color='yellow', linewidth=2, label='Συνολική Ετήσια Παραγωγή (κατά μέσο όρο)')

    plt.title(label=f"Η Χρονοσειρά της Συνολικής Παραγωγής Ηλεκτρισμού στην Ελλάδα {start_year}-{end_year}")
    plt.xlabel('Έτος')
    plt.ylabel('MW')
    plt.legend()

    # Set x-ticks to show each year
    years = pd.date_range(start=f'{start_year}-01-01', end=f'{end_year}-01-01', freq='YS')
    ax.set_xticks(years)
    ax.set_xticklabels([str(year.year) for year in years], rotation=0)

    # Save the plot as a JPG file
    plt.savefig(save_path, format='jpg', dpi=300)
    plt.close()
