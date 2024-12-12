import dataclasses
from typing import List, Dict
import pathlib
import datetime

import toml


@dataclasses.dataclass
class Config:
    # Base Headers include the datetime and the node that the data is from
    # and is common to all sensor data
    base_headers: List[str]

    # Network Headers include the signal metrics from the mesh network
    network_headers: List[str]

    # Sensor Headers include the sensor data from the different sensors
    sensor_headers: Dict[str, List[str]]

    # The names of the sensors
    sensor_names: List[str]

    # The full data headers for each sensor
    full_data_headers: Dict[str, List[str]]

    # The path to the data folder
    data_folder_path: str

    # The meshtastic logger id (only last 4 characters needed)
    logger: str

    # The path to the plot folder
    plot_folder_path: str

    # The DPI of the plots
    dpi: int

    # The names of the sensors that should be plotted on a log scale
    log_y_names: List[str]

    # The interval bounds for each sensor for the y-axis of boxplots
    interval_bounds: Dict[str, List[float]]

    # The start datetime for the data (i.e., to trim the data)
    # An empty string means no trimming
    start_datetime: datetime.datetime

    # The end datetime for the data (i.e., to trim the data)
    # An empty string means no trimming
    end_datetime: datetime.datetime

    # The event datetimes for the data
    event_datetimes: List[datetime.datetime]

    @classmethod
    def from_toml(cls, path: pathlib.Path) -> "Config":
        with open(path) as f:
            top_config = toml.load(f)

        sensor_config = top_config["SENSOR_CONFIG"]
        io_config = top_config["IO_CONFIG"]
        plot_config = top_config["PLOTTING_CONFIG"]
        events_config = top_config["EVENTS_CONFIG"]

        sensor_names = sensor_config["SENSOR_HEADERS"].keys()

        full_data_headers = {
            sensor: sensor_config["BASE_HEADERS"] + \
                    sensor_config["SENSOR_HEADERS"][sensor] + \
                    sensor_config["NETWORK_HEADERS"] \
                for sensor in sensor_names
        }

        datetime_format = "%Y-%m-%d %H:%M:%S"
        start_datetime = datetime.datetime.strptime(
            io_config["START_DATETIME"], datetime_format
        )
        end_datetime = datetime.datetime.strptime(
            io_config["END_DATETIME"], datetime_format
        )
        event_datetimes = [
            datetime.datetime.strptime(event_time, datetime_format)
            for event_time in events_config["EVENT_DATETIMES"]
        ]

        return cls(
            base_headers=sensor_config["BASE_HEADERS"],
            network_headers=sensor_config["NETWORK_HEADERS"],
            sensor_headers=sensor_config["SENSOR_HEADERS"],
            sensor_names=sensor_names,
            full_data_headers=full_data_headers,
            data_folder_path=io_config["DATAFOLDERPATH"],
            logger=io_config["LOGGER"],
            plot_folder_path=plot_config["PLOTFOLDERPATH"],
            dpi=plot_config["DPI"],
            log_y_names=plot_config["LOG_Y_NAMES"],
            interval_bounds=plot_config["INTERVAL_BOUNDS"],
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            event_datetimes=event_datetimes,
        )
