import datetime
import matplotlib.pyplot as plt

import pathlib         # Nicer IO than the os library
# from tqdm import tqdm  # Progress bar

# Custom imports
from data_parsing import read_csv_data_from_logger
from smesh_plots import plot_all_sensor_variables

# Global variables since the pepperwood code version does not include headers
# It would also be possible to put this in a config.yml or similar format.
BASE_HEADERS = ['datetime', 'from_node']
NETWORK_HEADERS = ['rxSnr', 'hopLimit', 'rxRssi', 'hopStart']

SENSOR_HEADERS = {
    "device_metrics":   ['batteryLevel', 'voltage', 'channelUtilization', 'airUtilTx'],
    "bme688":           ['temperature', 'relativeHumidity', 'barometricPressure', 'gasResistance', 'iaq'],
    "ina260":           ['ch3Voltage', 'ch3Current'],
    "pmsa003i":         ['pm10Standard', 'pm25Standard', 'pm100Standard', 'pm10Environmental', 'pm25Environmental', 'pm100Environmental']
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

# Check that the folder exists
assert pathlib.Path(DATAFOLDERPATH).is_dir(), \
    f"Data folder path {DATAFOLDERPATH} does not exist. Check the path. " + \
    f"Current working directory: {pathlib.Path.cwd()}"

print(f"[{datetime.datetime.now()}] Loading data...")
pepperwood_data_dfs = read_csv_data_from_logger(
    LOGGER, DATAFOLDERPATH, SENSOR_NAMES, FULL_DATA_HEADERS, 
    extension="_modified.csv")
print(f"[{datetime.datetime.now()}] Data loaded!")

## Plotting
for sensor in SENSOR_NAMES:
    print(f"[{datetime.datetime.now()}] Plotting {sensor}...")
    fig, axes = plot_all_sensor_variables(pepperwood_data_dfs, sensor=sensor,
                                          sensor_headers=SENSOR_HEADERS)
    fig.savefig(f"{PLOTFOLDERPATH}{sensor}_all_vars.png", dpi=DPI)
    plt.close(fig)
    print(f"[{datetime.datetime.now()}] {sensor} plotted!")
