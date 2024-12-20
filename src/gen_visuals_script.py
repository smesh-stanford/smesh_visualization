# import datetime
# import matplotlib.pyplot as plt

import pathlib         # Nicer IO than the os library
# from tqdm import tqdm  # Progress bar

# Custom imports
from config_parser import Config
from data_parsing import read_csv_data_from_logger, \
    trim_datetime_range, make_folder_datetime_range
from moving_average import calculate_sensor_moving_averages
from smesh_plots import save_plot_helper, \
    plot_all_sensor_variables, \
    plot_moving_averages, \
    plot_correlation_matrix, plot_correlation_scatter, \
    plot_datetime_histogram, plot_sensor_interval, \
    plot_sensor_interval_boxplot
from terminal_utils import with_color, now_print

########################################################
#  Plotting Configuration (you should only need to change this)
########################################################

# Config file path
# CONFIG_FILEPATH = pathlib.Path("data/pepperwood-post-burn/plotting_config.toml")
# CONFIG_FILEPATH = pathlib.Path("data/henrycoe-pre-burn/plotting_config.toml")
# CONFIG_FILEPATH = pathlib.Path("data/henrycoe-post-burn/plotting_config.toml")
# CONFIG_FILEPATH = pathlib.Path("data/henrycoe-post-burn/plotting_config_4004.toml")
# CONFIG_FILEPATH = pathlib.Path("data/burnbot-post-burn/plotting_config_4004.toml")
CONFIG_FILEPATH = pathlib.Path("data/pepperwood-post-burn/plotting_config_2024-12-19.toml")

now_print(f"Loading configuration from {with_color(CONFIG_FILEPATH)}...")
config = Config.from_toml(CONFIG_FILEPATH)

########################################################
# Main (should integrate with tyro)
########################################################

# Check that the folder exists
assert pathlib.Path(config.data_folder_path).is_dir(), \
    f"Data folder path {config.data_folder_path} does not exist. Check the path. " + \
    f"Current working directory: {pathlib.Path.cwd()}"

now_print(f"Loading data...")
smesh_data_dfs = read_csv_data_from_logger(
    config.logger, config.data_folder_path, config.sensor_names, 
    config.full_data_headers)
    # extension="_modified.csv")
now_print(f"Data loaded!")

# Trim the datetime range if necessary
if config.start_datetime and config.end_datetime:
    # Both strings are not empty
    now_print(f"Trimming datetime range...")
    smesh_data_dfs = trim_datetime_range(
        smesh_data_dfs, config.start_datetime, config.end_datetime)
    now_print(f"Datetime range trimmed!")

# Make the folder for the datetime range
# This fuction will account for the case where the datetimes are None
plots_folder = make_folder_datetime_range(
    pathlib.Path(config.plot_folder_path), 
    config.start_datetime, config.end_datetime)


# Plotting
for sensor in config.sensor_names:
    now_print(f"Plotting {with_color(sensor)}...")
    fig, axes = plot_all_sensor_variables(smesh_data_dfs, sensor=sensor,
                                          sensor_headers=config.sensor_headers,
                                          event_datetimes=config.event_datetimes)

    save_plot_helper(fig, plots_folder, f"{sensor}_all_vars_timeseries.png",
                     dpi=config.dpi)

    now_print(f"... {sensor} plotted!")

# Not plot pmsa with logy scale
for sensor in config.log_y_names:
    now_print(f"Plotting {with_color(sensor)} with logy scale...")
    fig, axes = plot_all_sensor_variables(smesh_data_dfs, sensor=sensor,
                                          sensor_headers=config.sensor_headers,
                                          event_datetimes=config.event_datetimes,
                                          logy=True)

    save_plot_helper(fig, plots_folder, f"{sensor}_all_vars_timeseries_logy.png",
                     dpi=config.dpi)

    now_print(f"... {sensor} plotted with logy scale!")

# Calculate and plot the moving average
moving_avg_dict = {}
for sensor in config.sensor_names:
    now_print(f"Calculating moving average for {with_color(sensor)}...")
    moving_avg_dict[sensor] = calculate_sensor_moving_averages(
        smesh_data_dfs, sensor=sensor, sensor_headers=config.sensor_headers,
        window_size=config.moving_average_window_size_min
    )
    now_print(f"... {sensor} moving average calculated!")

for sensor in config.sensor_names:
    now_print(f"Plotting moving average for {with_color(sensor)}...")
    fig, axes = plot_moving_averages(moving_avg_dict,
                                     smesh_data_dfs, sensor=sensor,
                                     sensor_headers=config.sensor_headers,
                                     window_min=config.moving_average_window_size_min,
                                     event_datetimes=config.event_datetimes)

    save_plot_helper(fig, plots_folder, f"{sensor}_all_vars_timeseries_moving_avg.png",
                     dpi=config.dpi)

    now_print(f"... {sensor} moving average plotted!")

# Plot correlation matrix and scatter
for sensor in config.sensor_names:
    now_print(f"Plotting correlation for {with_color(sensor)}...")
    fig, axes = plot_correlation_matrix(smesh_data_dfs, sensor=sensor,
                                        sensor_headers=config.sensor_headers)
    save_plot_helper(fig, plots_folder, f"{sensor}_correlation_matrix.png",
                     dpi=config.dpi)

    fig, axes = plot_correlation_scatter(smesh_data_dfs, sensor=sensor,
                                        sensor_headers=config.sensor_headers)
    save_plot_helper(fig, plots_folder, f"{sensor}_correlation_scatter.png",
                     dpi=config.dpi)

    now_print(f"... {sensor} correlation plotted!")

# Plot datetime histogram
for sensor in config.sensor_names:
    now_print(f"Plotting datetime histogram for {with_color(sensor)}...")
    fig, axes = plot_datetime_histogram(smesh_data_dfs, sensor=sensor,
                                        event_datetimes=config.event_datetimes)
    save_plot_helper(fig, plots_folder, f"{sensor}_datetime_histogram.png",
                     dpi=config.dpi)

    fig, axes = plot_sensor_interval(smesh_data_dfs, sensor=sensor,
                                        event_datetimes=config.event_datetimes)
    save_plot_helper(fig, plots_folder, f"{sensor}_sensor_interval.png",
                     dpi=config.dpi)

    fig, axes = plot_sensor_interval_boxplot(smesh_data_dfs, sensor=sensor)
    save_plot_helper(fig, plots_folder, f"{sensor}_sensor_interval_boxplot.png",
                     dpi=config.dpi)

    min_time, max_time = config.interval_bounds[sensor]
    min_time = int(min_time)
    max_time = int(max_time)
    fig, axes = plot_sensor_interval_boxplot(smesh_data_dfs, sensor=sensor, 
                    max_time=max_time, min_time=min_time,
                    lim_bounds=True)
    appendix = f"boxplot_bound_{min_time}-{max_time}s"
    save_plot_helper(fig, plots_folder, f"{sensor}_sensor_interval_{appendix}.png",
                     dpi=config.dpi)

    fig, axes = plot_sensor_interval_boxplot(smesh_data_dfs, sensor=sensor, 
                    max_time=max_time, min_time=min_time,
                    lim_bounds=True, violin_version=True)
    appendix = f"violin_bound_{min_time}-{max_time}s"
    save_plot_helper(fig, plots_folder, f"{sensor}_sensor_interval_{appendix}.png",
                     dpi=config.dpi)

    now_print(f"... {sensor} datetime histogram plotted!")


now_print(f"All plots completed!")
