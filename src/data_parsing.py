import datetime
import pathlib         # Nicer IO than the os library
import pandas as pd

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
        print(f"[{datetime.datetime.now()}] Trying to open data for", sensor)
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
        data_dfs[sensor]['from_short_name'] = data_dfs[sensor]['from_node'].str[-4:]

        print(f"[{datetime.datetime.now()}] Sensor completed!\n")

    return data_dfs
