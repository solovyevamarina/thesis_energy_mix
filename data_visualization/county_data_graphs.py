import pandas as pd
import numpy as np

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt


country_configs = {
    'GR': {
        'sources': ['Coal', 'Gas', 'Oil', 'Solar', 'Wind', 'Hydro'],
        'labels': ('Λινίτης', 'Φυσικό Αέριο', 'Πετρέλαιο', 'Φωτοβολταϊκά', 'Αιολικά', 'Ύδροηλεκτρικά'),
        'colors': ['brown', 'teal', 'black', 'yellow', 'skyblue', 'blue'],
        'fossil_sources': ['Coal', 'Gas', 'Oil'],
        'renewable_sources': ['Solar', 'Wind', 'Hydro']
    },
    'PL': {
        'sources': ['Biomass', 'Coal', 'Hard Coal', 'Coal Gas', 'Gas', 'Oil', 'Solar', 'Wind', 'Hydro'],
        'labels': ('Βιομάζα', 'Λινίτης', 'Άνθρακας', 'Ανθρακαέριο', 'Φυσικό Αέριο', 'Πετρέλαιο', 'Φωτοβολταϊκά', 'Αιολικά', 'Ύδροηλεκτρικά'),
        'colors': ['olive', 'brown', 'dimgray', 'slategrey', 'teal', 'black', 'yellow', 'skyblue', 'blue'],
        'fossil_sources': ['Coal', 'Hard Coal', 'Coal Gas', 'Gas', 'Oil'],
        'renewable_sources': ['Biomass', 'Hydro', 'Solar', 'Wind']
    },
    'SE': {
        'sources': ['Gas', 'Nuclear', 'Hydro', 'Solar', 'Wind', 'Other'],
        'labels': ('Φυσικό Αέριο', 'Πυρηνικά', 'Ύδροηλεκτρικά', 'Φωτοβολταϊκά', 'Αιολικά', 'Λοιπά ΑΕΠ'),
        'colors': ['teal', 'purple', 'blue', 'yellow', 'skyblue', 'gray'],
        'fossil_sources': ['Gas'],
        'renewable_sources': ['Hydro', 'Solar', 'Wind', 'Other']
    }
}


def generate_energy_mix_pie_chart(dataset, country, s_time, e_time, save_path='energy_mix_pie_chart.jpg'):

    # Get the configuration for the specified country
    if country not in country_configs:
        raise ValueError(f"No configuration found for country: {country}")

    config = country_configs[country]
    energy_sources = config['sources']
    labels = config['labels']
    colors = config['colors']

    # Extract data for the specified country and time period
    file_name = f"{country}_{s_time}_{e_time}"
    country_data = dataset[file_name].copy()

    # Calculate mean shares of energy sources
    mean_share = country_data[energy_sources].mean(axis=0)

    # Calculate total shares for fossil fuels and renewables
    fossil_sources = config.get('fossil_sources', [])
    renewable_sources = config.get('renewable_sources', [])

    all_fossil = sum(mean_share.loc[source] for source in fossil_sources if source in mean_share)
    all_renewable = sum(mean_share.loc[source] for source in renewable_sources if source in mean_share)
    total = all_fossil + all_renewable

    share_summary = {
        'All Fossil': (all_fossil / total) * 100,
        'All Renewables': (all_renewable / total) * 100,
    }

    # Plot the pie chart
    plt.figure(figsize=(10, 8))
    plt.pie(mean_share, labels=labels, labeldistance=1.15,
            wedgeprops={'linewidth': 1.5, 'edgecolor': 'white'}, autopct='%1.1f%%',
            colors=colors)
    plt.title(label=f"Πηγές Παραγωγής Ηλεκτρισμού {country} {s_time[:4]}-{e_time[:4]}")

    # Add text annotations for totals
    plt.text(-1.5, -1.3, 'Σύνολο από μη-ΑΠΕ:', fontsize=12)
    plt.text(-1.25, -1.5, f"{share_summary['All Fossil']:.1f}%", fontweight='bold', fontsize=12)
    plt.text(-1.4, -1.4, '                          ', bbox={'facecolor': 'red', 'alpha': 0.3, 'pad': 36})

    plt.text(0.6, -1.3, 'Σύνολο από ΑΠΕ:', fontsize=12)
    plt.text(0.85, -1.5, f"{share_summary['All Renewables']:.1f}%", fontweight='bold', fontsize=12)
    plt.text(0.7, -1.4, '                     ', bbox={'facecolor': 'green', 'alpha': 0.3, 'pad': 36})

    # Save the chart
    plt.savefig(save_path, format='jpg', dpi=300)
    plt.close()


