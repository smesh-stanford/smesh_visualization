import datetime
import pathlib         # Nicer IO than the os library
import pandas as pd

# Custom imports
from terminal_utils import with_color, now_print, print_issue
from config_parser import Config


def get_short_name(df: pd.DataFrame):
    """
    Get the short name from the dataframe.

    Inputs:
        df: pd.DataFrame - The dataframe

    Outputs:
        short_name: str - The short name of the node
    """
    snake_from_node = 'from_node' in df.columns
    camel_from_node = 'fromNode' in df.columns

    # We need to check that one of the columns exists
    assert snake_from_node or camel_from_node, \
        "The dataframe does not have a 'from_node' or 'fromNode' column, " + \
        "so we cannot determine the short name."
    
    from_node_col = 'from_node' if snake_from_node else 'fromNode'

    return df[from_node_col].str[-4:]


def read_csv_data_from_logger(config: Config, extension: str = ".csv") -> dict:
    """
    Find the relevant data read from a specified logger node and form a pandas
    dataframe for each of the datasets.

    Inputs:
        config: Config     - A Config object
        extension: str     - A string to the file extension. Default is ".csv"

    Ouputs:
        data_dfs : dict    - A dictionary of pandas dataframes
    """
    assert isinstance(config, Config), \
        f"config is not a Config object. It is a {type(config)}"

    data_dfs = {}

    for sensor in config.sensor_names:

        if sensor == "radio":
            # skip for now (handle at end when the rest of the data is loaded)
            continue

        now_print(f"Trying to open data for " + with_color(sensor) + "...")
        data_path = pathlib.Path(
            config.data_folder_path + config.logger + "_" + sensor + extension)
        
        if not data_path.exists():
            print(f"Current working directory: {pathlib.Path.cwd()}")
            print(f"No data for {sensor}. Used the following path: {data_path}")
            continue

        # The "header=None" means that the file does NOT have headers
        # The "infer" means that the headers will be inferred from the first row
        # of the csv file.
        csv_header_processing = "infer" if config.csv_has_headers else None

        # The "parse_dates=[0]" means that the zeroth column includes datetime
        # objects.
        data_dfs[sensor] = pd.read_csv(data_path, 
            header=csv_header_processing, parse_dates=[0])

        if not config.csv_has_headers:
            # If we do not have the headers, we need to add them
            data_dfs[sensor].columns = config.full_data_headers[sensor]
        
        # Include the short name out of convenience
        data_dfs[sensor]['from_short_name'] = get_short_name(data_dfs[sensor])

        now_print("... Sensor completed!")
        
    return data_dfs


def read_radio_data_from_sensor_data(data_dfs: dict, 
                                     config: Config) -> None:
    """
    Read the radio data from the sensor data and add it to the data_dfs
    dictionary.

    Inputs:
        data_dfs: dict - A dictionary of pandas dataframes
        config: Config - A Config object
    """
    assert isinstance(config, Config), \
        f"config is not a Config object. It is a {type(config)}"
    
    # Now that the data is loaded, we can load the radio data from the
    # pandas dataframes of the other sensors (i.e., the network headers
    # that are common to all sensors)
    now_print(f"Reformatting data for " + with_color("radio") + "...")

    # Get the radio headers with an additional column for the sensor from
    # which the radio data is coming
    radio_headers = config.full_data_headers["radio"]
    radio_df_headers = config.full_data_headers["radio"] + ["from_sensor"]

    # Create a new dataframe for the radio data
    radio_df = None

    # Add the radio data from the other sensors
    for sensor in config.sensor_names:
        if sensor == "radio":
            continue

        # Get a copy of the radio data from the sensor
        sensor_radio_df = data_dfs[sensor][radio_headers].copy()

        # Add the sensor name to the radio data
        sensor_radio_df["from_sensor"] = sensor

        sensor_radio_len = len(sensor_radio_df)

        assert all(sensor_radio_df.columns == radio_df_headers), \
            f"The columns of the radio dataframe are not as expected. " + \
            f"Expected: {radio_df_headers}. Got: {sensor_radio_df.columns}"

        # Add the radio data to the radio dataframe
        if radio_df is None:
            radio_df = sensor_radio_df
        else:
            radio_df_len = len(radio_df)
            radio_df = pd.concat([radio_df, sensor_radio_df])

            assert len(radio_df) == radio_df_len + sensor_radio_len, \
                f"The length of the radio dataframe is not as expected " + \
                " after concatenating the new sensor data. \n" + \
                f"Expected: {radio_df_len + sensor_radio_len} \n" + \
                f"Got: {len(radio_df)}"
            
            radio_df_len = len(radio_df)

    # Remove rows where the datetime is NaT
    radio_df = radio_df.dropna(subset=["datetime"])

    if len(radio_df) != radio_df_len:
        print_issue(f"Removed {radio_df_len - len(radio_df)} rows with " + \
                    "NaT datetime that could not be sorted in the radio data.")

    # Sort the radio dataframe by datetime
    # We ignore the index since we want the sort to be permanent
    radio_df.sort_values(by="datetime", inplace=True, ignore_index=True)

    # Add the short names
    radio_df['from_short_name'] = get_short_name(radio_df)

    # Add the radio dataframe to the data_dfs dictionary
    data_dfs["radio"] = radio_df


