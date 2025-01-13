"""
Pull data from the provided N5 sensor and plot it similarly to the 
SNode data.
"""

import pandas as pd
import pathlib 
import datetime

# Custom imports
from terminal_utils import now_print, with_color
from config_parser import Config
from data_parsing import make_folder_datetime_range
from smesh_plots import save_plot_helper, \
                        plot_all_sensor_variables, \
                        plot_moving_averages
from moving_average import calculate_sensor_moving_averages


def read_n5_data(n5_file: str) -> pd.DataFrame:
    """
    Read the N5 data from the provided file.

    Args:
    n5_file (str): The file containing the N5 data.

    Returns:
    pd.DataFrame: The N5 data.
    """
    # Read the data
    df_n5 = pd.read_csv(n5_file, header="infer", parse_dates=[0])

    # rename time column to datetime
    df_n5.rename(columns={"time": "datetime"}, inplace=True)

    return df_n5


if __name__ == "__main__":
    # Read the N5 data
    now_print(f"Loading N5 data...")
    n5_file = pathlib.Path("external-data/burnbot-post-burn/N5-raw-data-aa-87-13-85_2025-01-07 17_31_26_full.csv")
    df_n5 = read_n5_data(n5_file)
    now_print(f"... N5 data loaded!")

    # Format the config for the N5 data
    n5_sparse_config = Config.from_default()
    n5_sparse_config.plot_folder_path = "plots/burnbot-post-burn/N5/"
    n5_sparse_config.moving_average_window_size_min = datetime.timedelta(minutes=120)
    # The first two columns are datetime and stationID
    n5_sensor_name = "all_N5"
    n5_sparse_config.sensor_headers = {n5_sensor_name: list(df_n5.columns[2:])}
    n5_station_id = df_n5.columns[1]

    # print("N5 data description:")
    # print(df_n5.describe())

    plots_folder = make_folder_datetime_range(n5_sparse_config)
    now_print(f"Plots will be saved to {with_color(plots_folder)}")

    # Reformat to fit the existing plotting functions
    nf_data_dfs = {n5_sensor_name: df_n5}

    # Plot the N5 data
    now_print(f"Plotting {with_color(n5_sensor_name)} data...")
    fig, _ = plot_all_sensor_variables(nf_data_dfs, sensor=n5_sensor_name,
                                        config=n5_sparse_config,
                                        group_col_id=n5_station_id)

    save_plot_helper(fig, plots_folder, f"n5_all_vars_timeseries.png")
    now_print(f"... {with_color(n5_sensor_name)} data plotted!")

    # Calculate the moving average
    now_print(f"Calculating moving average for {with_color(n5_sensor_name)}...")
    moving_avg_dict = {}
    moving_avg_dict[n5_sensor_name] = calculate_sensor_moving_averages(
        nf_data_dfs, sensor=n5_sensor_name, config=n5_sparse_config,
        group_col_id=n5_station_id
    )

    # Plot the moving average
    now_print(f"Plotting moving average for {with_color(n5_sensor_name)}...")
    fig, _ = plot_moving_averages(moving_avg_dict, 
                                  nf_data_dfs, sensor=n5_sensor_name,
                                  config=n5_sparse_config,
                                  group_col_id=n5_station_id)
    save_plot_helper(fig, plots_folder, f"n5_all_vars_timeseries_moving_avg.png")
