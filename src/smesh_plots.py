import matplotlib.pyplot as plt
import numpy as np
import datetime

from terminal_utils import print_issue
from config_parser import Config

# try:
#     import astral          # For sunrise and sunset times
#     astral_available = True
#     print("Astral library loaded")
# except ImportError:
#     astral_available = False
#     print("Astral library not available")

def save_plot_helper(fig, folder, filename, dpi=300):
    """
    Save the plot to the filename with the specified dpi

    Inputs:
        fig: matplotlib.figure.Figure - The figure to save
        folder: pathlib.Path          - The folder to save the figure
        filename: str                 - The filename to save the figure
        dpi: int                      - The dpi to save the figure
    
    Outputs:
        None
    """
    fig.savefig(folder / filename, dpi=dpi, bbox_inches='tight')
    plt.close(fig)


def highlight_nighttime(ax, curr_data_df):
    """
    Highlight the nighttime in the plot

    Inputs:
        ax: matplotlib.axes.Axes - The axes to plot on
        curr_data_df: pd.DataFrame - The current data (for the datetime range)
    
    Outputs:
        None, ax is modified in place
    """
    # Fill in the x-axis with grey from 6pm to 6am to represent night time
    earliest_day = curr_data_df['datetime'].iloc[0].date()
    latest_day = curr_data_df['datetime'].iloc[-1].date()

    sunrise = datetime.datetime.strptime("06:00:00", "%H:%M:%S").time() 
    sunset = datetime.datetime.strptime("18:00:00", "%H:%M:%S").time()

    # Print each day between the earliest and latest day
    num_days = (latest_day - earliest_day).days + 2
    for i in range(num_days):
        curr_day = earliest_day + datetime.timedelta(days=i)

        curr_sunrise_datetime = datetime.datetime.combine(curr_day, sunrise)
        curr_sunset_datetime = datetime.datetime.combine(curr_day, sunset)
        ax.axvspan(curr_sunset_datetime - datetime.timedelta(days=1), 
                   curr_sunrise_datetime, 
                   color='grey', alpha=0.25, zorder=0)


def add_event_lines(ax, curr_data_df, event_datetimes):
    """
    Add vertical lines for the events if they are relevant to the current plot

    Inputs:
        ax: matplotlib.axes.Axes - The axes to plot on
        curr_data_df: pd.DataFrame - The current data (for the datetime range)
        event_datetimes: list[datetime.datetime] - The event datetimes
    
    Outputs:
        None, ax is modified in place
    """
    # Get the datetime bounds of the plot since the events
    # may be outside the bounds if the data was trimmed
    min_datetime = curr_data_df['datetime'].iloc[0]
    max_datetime = curr_data_df['datetime'].iloc[-1]

    for event_time in event_datetimes:
        if event_time > min_datetime and event_time < max_datetime:
            ax.axvline(x=event_time, color='k', linestyle='--')