def trim_datetime_range(data_dfs: dict, 
                        config: Config) -> dict:
    """
    Trim the datetime range of the dataframes in the dictionary.

    Inputs:
        data_dfs: dict                    - A dictionary of pandas dataframes
        config: Config                    - A Config object

    Outputs:
        trimmed_data_dfs: dict - A dictionary of pandas dataframes
    """
    trimmed_data_dfs = {}

    assert isinstance(config.start_datetime, datetime.datetime), \
        "start_datetime is not a datetime.datetime object. It is a " + \
        type(config.start_datetime)
    assert isinstance(config.end_datetime, datetime.datetime), \
        "end_datetime is not a datetime.datetime object. It is a " + \
        type(config.end_datetime)

    for sensor, df in data_dfs.items():
        trimmed_data_dfs[sensor] = df[
            (df['datetime'] >= config.start_datetime) & 
            (df['datetime'] <= config.end_datetime)
            ]

    return trimmed_data_dfs


def make_folder_datetime_range(config: Config,
        plots_folder: pathlib.Path=None) -> pathlib.Path:
    """
    Add a folder within the plots folder that includes the datetime range using 
    Pathlib.

    Inputs:
        config: Config - A Config object
        plots_folder: pathlib.Path - A Path object to override the plots folder
    
    Outputs:
        datetime_folder: pathlib.Path - A Path object to the datetime folder
    """
    assert isinstance(config, Config), \
        f"config is not a Config object. It is a {type(config)}"
    
    if plots_folder is None:
        plots_folder = pathlib.Path(config.plot_folder_path) / config.logger
    elif not isinstance(plots_folder, pathlib.Path):
        try:
            plots_folder = pathlib.Path(plots_folder)
        except TypeError as e:
            print(f"Could not convert plots_folder to a Path object.")
            print("Error: ", e)
            raise e

    if config.start_datetime is None or config.end_datetime is None:
        datetime_folder = plots_folder / f"full_timeseries"
    else:
        assert isinstance(config.start_datetime, datetime.datetime), \
            "start_datetime is not a datetime.datetime object. It is a " + \
            type(config.start_datetime)
        assert isinstance(config.end_datetime, datetime.datetime), \
            "end_datetime is not a datetime.datetime object. It is a " + \
            type(config.end_datetime)

        # Convert the datetime objects to strings as
        # "YYYY-MM-DD_HH-MM-SS"
        start_datetime_str = config.start_datetime.strftime("%Y-%m-%d_%H-%M-%S")
        end_datetime_str = config.end_datetime.strftime("%Y-%m-%d_%H-%M-%S")

        datetime_folder = plots_folder / f"{start_datetime_str}_{end_datetime_str}"
    
    datetime_folder.mkdir(exist_ok=True, parents=True)

    return datetime_folder
