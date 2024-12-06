import datetime
import matplotlib.pyplot as plt

import pathlib         # Nicer IO than the os library
# from tqdm import tqdm  # Progress bar

# Custom imports
from data_parsing import read_csv_data_from_logger, \
    trim_datetime_range, make_folder_datetime_range
from smesh_plots import save_plot_helper, \
    plot_all_sensor_variables, \
    plot_correlation_matrix, plot_correlation_scatter, \
    plot_datetime_histogram, plot_sensor_interval, \
    plot_sensor_interval_boxplot
from terminal_utils import with_color

########################################################
#  Sensor Configuration (should be in a yml file)
########################################################

# Global variables since the pepperwood code version does not include headers
# It would also be possible to put this in a config.yml or similar format.
BASE_HEADERS = ['datetime', 'from_node']
NETWORK_HEADERS = ['rxSnr', 'hopLimit', 'rxRssi', 'hopStart']

SENSOR_HEADERS = {
    "device_metrics":   ['batteryLevel', 'voltage', 'channelUtilization', 'airUtilTx'],
    "bme688":           ['temperature', 'relativeHumidity', 'barometricPressure', 'gasResistance', 'iaq'],
    "ina260":           ['ch3Voltage', 'ch3Current'],
    "pmsa003i":         ['pm10Standard', 'pm25Standard', 'pm100Standard', 'pm10Environmental', 'pm25Environmental', 'pm100Environmental'],
}
SENSOR_NAMES = SENSOR_HEADERS.keys()

FULL_DATA_HEADERS = {
    sensor: BASE_HEADERS + SENSOR_HEADERS[sensor] + NETWORK_HEADERS \
        for sensor in SENSOR_NAMES
}

DATAFOLDERPATH = 'data/'
LOGGER = "62e4"
PLOTFOLDERPATH = 'plots/'
DPI = 300

LOG_Y_NAMES = ["pmsa003i"]

INTERVAL_BOUNDS = {
    "device_metrics":   [60 * 5.5, 60 * 6.5],
    "bme688":           [50, 70],
    "ina260":           [60 * 4.5, 60 * 5.5],
    "pmsa003i":         [50, 70],
}

START_DATETIME = "2024-11-08 10:00:00"
END_DATETIME = "2024-11-12 10:00:00"

########################################################
# Events Configuration (should be in a yml file)
########################################################

EVENT_DATETIMES = [
    # Year, Month, Day, Time
    datetime.datetime(2024, 11, 9, 10), # Start of the burn
    datetime.datetime(2024, 11, 11, 6), # Start of the rain
    datetime.datetime(2024, 11, 12, 4), # WIFI disconnection
    datetime.datetime(2024, 11, 15, 13), # Last Logger Data
]

########################################################
# Main (should integrate with tyro)
########################################################

# Check that the folder exists
assert pathlib.Path(DATAFOLDERPATH).is_dir(), \
    f"Data folder path {DATAFOLDERPATH} does not exist. Check the path. " + \
    f"Current working directory: {pathlib.Path.cwd()}"

print(f"[{datetime.datetime.now()}] Loading data...")
pepperwood_data_dfs = read_csv_data_from_logger(
    LOGGER, DATAFOLDERPATH, SENSOR_NAMES, FULL_DATA_HEADERS, 
    extension="_modified.csv")
print(f"[{datetime.datetime.now()}] Data loaded!")

# Trim the datetime range if necessary
if START_DATETIME and END_DATETIME:
    # Both strings are not empty
    print(f"[{datetime.datetime.now()}] Trimming datetime range...")
    pepperwood_data_dfs = trim_datetime_range(
        pepperwood_data_dfs, START_DATETIME, END_DATETIME)
    print(f"[{datetime.datetime.now()}] Datetime range trimmed!")

    # Make the folder for the datetime range
    plots_folder = make_folder_datetime_range(
        pathlib.Path(PLOTFOLDERPATH), START_DATETIME, END_DATETIME)

else:
    # The strings are empty
    plots_folder = pathlib.Path(PLOTFOLDERPATH)