def plot_all_sensor_variables(data_dict: dict, sensor: str,
                              config: Config,
                              logy: bool = False,
                              alpha: float = 1.0,
                              group_col_id: str = 'from_short_name',
                              use_labels: bool = True) -> tuple:
    """
    Plot each sensor variable as a new row in the subplots.

    Inputs:
        data_dict: dict - The dictionary of sensor data
        sensor: str - The sensor to plot
        config: Config - The configuration object
        logy: bool - Whether to use a log scale on the y-axis
        alpha: float - The alpha value for the scatter plot
        group_col_id: str - The column to group the data by
        use_labels: bool - Whether to use labels for the data
    
    Outputs:
        fig: matplotlib.figure.Figure - The figure object
        axes: list[matplotlib.axes.Axes] - The axes objects

    We output the figure and axes objects so that we can modify the plot 
    further if needed (e.g., to include the moving average).
    """
    assert isinstance(config, Config), \
        f"config is not a Config object: {config}"
    
    sensor_vars = config.sensor_headers[sensor]
    
    num_vars = len(sensor_vars)

    fig, axes = plt.subplots(nrows = num_vars, ncols=1,
                             figsize=(12, 3 * num_vars), sharex=True)
    # even when we only have one row (num_vars = 1), we still need to
    # access the axes as a list
    axes = [axes] if num_vars == 1 else axes

    curr_data_df = data_dict[sensor]

    for node_name, node_data in curr_data_df.groupby(group_col_id):
        for var_id, sensed_var in enumerate(sensor_vars):
            label = node_name if use_labels else None
            axes[var_id].scatter(x='datetime', y=sensed_var,
                           data=node_data, label=label, s=1, alpha=alpha)

    for var_id, sensed_var in enumerate(sensor_vars):
        axes[var_id].grid(True)
        axes[var_id].set_ylabel(sensed_var)

        if use_labels:
            axes[var_id].legend(bbox_to_anchor=(1.01, 1), loc='upper left',
                                markerscale=3)
        
        if config.event_datetimes is not None:
            add_event_lines(axes[var_id], curr_data_df, config.event_datetimes)

        if logy:
            axes[var_id].set_yscale('log')

        # if var_id == 0:
        #     axes[var_id].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        # else:
        #     axes[var_id].get_legend().remove()

    minx, maxx = plt.xlim()
    plt.xlabel('Date and Time')

    # Fill in the x-axis with grey to represent night time
    for var_id in range(len(sensor_vars)):
        highlight_nighttime(axes[var_id], curr_data_df)

    # if astral_available:
    #     city = astral.LocationInfo("City", "Region", "Country", 0, 0)
    #     sun = city.sun(date=datetime.datetime.now(), local=True)
    #     sunrise = sun['sunrise']
    #     sunset = sun['sunset']
    #     axes[0].axvspan(sunset, sunrise + datetime.timedelta(days=1), color='grey', alpha=0.5)

    plt.xlim([minx, maxx])

    plt.tight_layout()

    return fig, axes


def plot_moving_averages(moving_avg_dict: dict, 
                         data_dict: dict,
                         sensor: str, 
                         config: Config,
                         logy: bool = False,
                         group_col_id: str = 'from_short_name') -> tuple:
    """
    Plot the moving averages for the sensor variables

    This function uses the plot_all_sensor_variables function as a background.

    Inputs:
        moving_avg_dict: dict - The dictionary of calculated moving averages
        data_dict: dict - The dictionary of sensor data
        sensor: str - The sensor to plot
        config: Config - The configuration object
        logy: bool - Whether to use a log scale on the y-axis
        group_col_id: str - The column to group the data by 
    
    Outputs:
        fig: matplotlib.figure.Figure - The figure object
        axes: list[matplotlib.axes.Axes] - The axes objects
    """
    assert isinstance(config, Config), \
        f"config is not a Config object: {config}"

    sensor_vars = config.sensor_headers[sensor]
    window_min_int = int(
        config.moving_average_window_size_min.total_seconds() / 60
        )

    fig, axes = plot_all_sensor_variables(data_dict, sensor, config,
                                            logy=logy, alpha=0.5,
                                            use_labels=False,
                                            group_col_id=group_col_id)
    
    for node_name, node_data in moving_avg_dict[sensor].items():
        for var_id, sensed_var in enumerate(sensor_vars):
            axes[var_id].plot(node_data['datetime'], node_data[sensed_var],
                label=f"{node_name} Moving Average [{window_min_int} min]")
            
    for var_id, sensed_var in enumerate(sensor_vars):
        axes[var_id].legend(bbox_to_anchor=(1.01, 1), loc='upper left',
                            markerscale=3)

    return fig, axes


def plot_correlation_matrix(data_dict: dict, sensor: str,
                            config: Config, 
                            cmap_choice: str = 'PuOr') -> tuple:
    """
    Plot the correlation matrix for the sensor variables.

    Inputs:
        data_dict: dict - The dictionary of sensor data
        sensor: str - The sensor to plot
        config: Config - The configuration object
        cmap_choice: str - The colormap for coloring the correlation values.
            Default is 'PuOr' (purple to orange), which is a diverging colormap.
            This is convenient to distinguish between positive and negative
            correlations, but is not super colorblind-friendly.
    
    Outputs:
        fig: matplotlib.figure.Figure - The figure object
        ax: matplotlib.axes.Axes - The axes
    """
    curr_data_df = data_dict[sensor]
    sensor_vars = config.sensor_headers[sensor]
    corr_matrix = curr_data_df[sensor_vars].corr()
    num_vars = len(sensor_vars)

    # print(f"Correlation matrix for {sensor}")
    # print(corr_matrix)

    fig, ax = plt.subplots(figsize=(num_vars + 1, num_vars + 1))
    plt.clf()
    # Note that matshow is not compatible with tight_layout
    plt.matshow(corr_matrix, fignum=fig.number,
                vmin=-1, vmax=1, cmap=cmap_choice)
    plt.colorbar()
    vars_list = range(num_vars)
    plt.xticks(vars_list, sensor_vars, rotation=45)
    plt.yticks(vars_list, sensor_vars)
    
    # Annotate the correlation values
    for i in range(num_vars):
        for j in range(num_vars):
            curr_val = corr_matrix.iloc[i, j]
            annot_color = 'white' if abs(curr_val) > 0.5 else 'black'
            plt.text(j, i, f"{corr_matrix.iloc[i, j]:.2f}",
                     ha='center', va='center', color=annot_color)

    return fig, ax


