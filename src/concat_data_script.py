"""
Concatenate data from the same logger into one file

In the new logging code, we start a new file at a preset interval.
This script concatenates all the files from the same logger into one file.

Author: Daniel Neamati
"""

import pathlib         # Nicer IO than the os library
import sys             # For system arguments

# Custom imports
from concat_data_utils import concat_logger_data

if __name__ == "__main__":
    # Concatenate the data for each logger
    # concat_logger_data(
    #     "ca0c",
    #     "data/burnbot-post-burn-rohan/",
    #     "data/burnbot-post-burn/"
    # )
    # concat_logger_data(
    #     logger_name="62e4",
    #     data_dir="data/burnbot-post-burn-62e4/",
    #     output_dir="data/burnbot-post-burn/"
    # )
    # concat_logger_data(
    #     logger_name="0ff4",
    #     data_dir="raw_data/data_2025-02-09/data/",
    #     output_dir="data/winter-term-packard/"
    # )

    # Set default values for easier VS Code debugging
    logger_name = "f864"
    data_dir = pathlib.Path(
        r"raw_data/pepperwood_2025-10-23_19-54")
    output_dir = pathlib.Path("data/pepperwood_2025_gdrive/pepperwood_2025_gdrive_10-23_19-54")

    if len(sys.argv) > 1:
        logger_name = sys.argv[1]
        # The path may be a windows path, so we need to treat it as a raw
        # string to avoid escape characters
        data_dir = pathlib.Path(r"{}".format(sys.argv[2]))
        output_dir = pathlib.Path(r"{}".format(sys.argv[3]))

    concat_logger_data(
        logger_name=logger_name,
        data_dir=data_dir,
        output_dir=output_dir
    )