# Plotting
for sensor in SENSOR_NAMES:
    print(f"[{datetime.datetime.now()}] Plotting {with_color(sensor)}...")
    fig, axes = plot_all_sensor_variables(pepperwood_data_dfs, sensor=sensor,
                                          sensor_headers=SENSOR_HEADERS,
                                          event_datetimes=EVENT_DATETIMES)

    save_plot_helper(fig, plots_folder, f"{sensor}_all_vars_timeseries.png",
                     dpi=DPI)

    print(f"[{datetime.datetime.now()}] ... {sensor} plotted!")

# Not plot pmsa with logy scale
for sensor in LOG_Y_NAMES:
    print(f"[{datetime.datetime.now()}] Plotting {with_color(sensor)} with logy scale...")
    fig, axes = plot_all_sensor_variables(pepperwood_data_dfs, sensor=sensor,
                                          sensor_headers=SENSOR_HEADERS,
                                          event_datetimes=EVENT_DATETIMES,
                                          logy=True)

    save_plot_helper(fig, plots_folder, f"{sensor}_all_vars_timeseries_logy.png",
                     dpi=DPI)

    print(f"[{datetime.datetime.now()}] ... {sensor} plotted with logy scale!")

# Plot correlation matrix and scatter
for sensor in SENSOR_NAMES:
    print(f"[{datetime.datetime.now()}] Plotting correlation for {with_color(sensor)}...")
    fig, axes = plot_correlation_matrix(pepperwood_data_dfs, sensor=sensor,
                                        sensor_headers=SENSOR_HEADERS)
    save_plot_helper(fig, plots_folder, f"{sensor}_correlation_matrix.png",
                     dpi=DPI)

    fig, axes = plot_correlation_scatter(pepperwood_data_dfs, sensor=sensor,
                                        sensor_headers=SENSOR_HEADERS)
    save_plot_helper(fig, plots_folder, f"{sensor}_correlation_scatter.png",
                     dpi=DPI)

    print(f"[{datetime.datetime.now()}] ... {sensor} correlation plotted!")

# Plot datetime histogram
for sensor in SENSOR_NAMES:
    print(f"[{datetime.datetime.now()}] Plotting datetime histogram for {with_color(sensor)}...")
    fig, axes = plot_datetime_histogram(pepperwood_data_dfs, sensor=sensor,
                                        event_datetimes=EVENT_DATETIMES)
    save_plot_helper(fig, plots_folder, f"{sensor}_datetime_histogram.png",
                     dpi=DPI)

    fig, axes = plot_sensor_interval(pepperwood_data_dfs, sensor=sensor,
                                        event_datetimes=EVENT_DATETIMES)
    save_plot_helper(fig, plots_folder, f"{sensor}_sensor_interval.png",
                     dpi=DPI)

    fig, axes = plot_sensor_interval_boxplot(pepperwood_data_dfs, sensor=sensor)
    save_plot_helper(fig, plots_folder, f"{sensor}_sensor_interval_boxplot.png",
                     dpi=DPI)

    min_time, max_time = INTERVAL_BOUNDS[sensor]
    min_time = int(min_time)
    max_time = int(max_time)
    fig, axes = plot_sensor_interval_boxplot(pepperwood_data_dfs, sensor=sensor, 
                    max_time=max_time, min_time=min_time,
                    lim_bounds=True)
    appendix = f"boxplot_bound_{min_time}-{max_time}s"
    save_plot_helper(fig, plots_folder, f"{sensor}_sensor_interval_{appendix}.png",
                     dpi=DPI)

    fig, axes = plot_sensor_interval_boxplot(pepperwood_data_dfs, sensor=sensor, 
                    max_time=max_time, min_time=min_time,
                    lim_bounds=True, violin_version=True)
    appendix = f"violin_bound_{min_time}-{max_time}s"
    save_plot_helper(fig, plots_folder, f"{sensor}_sensor_interval_{appendix}.png",
                     dpi=DPI)

    print(f"[{datetime.datetime.now()}] ... {sensor} datetime histogram plotted!")


print(f"[{datetime.datetime.now()}] All plots completed!")