def plot_correlation_scatter(data_dict: dict, sensor: str,
                             config: Config) -> tuple:
    """
    Plot the correlation scatter plot for the sensor variables.

    Inputs:
        data_dict: dict - The dictionary of sensor data
        sensor: str - The sensor to plot
        config: Config - The configuration object

    Outputs:
        fig: matplotlib.figure.Figure - The figure object
        axes: list[matplotlib.axes.Axes] - The axes objects
    """
    curr_data_df = data_dict[sensor]
    sensor_vars = config.sensor_headers[sensor]
    num_vars = len(sensor_vars)

    fig, axes = plt.subplots(nrows = num_vars, ncols=num_vars,
                             figsize=(2 * num_vars + 1, 2 * num_vars),
                             sharex='col', sharey='row')
    
    # Even when we only have one row and column (num_vars = 1), we still need to
    # access the axes as a 2D numpy array
    axes = np.array([[axes]]) if num_vars == 1 else axes
    assert axes.shape == (num_vars, num_vars), f"axes shape is {axes.shape}"
    
    starting_datetime = curr_data_df['datetime'].iloc[0]
    diff_from_start = curr_data_df['datetime'] - starting_datetime

    dt_time_to_days = lambda x: x.total_seconds() / (60 * 60 * 24)
    diff_from_start_in_days = diff_from_start.apply(dt_time_to_days)

    for i, var1 in enumerate(sensor_vars):
        for j, var2 in enumerate(sensor_vars):
            # Color by the index of the data
            im_for_colorbar = axes[j, i].scatter(
                                x=var1, y=var2,
                                data=curr_data_df, s=0.25,
                                c=diff_from_start_in_days)
            # c=curr_data_df["datetime"].apply(lambda x: x.timestamp()))
            # c=range(len(curr_data_df)))
            axes[j, i].grid(True)

            # only set the x-axis label for the bottom row
            if j == 0:
                axes[j, i].set_xlabel(var1)
                axes[j, i].xaxis.set_label_position('top')
            elif j == num_vars - 1:
                axes[j, i].set_xlabel(var1)
                # axes[j, i].xaxis.tick_top()
                # axes[j, i].xaxis.set_label_position('top')
            
            # only set the y-axis label for the left column
            if i == 0:
                axes[j, i].set_ylabel(var2)
    
    plt.tight_layout()

    fig.subplots_adjust(right=0.8)
    # We make the colorbar thin to avoid taking up too much space
    cbar_ax = fig.add_axes([0.85, 0.15, 0.03, 0.7])
    cbar = fig.colorbar(im_for_colorbar, cax=cbar_ax, shrink=0.1)
    cbar.ax.set_ylabel("Date (at midnight)", rotation=-90, va="bottom")

    total_num_days = int(diff_from_start_in_days.iloc[-1])
    first_midnight_datetime = starting_datetime.replace(
        hour=0, minute=0, second=0, microsecond=0)

    cticks = []
    ctick_labels = []

    for i in range(1, total_num_days + 1):
        curr_datetime = first_midnight_datetime + datetime.timedelta(days=i)
        cticks.append(i)
        ctick_labels.append(curr_datetime.strftime("%Y-%m-%d"))

    cbar.set_ticks(cticks)
    cbar.set_ticklabels(ctick_labels)

    return fig, axes


