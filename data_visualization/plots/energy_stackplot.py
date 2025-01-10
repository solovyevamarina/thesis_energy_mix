import pandas as pd
import numpy as np

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import gc

def generate_energy_stack_plot(dataset, country, s_time, e_time, country_configs):
    save_path = f"plots/energy_stack_plot_{country}_{s_time[:4]}_{e_time[:4]}.jpg"

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
    plt.title(
        label=f"Πηγές Παραγωγής Ηλεκτρισμού στην {country_configs[country]['country_name'][0]} {s_time[:4]}-{e_time[:4]}")
    plt.xlabel('Year')
    plt.ylabel('Average Production')

    # Save the plot as a JPG file
    plt.savefig(save_path, format='jpg', dpi=300)
    plt.close()
    gc.collect()