def calculate_yearly_energy_percentages(dataset, country, s_time, e_time, country_configs):

    # Validate country configuration
    if country not in country_configs:
        raise ValueError(f"No configuration found for country: {country}")

    config = country_configs[country]
    energy_sources = config['sources']
    fossil_sources = config.get('fossil_sources', [])
    renewable_sources = config.get('renewable_sources', [])

    # Parse years from s_time and e_time
    start_year = int(s_time[:4])
    end_year = int(e_time[:4])

    # Initialize a list to store yearly data
    yearly_data = []

    # Loop through each year in the range
    for year in range(start_year, end_year + 1):
        file_name = f"{country}_{s_time}_{e_time}"
        if file_name not in dataset:
            continue  # Skip if the data for the year is missing

        # Extract data for the current year
        dataset[file_name]['Year'] = dataset[file_name]['Year'].astype(int)
        year_data = dataset[file_name][dataset[file_name]['Year'] == year][energy_sources].mean(axis=0)


        # Calculate fossil and renewable shares
        all_fossil = sum(year_data.loc[source] for source in fossil_sources if source in year_data)
        all_renewable = sum(year_data.loc[source] for source in renewable_sources if source in year_data)
        total = all_fossil + all_renewable

        # Calculate percentages
        fossil_percentage = (all_fossil / total) * 100 if total > 0 else 0
        renewable_percentage = (all_renewable / total) * 100 if total > 0 else 0

        # Append yearly data
        yearly_data.append({
            'Έτος': year,
            'Μη-ΑΠΕ': round(fossil_percentage, 1),
            'ΑΠΕ': round(renewable_percentage, 1),
        })

    # Convert to DataFrame
    yearly_df = pd.DataFrame(yearly_data)
    return yearly_df


def generate_energy_stack_plot(dataset, country, s_time, e_time, save_path='energy_stack_plot.jpg'):

    # Get the configuration for the specified country
    if country not in country_configs:
        raise ValueError(f"No configuration found for country: {country}")

    config = country_configs[country]
    energy_sources = config['sources']
    labels = config['labels']
    colors = config['colors']

    # Extract data for the specified country and time period
    file_name = f"{country}_{s_time}_{e_time}"
    if file_name not in dataset:
        raise ValueError(f"Dataset does not contain file: {file_name}")

    country_data = dataset[file_name].copy()

    # Group by year and calculate the mean for each energy source
    yearly_avg = country_data.groupby('Year')[energy_sources].mean().reset_index()

    # Plotting the stack plot
    fig, ax = plt.subplots(figsize=(16, 8))
    plt.stackplot(
        yearly_avg['Year'], *[yearly_avg[source] for source in energy_sources],
        baseline='zero', colors=colors, labels=labels
    )

    # Adding titles, labels, and legend
    plt.legend(loc='lower left', title='Energy Sources')
    plt.title(label=f"Πηγές Παραγωγής Ηλεκτρισμού {country} {s_time[:4]}-{e_time[:4]}")
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

    plt.title(label=f"Η Χρονοσειρά της Συνολικής Παραγωγής Ηλεκτρισμού στην {country} {start_year}-{end_year}")
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


def generate_price_timeline_plot(a_dataset, country, s_time, e_time, save_path='price_timeline_plot.jpg'):
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
    plt.plot(GR_ym_avg['Date'][s2mask], series2[s2mask], linestyle='-', color='darkorange', label='Μηνιαίες Τιμές (κατά μέσο όρο)')
    plt.plot(GR_y_avg['Date'][s3mask], series3[s3mask], linestyle='-', color='red', linewidth=2, label='Ετήσιες Τιμές (κατά μέσο όρο)')

    plt.title(label=f"Η Χρονοσειρά της Οριακής Τιμής Συστήματος στην Ελλάδα {start_year}-{end_year}")
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
