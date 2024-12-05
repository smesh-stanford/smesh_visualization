import matplotlib.pyplot as plt
import datetime

# try:
#     import astral          # For sunrise and sunset times
#     astral_available = True
#     print("Astral library loaded")
# except ImportError:
#     astral_available = False
#     print("Astral library not available")


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

    # Fill in the x-axis with grey from 6pm to 6am to represent night time
    # print("Datetimes")
    # print(curr_data_df['datetime'])
    earliest_day = curr_data_df['datetime'].iloc[0].date()
    latest_day = curr_data_df['datetime'].iloc[-1].date()

    sunrise = datetime.datetime.strptime("06:00:00", "%H:%M:%S").time() 
    sunset = datetime.datetime.strptime("18:00:00", "%H:%M:%S").time()

    # Print each day between the earliest and latest day
    num_days = (latest_day - earliest_day).days + 2
    for var_id in range(len(sensor_vars)):
        for i in range(num_days):
            curr_day = earliest_day + datetime.timedelta(days=i)

            curr_sunrise_datetime = datetime.datetime.combine(curr_day, sunrise)
            curr_sunset_datetime = datetime.datetime.combine(curr_day, sunset)
            axes[var_id].axvspan(
                            curr_sunset_datetime - datetime.timedelta(days=1), 
                            curr_sunrise_datetime, 
                            color='grey', alpha=0.25, zorder=0)

    # if astral_available:
    #     city = astral.LocationInfo("City", "Region", "Country", 0, 0)
    #     sun = city.sun(date=datetime.datetime.now(), local=True)
    #     sunrise = sun['sunrise']
    #     sunset = sun['sunset']
    #     axes[0].axvspan(sunset, sunrise + datetime.timedelta(days=1), color='grey', alpha=0.5)

    plt.xlim([minx, maxx])

    plt.tight_layout()

    return fig, axes
