import pandas as pd
import datetime

from terminal_utils import print_issue
from config_parser import Config

def moving_average_per_node(df: pd.DataFrame, 
                            window_size: datetime.timedelta,
                            datetime_col: str = 'datetime') -> pd.DataFrame:
    """
    Apply a moving average to a single dataframe that has irregular datetimes.

    Inputs:
        data_dfs: pd.DataFrame - A pandas dataframe
        window_size: datetime.timedelta - The window size for the moving average
        datetime_col: str - The name of the datetime column
    
    Outputs:
        moving_avg_df: pd.DataFrame - A pandas dataframe with the moving average
    """
    # Check that the types are correct
    assert isinstance(df, pd.DataFrame), \
        f"df is not a pd.DataFrame object. It is a {type(df)}"
    assert isinstance(window_size, datetime.timedelta), \
        f"window_size is not a datetime.timedelta object. " + \
        f"It is a {type(window_size)}"
    
    # Check that the datetime column exists
    assert datetime_col in df.columns, \
        f"{datetime_col} is not in the dataframe columns. " + \
        f"The columns are {df.columns}"
    assert df[datetime_col].dtype == 'datetime64[ns]', \
        f"{datetime_col} is not a datetime column. " + \
        f"The type is {df[datetime_col].dtype}"
    
    # Remove any rows with NaT (Not a Time) values in the datetime column and 
    # print a warning if any are removed
    num_na = df[datetime_col].isna().sum()
    if num_na > 0:
        print_issue(f"Warning: {num_na} rows have NaT values in the " + \
                    f"datetime column ({datetime_col}). These will be removed.")
        df = df.dropna(subset=[datetime_col])

    # Sort the dataframe by the datetime column
    df_sorted = df.sort_values(by=datetime_col)
    
    # Apply the moving average
    moving_avg_df = df_sorted.rolling(window=window_size, on=datetime_col).mean()

    return moving_avg_df


def calculate_sensor_moving_averages(data_dict: dict, 
        sensor: str, config: Config,
        group_col_id: str = 'from_short_name') -> dict:
    """
    Get the moving averages a specific sensor.

    Inputs:
        data_dict: dict - A dictionary of dataframes
        sensor: str - The name of the sensor
        config: Config - The configuration object
        group_col_id: str - The column to group by
    
    Outputs:
        moving_avg_dict: dict - A dictionary of dataframes with the moving averages
    """
    # Get the dataframe
    curr_data_df = data_dict[sensor]
    
    # Get the moving averages
    moving_avg_df_dict = {}
    for node_name, node_data in curr_data_df.groupby(group_col_id):

        # Only keep the datetime column and the data columns
        node_data = node_data[['datetime'] + config.sensor_headers[sensor]]

        # Apply the moving average
        moving_avg_df_dict[node_name] = moving_average_per_node(
            node_data, config.moving_average_window_size_min)
    
    return moving_avg_df_dict
