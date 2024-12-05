import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


from tqdm import tqdm  # Progress bar

try:
    import astral          # For sunrise and sunset times
    astral_available = True
    print("Astral library loaded")
except ImportError:
    astral_available = False
    print("Astral library not available")

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


