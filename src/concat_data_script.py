"""
Concatenate data from the same logger into one file

In the new logging code, we start a new file at a preset interval.
This script concatenates all the files from the same logger into one file.

Author: Daniel Neamati
"""

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
    concat_logger_data(
        logger_name="0ff4",
        data_dir="raw_data/data_2025-02-09/data/",
        output_dir="data/winter-term-packard/"
    )
