import matplotlib.pyplot as plt
import datetime

# try:
#     import astral          # For sunrise and sunset times
#     astral_available = True
#     print("Astral library loaded")
# except ImportError:
#     astral_available = False
#     print("Astral library not available")


def highlight_nighttime(ax, curr_data_df):
    """
    Highlight the nighttime in the plot
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
        ax.axvspan(
                        curr_sunset_datetime - datetime.timedelta(days=1), 
                        curr_sunrise_datetime, 
                        color='grey', alpha=0.25, zorder=0)


def plot_all_sensor_variables(data_dict: dict, sensor: str,
                              sensor_headers: dict,
                              event_datetimes: list = None,
                              logy: bool = False) -> tuple:
    """
    Plot each sensor variable by row
    """
    col_id = 'from_short_name'
    sensor_vars = sensor_headers[sensor]
    num_vars = len(sensor_vars)

    fig, axes = plt.subplots(nrows = num_vars, ncols=1,
                             figsize=(12, 3 * num_vars), sharex=True)

    curr_data_df = data_dict[sensor]

    for node_name, node_data in curr_data_df.groupby(col_id):
        for var_id, sensed_var in enumerate(sensor_vars):
            axes[var_id].scatter(x='datetime', y=sensed_var,
                           data=node_data, label=node_name, s=1)
            # axes[var_id].plot(x='datetime', y=sensed_var,
            #                   data=node_data, label=node_name)

    for var_id, sensed_var in enumerate(sensor_vars):
        axes[var_id].grid(True)
        axes[var_id].set_ylabel(sensed_var)
        axes[var_id].legend(bbox_to_anchor=(1.01, 1), loc='upper left',
                            markerscale=3)
        
        if event_datetimes is not None:
            for event_time in event_datetimes:
                axes[var_id].axvline(x=event_time, color='k', linestyle='--')

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


def plot_correlation_matrix(data_dict: dict, sensor: str,
                            sensor_headers: dict) -> tuple:
    """
    Plot the correlation matrix for the sensor variables
    """
    curr_data_df = data_dict[sensor]
    sensor_vars = sensor_headers[sensor]
    corr_matrix = curr_data_df[sensor_vars].corr()
    num_vars = len(sensor_vars)

    # print(f"Correlation matrix for {sensor}")
    # print(corr_matrix)

    fig, ax = plt.subplots(figsize=(num_vars + 1, num_vars + 1))
    plt.clf()
    # Note that matshow is not compatible with tight_layout
    plt.matshow(corr_matrix, fignum=fig.number,
                vmin=-1, vmax=1, cmap='PuOr')
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
                             sensor_headers: dict) -> tuple:
    """
    Plot the correlation scatter plot for the sensor variables
    """
    curr_data_df = data_dict[sensor]
    sensor_vars = sensor_headers[sensor]
    num_vars = len(sensor_vars)

    fig, axes = plt.subplots(nrows = num_vars, ncols=num_vars,
                             figsize=(2 * num_vars + 1, 2 * num_vars),
                             sharex='col', sharey='row')

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
                            event_datetimes: list = None) -> tuple:
    """
    Plot the histogram of the datetime values. Since the sensor data comes as
    a packet, we only need to plot the time of the packet.
    """
    curr_data_df = data_dict[sensor]
    datetime_values = curr_data_df['datetime']

    num_days = (datetime_values.iloc[-1] - datetime_values.iloc[0]).days + 1
    
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(datetime_values, bins=num_days * 24 * 4)

    plt.xticks(rotation=45)
    ax.set_xlabel('Date and Time')
    ax.set_ylabel(f"Number of measurements per 15 minutes")
    plt.title(f'Temporal Histogram of {sensor} readings')

    if event_datetimes is not None:
        for event_time in event_datetimes:
            ax.axvline(x=event_time, color='k', linestyle='--')

    highlight_nighttime(ax, curr_data_df)
    
    return fig, ax
