import dataclasses
from typing import List, Dict
import pathlib
import datetime

import toml
import pandas as pd


@dataclasses.dataclass
class Config:
    # The CSV file has headers in the newer versions
    csv_has_headers: bool

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
    # In colab, it likely starts with '/content/drive/Shareddrives/'
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

    # Moving average window size
    moving_average_window_size_min: datetime.timedelta

    @classmethod
    def from_toml(cls, path: pathlib.Path, 
                  datetime_format: str = "%Y-%m-%d %H:%M:%S") -> "Config":
        """
        Create a Config object from a TOML file.

        Inputs:
            cls: type - The class
            path: pathlib.Path - The path to the TOML file
            datetime_format: str - The datetime format of entries in the TOML
        
        Outputs:
            config: Config - The Config object instance        
        """
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

        # BACKWARD COMPATIBILITY
        # In previous versions, the sensor configuration was specified in the
        # config file. Now, it is specified in the CSV file itself.
        csv_has_headers = False
        for sensor in sensor_names:
            if not sensor_config["SENSOR_HEADERS"][sensor]:
                csv_has_headers = True
                break

        # If the network headers are not empty, we want to add the "radio"
        # as a sensor. Note that there is radio data for each sensor.
        if sensor_config["NETWORK_HEADERS"]:
            sensor_config["SENSOR_HEADERS"]["radio"] = sensor_config["NETWORK_HEADERS"]
            sensor_names = sensor_config["SENSOR_HEADERS"].keys()
            full_data_headers["radio"] = sensor_config["BASE_HEADERS"] + \
                                         sensor_config["NETWORK_HEADERS"]

        # Note that we _need_ to account for the case where the strings are empty
        # since we cannot strptime an empty string
        if not io_config["START_DATETIME"]:
            start_datetime = None
        else:
            start_datetime = datetime.datetime.strptime(
                io_config["START_DATETIME"], datetime_format
            )

        if not io_config["END_DATETIME"]:
            end_datetime = None
        else:
            end_datetime = datetime.datetime.strptime(
                io_config["END_DATETIME"], datetime_format
            )

        if not plot_config["MOVING_AVERAGE_WINDOW_SIZE_MIN"]:
            moving_average_window_size_min = datetime.timedelta(minutes=10)
        else:
            moving_average_window_size_min = datetime.timedelta(
                minutes=plot_config["MOVING_AVERAGE_WINDOW_SIZE_MIN"]
            )

        
        event_datetimes = [
            datetime.datetime.strptime(event_time, datetime_format)
            for event_time in events_config["EVENT_DATETIMES"]
        ]

        return cls(
            csv_has_headers=csv_has_headers,
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
            moving_average_window_size_min=moving_average_window_size_min
        )
    
    @classmethod
    def from_default(cls) -> "Config":
        """
        Generate a default Config object that has most parameters set to None.
        """
        return cls(
            csv_has_headers=True,
            base_headers=[],
            network_headers=[],
            sensor_headers={},
            sensor_names=[],
            full_data_headers={},
            data_folder_path="data/",
            logger="",
            plot_folder_path="plots/",
            dpi=300,
            log_y_names=[],
            interval_bounds={},
            start_datetime=None,
            end_datetime=None,
            event_datetimes=[],
            moving_average_window_size_min=datetime.timedelta(minutes=10)
        )

    def update_headers(self, data_dfs: Dict[str, pd.DataFrame]):
        """
        Update the headers of the config with the headers from the dataframes.
        When the CSV file has headers, the headers will not be set in the
        config file, but we will need to update the headers in the config
        class instance.

        Inputs:
            data_dfs: Dict[str, pd.DataFrame] - The dataframes
        """
        for sensor in self.sensor_names:
            self.full_data_headers[sensor] = list(data_dfs[sensor].columns)

        # We need to separate the base, sensor, and network headers.

        len_base_headers = len(self.base_headers)

        for sensor in self.sensor_names:
            assert self.base_headers == self.full_data_headers[sensor][0:len_base_headers], \
                "The base headers are not the same among all sensors!\n" + \
                f"Base headers: {self.base_headers}\n" + \
                f"{sensor} headers: {self.full_data_headers[sensor]}"
            

        # The network headers are shared among all sensors and are at the end
        # of the headers. We can get the network headers with set intersection.
        network_headers = None
        for sensor in self.sensor_names:
            if network_headers is None:
                network_headers = set(
                    self.full_data_headers[sensor][len_base_headers:]
                )
            else:
                network_headers = network_headers.intersection(
                    set(self.full_data_headers[sensor][len_base_headers:])
                )
        
        self.network_headers = sorted(list(network_headers))

        # remove the short name, if it exists
        if "from_short_name" in self.network_headers:
            self.network_headers.remove("from_short_name")

        if len(self.network_headers) > 0:
            # We have radio data
            self.sensor_headers["radio"] = self.network_headers
            self.sensor_names = self.sensor_headers.keys()
            self.full_data_headers["radio"] = self.base_headers + self.network_headers
        
        # The remaining headers are the sensor headers and are between the
        # base and network headers.
        len_network_headers = len(self.network_headers)
        for sensor in self.sensor_names:
            if sensor != "radio":
                self.sensor_headers[sensor] = self.full_data_headers[sensor][
                        len_base_headers:-(len_network_headers + 1)
                    ]
