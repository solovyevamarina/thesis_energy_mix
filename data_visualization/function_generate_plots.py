from data_visualization.plots.mix_pie_chart_energy_perc import generate_energy_mix_pie_chart, calculate_yearly_energy_percentages
from data_visualization.plots.energy_stackplot import generate_energy_stack_plot
from data_visualization.plots.price_timeline import generate_price_timeline_plot
from data_visualization.plots.energy_production_timeline import generate_timeline_plot


def generate_descriptive_plots(a_dataset, country, s_time, e_time, country_configs):
    # Generate the individual plots one by one

    # 1. Energy Mix Pie Chart
    try:
        generate_energy_mix_pie_chart(a_dataset, country, s_time, e_time, country_configs)
        print(f"Energy Mix Pie Chart for {country} ({s_time} to {e_time}) created successfully.")
    except Exception as e:
        print(f"Error creating Energy Mix Pie Chart: {e}")

    # 2. Yearly Energy Percentages CSV
    try:
        calculate_yearly_energy_percentages(a_dataset, country, s_time, e_time, country_configs)
        print(f"Yearly Energy Percentages CSV for {country} ({s_time} to {e_time}) created successfully.")
    except Exception as e:
        print(f"Error creating Yearly Energy Percentages CSV: {e}")

    # 3. Yearly Energy Stackplot
    try:
        generate_energy_stack_plot(a_dataset, country, s_time, e_time, country_configs)
        print(f"Yearly Energy Stackplot Chart for {country} ({s_time} to {e_time}) created successfully.")
    except Exception as e:
        print(f"Error creating Yearly Energy Stackplot Chart: {e}")

    # 4. Timeline Plot for Energy Production
    try:
        generate_timeline_plot(a_dataset, country, s_time, e_time, country_configs)
        print(f"Energy Timeline Plot for {country} ({s_time} to {e_time}) created successfully.")
    except Exception as e:
        print(f"Error creating Energy Timeline Plot: {e}")

    # 4. Price Timeline Plot
    try:
        generate_price_timeline_plot(a_dataset, country, s_time, e_time, country_configs)
        print(f"Price Timeline Plot for {country} ({s_time} to {e_time}) created successfully.")
    except Exception as e:
        print(f"Error creating Price Timeline Plot: {e}")
