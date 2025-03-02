import pathlib         # Nicer IO than the os library

# Custom imports
from terminal_utils import with_color, now_print


def get_logger_data_files(logger_name: str, data_dir: pathlib.Path) -> list:
    """
    Get all the data files for a specific logger.

    Inputs:
        logger_name: str, name of the logger (4 digit short name)
        data_dir: pathlib.Path, directory where the data is stored
    
    Outputs:
        data_files: list of pathlib.Path, list of data files
    """
    # Get all the files in the data directory
    data_files = list(data_dir.glob(f"{logger_name}_*.csv"))

    now_print(f"Found {len(data_files)} files for logger " + \
              f"{with_color(logger_name)}")
    
    if len(data_files) == 0:
        now_print(f"No files found for logger {with_color(logger_name)}")

        # We assume all the files are for this logger
        data_files = list(data_dir.glob("*.csv"))
        
        # Rename the files to include the logger name
        for data_file in data_files:
            new_name = data_dir / f"{logger_name}_{data_file.name}"
            data_file.rename(new_name)
            data_file = new_name

        now_print(f"Renamed {len(data_files)} files to include " + \
                    f"the logger name {with_color(logger_name)}")
        
        # Rerun this function to get the files for this logger
        data_files = get_logger_data_files(logger_name, data_dir)

    return data_files


def group_sensor_files(data_filenames):
    """
    Group the data files by the sensor type based on the filename.

    Inputs:
        data_filenames: list of pathlib.Path, list of data files
    
    Outputs:
        data_files_dict: dict, keys are the sensor types and 
                               the values are lists of pathlib.Path objects
    """
    data_files_dict = {}
    for data_file in data_filenames:
        # The sensor type is the second part of the filename
        # e.g, ca0c_airQualityMetrics_2024-12-19_11-25-29.csv
        #           ^^^^^^^^^^^^^^^^^
        sensor_type = data_file.name.split("_")[1]

        if sensor_type not in data_files_dict:
            data_files_dict[sensor_type] = []
        data_files_dict[sensor_type].append(data_file)
    
    return data_files_dict


def concat_sensor_data(sensor_files: list, output_file: pathlib.Path,
                       data_has_header: bool = True) -> None:
    """
    Perform the intermediate step of concatenating the data from the same sensor
    type into one file.

    Inputs:
        sensor_files: list of pathlib.Path, list of data files
        output_file: pathlib.Path, path to the output file
        data_has_header: bool, whether the data has a header or not

    Outputs:
        None, writes the concatenated data to the output_file
    """
    if data_has_header:
        # Get the header
        with open(sensor_files[0], "r") as data_f:
            header = data_f.readline()
    
    # Concatenate the data
    with open(output_file, "w") as out_f:
        if data_has_header:
            out_f.write(header)
        for sensor_file in sensor_files:
            with open(sensor_file, "r") as data_f:
                if data_has_header:
                    curr_data_header = data_f.readline()

                    # Check if the headers are the same
                    assert curr_data_header == header, \
                        "Header mismatch when trying to concatenate data." + \
                        f"Zeroth file ({sensor_files[0]}) had header: {header}" + \
                        f"Current file ({sensor_file}) has header: {curr_data_header}"

                out_f.write(data_f.read())


def concat_logger_data(logger_name: str, 
                       data_dir: pathlib.Path, 
                       output_dir: pathlib.Path,
                       data_has_header: bool = True) -> None:
    """
    Concatenate data from the same logger into one file. Note that the data
    usually has a header, so we need to extract the headers and make sure that 
    the headers align so the data is concatenated correctly.

    Example data:
    ca0c_airQualityMetrics_2024-12-19_11-25-29.csv
    ca0c_airQualityMetrics_2024-12-19_12-25-33.csv
    ca0c_airQualityMetrics_2024-12-19_13-32-02.csv
    ca0c_airQualityMetrics_2024-12-19_14-19-22.csv
    ca0c_airQualityMetrics_2024-12-19_14-19-42.csv
    ca0c_airQualityMetrics_2024-12-19_16-04-14.csv
    ca0c_deviceMetrics_2024-12-19_11-25-29.csv
    ca0c_deviceMetrics_2024-12-19_12-25-33.csv
    ca0c_deviceMetrics_2024-12-19_14-19-22.csv
    ca0c_deviceMetrics_2024-12-19_14-19-42.csv
    ca0c_deviceMetrics_2024-12-19_16-04-14.csv
    ca0c_environmentMetrics_2024-12-19_11-25-29.csv
    ca0c_environmentMetrics_2024-12-19_12-25-33.csv
    ca0c_environmentMetrics_2024-12-19_14-19-22.csv
    ca0c_environmentMetrics_2024-12-19_14-19-42.csv
    ca0c_environmentMetrics_2024-12-19_16-04-14.csv
    ca0c_powerMetrics_2024-12-19_11-25-29.csv
    ca0c_powerMetrics_2024-12-19_12-25-33.csv
    ca0c_powerMetrics_2024-12-19_14-19-22.csv
    ca0c_powerMetrics_2024-12-19_14-19-42.csv
    ca0c_powerMetrics_2024-12-19_16-04-14.csv

    will become:
    ca0c_airQualityMetrics.csv
    ca0c_deviceMetrics.csv
    ca0c_environmentMetrics.csv
    ca0c_powerMetrics.csv

    Inputs:
        logger_name: str, name of the logger (4 digit short name)
        data_dir: pathlib.Path, directory where the data is stored
        output_dir: pathlib.Path, directory where the output should be stored
        data_has_header: bool, whether the data has a header
    
    Outputs:
        None, writes the concatenated data into the output_dir
    """
    data_dir = pathlib.Path(data_dir)
    output_dir = pathlib.Path(output_dir)

    # Get all the data files for the logger
    data_files = get_logger_data_files(logger_name, data_dir)

    # Group the files by the type of data they contain
    data_files_dict = group_sensor_files(data_files)

    # Concatenate the data
    for sensor_type, data_files in data_files_dict.items():
        # Output file
        output_file = output_dir / f"{logger_name}_{sensor_type}.csv"
        now_print(f"Concatenating {with_color(sensor_type)} data for " + \
                  f"{with_color(logger_name)} to {output_file}...")

        # Concatenate the sensor data
        concat_sensor_data(data_files, output_file, data_has_header)

        now_print(f"... concatenated {with_color(sensor_type)} data for " + \
                  f"{with_color(logger_name)}!")
        
