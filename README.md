# SMesh Visualization
Use `smesh_visualization` to visualize data from our SMesh Nodes with `matplotlib`: [https://matplotlib.org/stable/].

## Repo structure
This repo is intended to include the relevant code and example files (inputs and outputs). Eventually, this repo will _only_ store the relevant code with minimal examples. 
```
- data                  <-- Contains the raw SNode data
  └─── burnbot-post-burn (new format)
       └─── 62e4_airQualityMetrics.csv
       └─── 62e4_deviceMetrics.csv
       └─── 62e4_environmentMetrics.csv
       └─── 62e4_powerMetrics.csv
       └─── plotting_config_62e4.toml
       └─── etc.
  └─── pepperwood-post-burn
       └─── 62e4_bme688.csv
       └─── 62e4_device_metrics.csv
       └─── 62e4_ina260.csv
       └─── 62e4_pmsa003i.csv
       └─── plotting_config.toml
       └─── etc.
  └─── etc.
- notebooks             <-- Contains old data visualization notebooks [to be deprecated]
  └─── pepperwood_csv_data_analysis.ipynb
- plots                 <-- Contains the generated plots (usually hi-res at 300 dpi)
  └─── pepperwood-post-burn
       └─── 62e4
            └─── 2024-11-08_10-00-00_2024-11-12_10-00-00
                 └─── many plots
            └─── full_timeseries
                 └─── many plots
  └─── etc.
- src                   <-- Contains all the functions and scripts
  └─── concat_data_script.py    <-- Script to combine the data in the new format into one file
  └─── ...
  └─── gen_visuals_script.py    <-- Script to generate all the plots
  └─── ...
- visualization logs    <-- Contains the stdout of running the plotting script as reference
  └─── etc.
- .gitignore
- README.md
- requirements.txt
```

## Using this repository
Once you clone the repo, the overall process is as follows:
1. :floppy_disk: Save the SNode data files to your computer.
2. :paperclips: Concatenate the data files into one file per sensor
3. :clipboard: Make a plotting configuration file to specify the plotting parameters
4. :drum: Generate the plots
5. :chart_with_downwards_trend: Present your findings

### Step 1: :floppy_disk: Save the data files locally
The expectation is that you are running this repo on your computer (though you could run this code elsewhere, such as in Google Colab, without issue). You will likely download a zip folder with all the data from a fieldwork trip. Unzip the folder such that it looks like this:
```
data/burnbot-post-burn-62e4/
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
```

---
### Step 2: :paperclips: Concatenating the data files
If you are using the new data format, you will have (potentially) a lot of files. We do not want to upload all those individual files to GitHub or parse through them every time. Instead, we concatenate all those files into **one** file, which will go to the `data/` folder.

Go to `src/concat_data_script.py` and edit these lines:
https://github.com/smesh-stanford/smesh_visualization/blob/d0d56b09c9bc9831459af950206421a3943f5d2d/src/concat_data_script.py#L20-L24

The `data_dir` is where the SNode data is currently located (potentially _many_ files). The `output_dir` is where the SNode data will be stored once concatenated. The `logger_name` specifies which logger to select when concatenating. 

Usually, you run `python src/concat_data_script.py` from the base repo directory (e.g., from VS Code). If using relative paths, the directory paths must be in reference to where the script is run! You can use absolute paths if needed to ignore where the script is run from.  

At this point, the data will look like
```
data/burnbot-post-burn/
    ca0c_airQualityMetrics.csv
    ca0c_deviceMetrics.csv
    ca0c_environmentMetrics.csv
    ca0c_powerMetrics.csv
```
:warning: **Please avoid committing the original `data_dir` to GitHub!**

---
### Step 3: :clipboard: Make the plotting configuration
Wherever the `output_dir`, you will now make a plotting configuration file to specify what we want to plot. Generally, you can copy an existing file and make small modifications. This is a [TOML file](https://en.wikipedia.org/wiki/TOML) with four sections:
1. **Sensor Configuration:** Most entries will be blank in the new data format since headers are included in the CSV. It is important to check that the `"fromNode"` string matches the CSV data provided. Otherwise, we cannot find the relevant SNode that sent the data.
2. **IO Configuration:** :warning: _Please_ change the `DATAFOLDERPATH` and `LOGGER` entries to match the directory where the data is located (`output_dir` and `logger_name` in the previous script)
3. **Plotting Configuration:** :warning: _Please_ change the `PLOTFOLDERPATH` entry to match the directory that you want to save the plots. The `PLOTTING_CONFIG.INTERVAL_BOUNDS` parameter lets you set the y limits in the boxplots to identify if packets are going through at the expected intervals. Choose bounds that match what was used in the field. For example, if the SNode should have sent `enviornmentalMetrics` (bme688 or wind) at every 60 seconds, a typical interval is `50, 200`, which includes the expected 60 seconds (with 10s margin), the 120 seconds case of a missed packet, and the 180 seconds case of two missed packets (with 20s margin).
4. **Events Configuration:** :warning: _Please_ change the `EVENT_DATETIMES` to match the event dates and times of the relevant fieldwork. Often this includes when the burn started and ended, as well as weather considerations (e.g., rain) that may impact the interpretation of the results. 

---
### Step 4: :drum: Generate the Plots
With everything set up, you now either (1) use system arguments or (2) edit the default `config_filepath`.

#### Option 1 (Preferred)
Simply run `python path/to/src/gen_visuals_script.py path/to/plotting_config.toml`. For example, if running from the repo directory, you may have `python src/gen_visuals_script.py data/burnbot-post-burn/plotting_config_62e4.toml`. 

#### Option 2
In the `gen_visuals_script.py`, change the default `config_filepath` as shown below:
https://github.com/smesh-stanford/smesh_visualization/blob/d0d56b09c9bc9831459af950206421a3943f5d2d/src/gen_visuals_script.py#L189

---
### Step 5: :chart_with_downwards_trend: Present your findings
You can now show off the time series of the data!
![PM timeseries at Pepperwood Preserve](https://github.com/smesh-stanford/smesh_visualization/blob/main/plots/pepperwood-post-burn/62e4/full_timeseries/pmsa003i_all_vars_timeseries_moving_avg.png)

Or the correlation between sensor measurements!
![BME correlation at Pepperwood Preserve](https://github.com/smesh-stanford/smesh_visualization/blob/main/plots/pepperwood-post-burn/62e4/full_timeseries/bme688_correlation_scatter.png)

Or the interval between sensor packets!
![INA interval at Pepperwood Preserve](https://github.com/smesh-stanford/smesh_visualization/blob/main/plots/pepperwood-post-burn/62e4/full_timeseries/ina260_sensor_interval_boxplot_bound_270-330s.png)

Or the radio readings throughout!
![Radio timeseries at Pepperwood Preserve](https://github.com/smesh-stanford/smesh_visualization/blob/main/plots/pepperwood-post-burn/62e4/full_timeseries/radio_all_vars_timeseries_moving_avg.png)
