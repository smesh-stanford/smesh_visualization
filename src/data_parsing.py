import datetime
import pathlib         # Nicer IO than the os library
import pandas as pd

# Custom imports
from terminal_utils import with_color, now_print


def get_short_name(df: pd.DataFrame):
    """
    Get the short name from the dataframe.

    Inputs:
        df: pd.DataFrame - The dataframe

    Outputs:
        short_name: str - The short name of the node
    """
    assert 'from_node' in df.columns, \
        "The dataframe does not have a 'from_node' column, so we cannot " + \
        "determine the short name."

    return df['from_node'].str[-4:]


def read_csv_data_from_logger(logger: str, folderpath: str, 
                              sensor_list: list,
                              data_headers: dict,
                              extension: str = ".csv") -> dict:
    """
    Find the relevant data read from a specified logger node and form a pandas
    dataframe for each of the datasets.

    Inputs:
        logger: str        - A string to the logger node
        folderpath: str    - A string to the folder. In colab, it likely starts
                             with '/content/drive/Shareddrives/'
        sensor_list: list  - A list of strings to the sensors to include
        data_headers: dict - A dictionary of lists of strings to the headers
        extension: str     - A string to the file extension. Default is ".csv"

    Ouputs:
        data_dfs : dict    - A dictionary of pandas dataframes
    """
    data_dfs = {}

    for sensor in sensor_list:

        if sensor == "radio":
            # skip for now (handle at end when the rest of the data is loaded)
            continue

        now_print(f"Trying to open data for " + with_color(sensor) + "...")
        data_path = pathlib.Path(folderpath + logger + "_" + sensor + extension)
        if not data_path.exists():
            print(f"Current working directory: {pathlib.Path.cwd()}")
            print(f"No data for {sensor}. Used the following path: {data_path}")
            continue

        # The "header=None" means that the file does NOT have headers
        # The "parse_dates=[0]" means that the zeroth column includes datetime
        # objects.
        data_dfs[sensor] = pd.read_csv(data_path, header=None, parse_dates=[0])

        # Since we do not have the headers, we need to add them
        data_dfs[sensor].columns = data_headers[sensor]
        # Include the short name out of convenience
        data_dfs[sensor]['from_short_name'] = get_short_name(data_dfs[sensor])

        now_print("... Sensor completed!")
    
    if "radio" in sensor_list:
        # Now that the data is loaded, we can load the radio data from the
        # pandas dataframes of the other sensors (i.e., the network headers
        # that are common to all sensors)
        now_print(f"Reformatting data for " + with_color("radio") + "...")

        # Get the radio headers with an additional column for the sensor from
        # which the radio data is coming
        radio_headers = data_headers["radio"]
        radio_df_headers = data_headers["radio"] + ["from_sensor"]

        # Create a new dataframe for the radio data
        radio_df = None

        # Add the radio data from the other sensors
        for sensor in sensor_list:
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

        # Sort the radio dataframe by datetime
        # We ignore the index since we want the sort to be permanent
        radio_df.sort_values(by="datetime", inplace=True, ignore_index=True)

        # Add the short names
        radio_df['from_short_name'] = get_short_name(radio_df)

        # Add the radio dataframe to the data_dfs dictionary
        data_dfs["radio"] = radio_df

    return data_dfs


def trim_datetime_range(data_dfs: dict, 
                        start_datetime: datetime.datetime, 
                        end_datetime: datetime.datetime) -> dict:
    """
    Trim the datetime range of the dataframes in the dictionary.

    Inputs:
        data_dfs: dict                    - A dictionary of pandas dataframes
        start_datetime: datetime.datetime - The start datetime
        end_datetime: datetime.datetime   - The end datetime

    Outputs:
        trimmed_data_dfs: dict - A dictionary of pandas dataframes
    """
    trimmed_data_dfs = {}

    assert isinstance(start_datetime, datetime.datetime), \
        f"start_datetime is not a datetime.datetime object. It is a {type(start_datetime)}"
    assert isinstance(end_datetime, datetime.datetime), \
        f"end_datetime is not a datetime.datetime object. It is a {type(end_datetime)}"

    for sensor, df in data_dfs.items():
        trimmed_data_dfs[sensor] = df[(df['datetime'] >= start_datetime) & 
                                      (df['datetime'] <= end_datetime)]

    return trimmed_data_dfs


def make_folder_datetime_range(plots_folder: pathlib.Path, 
                               start_datetime: datetime.datetime, 
                               end_datetime: datetime.datetime) -> pathlib.Path:
    """
    Add a folder within the plots folder that includes the datetime range using 
    Pathlib.

    Inputs:
        plots_folder: pathlib.Path - A Path object to the plots folder
        start_datetime: datetime.datetime - The start datetime
        end_datetime: datetime.datetime   - The end datetime
    
    Outputs:
        datetime_folder: pathlib.Path - A Path object to the datetime folder
    """
    if not isinstance(plots_folder, pathlib.Path):
        try:
            plots_folder = pathlib.Path(plots_folder)
        except TypeError as e:
            print(f"Could not convert plots_folder to a Path object. Error: {e}")
            raise e

    assert isinstance(start_datetime, datetime.datetime) or start_datetime is None, \
        f"start_datetime is not a datetime.datetime object. It is a {type(start_datetime)}"
    assert isinstance(end_datetime, datetime.datetime) or start_datetime is None, \
        f"end_datetime is not a datetime.datetime object. It is a {type(end_datetime)}"
    
    if start_datetime is None or end_datetime is None:
        datetime_folder = plots_folder / f"full_timeseries"
    else:    
        # Convert the datetime objects to strings as
        # "YYYY-MM-DD_HH-MM-SS"
        start_datetime_str = start_datetime.strftime("%Y-%m-%d_%H-%M-%S")
        end_datetime_str = end_datetime.strftime("%Y-%m-%d_%H-%M-%S")

        datetime_folder = plots_folder / f"{start_datetime_str}_{end_datetime_str}"
    
    datetime_folder.mkdir(exist_ok=True, parents=True)

    return datetime_folder
