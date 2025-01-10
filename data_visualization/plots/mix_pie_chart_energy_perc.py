import pandas as pd
import numpy as np

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import gc

def generate_energy_mix_pie_chart(country_data, country, s_time, e_time, country_configs):

    save_path = f"plots/energy_mix_pie_chart_{country}_{s_time[:4]}_{e_time[:4]}.jpg"
    # Get the configuration for the specified country
    if country not in country_configs:
        raise ValueError(f"No configuration found for country: {country}")

    config = country_configs[country]
    energy_sources = config['sources']
    labels = config['labels']
    colors = config['colors']

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
    plt.title(label=f"Πηγές Παραγωγής Ηλεκτρισμού στην {country_configs[country]['country_name'][0]} {s_time[:4]}-{e_time[:4]}")

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
    gc.collect()


def calculate_yearly_energy_percentages(country_data, country, s_time, e_time, country_configs):
    save_path = f"plots/yearly_energy_percentages_{country}_{s_time[:4]}_{e_time[:4]}.csv"

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

        # Extract data for the current year
        country_data['Year'] = country_data['Year'].astype(int)
        year_data = country_data[country_data['Year'] == year][energy_sources].mean(axis=0)

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

    # Convert to DataFrame and save
    yearly_df = pd.DataFrame(yearly_data)
    yearly_df.to_csv(save_path, index=False, encoding='utf-8')

    return
