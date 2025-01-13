"""
Pull data from the provided N5 sensor and plot it similarly to the 
SNode data.
"""

import pandas as pd
import matplotlib.pyplot as plt
import pathlib 

# Custom imports
from config_parser import Config
from data_parsing import make_folder_datetime_range
from smesh_plots import save_plot_helper


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


def plot_all_n5_variables(df_n5: pd.DataFrame):
    """
    Plot all the variables in the N5 data.

    Args:
    df_n5 (pd.DataFrame): The N5 data.
    """
    # We do not need to plot the datetime or stationID separately
    num_vars = len(df_n5.columns) - 2

    fig, axes = plt.subplots(nrows=num_vars, ncols=1, 
                             figsize=(12, 3 * num_vars), sharex=True)
    # handle single axes case
    axes = [axes] if num_vars == 1 else axes

    sensor_vars = df_n5.columns[2:]

    for ax_ind, sensor_var_name in enumerate(sensor_vars):
        axes[ax_ind].scatter(x='datetime', y=sensor_var_name, data=df_n5,
                             label='stationID', s=1)
        axes[ax_ind].grid(True)
        axes[ax_ind].set_ylabel(sensor_var_name)

    return fig, axes


if __name__ == "__main__":
    # Read the N5 data
    n5_file = pathlib.Path("external-data/burnbot-post-burn/N5-raw-data-aa-87-13-85_2025-01-07 17_31_26.csv")
    df_n5 = read_n5_data(n5_file)

    n5_sparse_config = Config.from_default()
    n5_sparse_config.plot_folder_path = "plots/pepperwood-post-burn/N5/"

    plots_folder = make_folder_datetime_range(n5_sparse_config)

    # Plot the N5 data
    fig, _ = plot_all_n5_variables(df_n5)
    save_plot_helper(fig, plots_folder, f"n5_raw_data.png")