def plot_datetime_histogram(data_dict: dict, sensor: str,
                            config: Config, bin_width_min: int = 15) -> tuple:
    """
    Plot the histogram of the datetime values. Since the sensor data comes as
    a packet, we only need to plot the time of the packet.

    Inputs:
        data_dict: dict - The dictionary of sensor data
        sensor: str - The sensor to plot
        config: Config - The configuration object
        bin_width_min: int - The width of the bins in minutes
    
    Outputs:
        fig: matplotlib.figure.Figure - The figure object
        ax: matplotlib.axes.Axes - The axes
    """
    curr_data_df = data_dict[sensor]
    datetime_values = curr_data_df['datetime']

    num_days = (datetime_values.iloc[-1] - datetime_values.iloc[0]).days + 1
    hrs_per_day = 24
    bins_per_hr = 60 / bin_width_min
    num_bins = num_days * hrs_per_day * bins_per_hr

    # Cast to integer and print warning if there is rounding error
    if num_bins != int(num_bins):
        print_issue(f"Number of bins is not an integer: {num_bins}. " + \
                    f"{int(num_bins)} will be used instead.")
    num_bins = int(num_bins)
    
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(datetime_values, bins=num_bins)

    plt.xticks(rotation=45)
    ax.set_xlabel('Date and Time')

    if bin_width_min != int(bin_width_min):
        print_issue(f"Bin width is not an integer: {bin_width_min}. " + \
                    f"{int(bin_width_min)} will be used instead.")
    bin_width_min = int(bin_width_min)

    ax.set_ylabel(f"Number of measurements per {bin_width_min} minutes")
    plt.title(f'Temporal Histogram of {sensor} readings')
    
    minx, maxx = plt.xlim()

    if config.event_datetimes is not None:
        add_event_lines(ax, curr_data_df, config.event_datetimes)

    highlight_nighttime(ax, curr_data_df)
    plt.xlim([minx, maxx])
    
    return fig, ax


def get_sensor_interval(data_dict: dict, sensor: str,
                        max_time_s = 60 * 60 * 3) -> tuple:
    """
    Get the interval between the sensor readings by node

    Inputs:
        data_dict: dict - The dictionary of sensor data
        sensor: str - The sensor to plot
        max_time_s: int - The maximum time in seconds between readings
    
    Outputs:
        all_intervals: dict - The dictionary of intervals by node
        all_datetimes: dict - The dictionary of datetimes by node
    """
    curr_data_df = data_dict[sensor]
    group_col_id = 'from_short_name'

    all_intervals = {}
    all_datetimes = {}

    for node_name, node_data in curr_data_df.groupby(group_col_id):
        # Check if the datetime is sorted
        if not node_data['datetime'].is_monotonic_increasing:
            print_issue(f"Data for {node_name} is not sorted by datetime.")

        diff_from_prev = node_data['datetime'].diff().dt.total_seconds()

        # if the gap is too large, we assume that the sensor or logger was 
        # turned off and we don't plot the gap
        diff_to_plot = diff_from_prev[diff_from_prev < max_time_s]
        datetime_to_plot = node_data['datetime'][diff_from_prev < max_time_s]

        all_intervals[node_name] = diff_to_plot
        all_datetimes[node_name] = datetime_to_plot

    return all_intervals, all_datetimes


def plot_sensor_interval(data_dict: dict, sensor: str,
                          config: Config,
                          max_time_s = 60 * 60 * 3, 
                          show_max: bool = False) -> tuple:
    """
    Plot the interval between the sensor readings by node

    Inputs:
        data_dict: dict - The dictionary of sensor data
        sensor: str - The sensor to plot
        config: Config - The configuration object
        max_time_s: int - The maximum time in seconds between readings
        show_max: bool - Whether to show the maximum time in the plot
    
    Outputs:
        fig: matplotlib.figure.Figure - The figure object
        ax: matplotlib.axes.Axes - The axes
    """
    curr_data_df = data_dict[sensor]
    all_intervals, all_datetimes = get_sensor_interval(
        data_dict, sensor, max_time_s)

    fig, ax = plt.subplots(figsize=(8, 4))
    for node_name, node_intervals in all_intervals.items():
        ax.scatter(all_datetimes[node_name], node_intervals, 
                   label=node_name, s=1)
    
    plt.xticks(rotation=45)
    ax.set_xlabel('Date and Time')
    max_time_hr_str = str(int(max_time_s / 60 / 60))
    ax.set_ylabel('Time interval between readings ' + \
                   f'(s, max of {max_time_hr_str} hr)')
    plt.title(f'Time Interval between {sensor} readings')

    # plt.axhline(y=0, color='k', linestyle='--', label='0 sec gap')
    
    minx, maxx = plt.xlim()

    if show_max:
        plt.axhline(y=max_time_s, color='r', linestyle='--', 
                    label=f'{max_time_hr_str} hr gap')

    if config.event_datetimes is not None:
        add_event_lines(ax, curr_data_df, config.event_datetimes)

    highlight_nighttime(ax, curr_data_df)
    ax.legend(bbox_to_anchor=(1.01, 1), loc='upper left', markerscale=3)

    plt.xlim([minx, maxx])

    return fig, ax


def plot_sensor_interval_boxplot(data_dict: dict, sensor: str,
                                 config: Config,
                                 force_lim_bounds: bool = False,
                                 min_num_readings: int = 10,
                                 violin_version: bool = False) -> tuple:
    """
    Plot the interval between the sensor readings by node

    Inputs:
        data_dict: dict - The dictionary of sensor data
        sensor: str - The sensor to plot
        config: Config - The configuration object
        force_lim_bounds: bool - Whether to limit the bounds of the plot
        min_num_readings: int - The minimum number of readings to plot
        violin_version: bool - Whether to use a violin plot instead of a boxplot
    
    Outputs:
        fig: matplotlib.figure.Figure - The figure object
        ax: matplotlib.axes.Axes - The axes
    """
    if sensor in config.interval_bounds:
        min_time, max_time = config.interval_bounds[sensor]
    else:
        min_time, max_time = None, None
    cut = max_time if violin_version else np.inf
    all_intervals, _ = get_sensor_interval(data_dict, sensor, cut)

    # Store these in case there is an error later
    num_keys_originally = len(all_intervals.keys())
    num_vals_originally = len(all_intervals.values())
    num_vals_each_originally = [
        len(node_intervals) for node_intervals in all_intervals.values()
        ]

    # Remove empty nodes
    all_intervals = {node_name: node_intervals for node_name, node_intervals \
                     in all_intervals.items() \
                     if len(node_intervals) > min_num_readings}
    
    num_keys_filtered = len(all_intervals.keys())
    num_vals_filtered = len(all_intervals.values())
    
    fig, ax = plt.subplots(figsize=(8, 4))

    if num_keys_filtered == 0:
        assert num_vals_filtered == 0, \
            f"There are no keys but there are {num_vals_filtered} values"

        print_issue(f"No nodes have more than {min_num_readings} readings. " + \
                    f"Originally there were {num_keys_originally} nodes " + \
                    f"with {num_vals_originally} values. " + \
                    f"With {num_vals_each_originally} readings each.")

        return fig, ax

    if violin_version:
        # convert to list of arrays for violinplot
        all_intervals_names = []
        for node_ind, (node_name, node_intervals) in enumerate(all_intervals.items()):
            all_intervals_names.append(node_name)
            node_vals = node_intervals.values
            num_measurements = len(node_vals)
            ax.violinplot(node_vals, positions=[node_ind], 
                          showextrema=False, showmedians=True,
                          points=num_measurements // 5)
        
        ax.set_xticks(range(0, len(all_intervals_names)))
        ax.set_xticklabels(all_intervals_names)
    else:
        flierprops = dict(marker='_', markeredgecolor='tab:grey')
        ax.boxplot(all_intervals.values(), labels=all_intervals.keys(), 
                   flierprops=flierprops)

    plt.xticks(rotation=45)
    ax.set_xlabel('Node Name')
    # max_time_str = f"{(max_time / 60):.2f} min"
    ax.set_ylabel(f'Time interval between readings (s)')
    #   , max of {max_time_str})')
    title = f'Time Interval between {sensor} readings'
    if force_lim_bounds:
        title += f" (between {min_time} and {max_time} s)"
    plt.title(title)

    plt.axhline(y=0, color='b', linestyle='--', label='0 sec gap')
    plt.grid(True, axis='y')

    if force_lim_bounds:
        plt.ylim([min_time, max_time])

    return fig, ax
