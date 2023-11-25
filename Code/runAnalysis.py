import utilityFunctions as uf
import pandas as pd
import numpy as np
from datetime import datetime
import seaborn as sns
import matplotlib.pylab as plt
import matplotlib.dates as mdates
import folium

sns.set_palette("deep")
sns.set_context("notebook", font_scale=1.5, rc={"lines.linewidth": 2.5})
sns.set_style('whitegrid')

# Connect to healthdata database
connection = uf.create_db_connection('localhost', 'Rui', 'rui123chen45',
                                     'healthdata', 5432)

# Read data from PostgreSQL database table and load into a DataFrame instance
workout_routes = pd.read_sql("select * from workout_routes", connection)
workout_routes['altitude'] = workout_routes['altitude'] * 3.28084  # convert from m to ft
heartRate = pd.read_sql("select * from heart_rate", connection)
walkingSpeed = pd.read_sql("select * from walking_speed", connection)
runningSpeed = pd.read_sql("select * from running_speed", connection)
connection.close()

for route_num in np.arange(1,workout_routes['workout_id'].max()+1):
    print("Making plots for route number " + str(route_num) + "/" + str(workout_routes['workout_id'].max()))

    # Compute total time, distance, and elevation change of each hike
    current_route = workout_routes[workout_routes['workout_id'] == route_num]
    startTime = current_route['time'].iloc[0]
    endTime = current_route['time'].iloc[-1]
    elevChangeFt = np.round(current_route['altitude'].max() - current_route['altitude'].min(),2)
    totalDistanceMi = uf.compute_total_distance_mi(current_route)
    totalTime = endTime - startTime
    #print('Total time (Days HH:MM:SS): ' + str(totalTime))
    #print('Total Distance: ' + str(totalDistanceMi) + ' miles')
    #print('Total Elevation Change: ' + str(elevChangeFt) + ' ft')

    # Find heart rate and speed info for each hike
    current_route_heartRate = heartRate[(heartRate['time'] <= np.datetime64(endTime)) &
                                        (heartRate['time'] >= np.datetime64(startTime))]
    current_route_walkingSpeed = walkingSpeed[(walkingSpeed['time'] <= np.datetime64(endTime)) &
                                        (walkingSpeed['time'] >= np.datetime64(startTime))]
    current_route_runningSpeed = runningSpeed[(runningSpeed['time'] <= np.datetime64(endTime)) &
                                        (runningSpeed['time'] >= np.datetime64(startTime))]

    # Plot
    fig, axes = plt.subplots(3,1,sharex = True,figsize=(10, 8))
    fig.suptitle(str(startTime.date()))
    sns.lineplot(ax=axes[0], x = "time", y = "altitude", data = current_route, color='y')
    axes[0].fill_between(current_route["time"], current_route["altitude"], color='y', alpha=0.2)
    axes[0].set(ylabel='Elevation (ft)')
    axes[0].set_ylim([0, current_route["altitude"].max()+50])

    if not current_route_walkingSpeed.empty:
        sns.lineplot(ax=axes[1], x = "time", y = "speed", data = current_route_walkingSpeed, marker="o")
        axes[1].set_ylim([0, current_route_walkingSpeed["speed"].max() + 3])
    elif not current_route_runningSpeed.empty:
        sns.lineplot(ax=axes[1], x="time", y="speed", data=current_route_runningSpeed, marker="o")
        axes[1].set_ylim([0, current_route_runningSpeed["speed"].max() + 3])
    else:
        axes[1].text(0.5, 0.5, 'NO DATA', horizontalalignment='center',
                     verticalalignment='center', transform=axes[1].transAxes)
    axes[1].set(ylabel='Speed (mph)')

    if not current_route_heartRate.empty:
        sns.lineplot(ax=axes[2], x = "time", y = "heart_rate", data = current_route_heartRate, marker="o", color='r')
        axes[2].set_ylim([40, current_route_heartRate["heart_rate"].max() + 30])
    else:
        axes[2].text(0.5, 0.5, 'NO DATA', horizontalalignment='center',
                     verticalalignment='center', transform=axes[2].transAxes)
    axes[2].set(ylabel='Heart Rate (bpm)')
    axes[2].set_xlim([startTime, endTime])
    axes[2].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

    plt.tight_layout()
    plt.savefig('../Figures/' + str(route_num).zfill(4) + '.png')
    plt.close()

    # Create route map with zoom level 15
    min_lat = current_route['latitude'].min()
    max_lat = current_route['latitude'].max()
    min_lon = current_route['longitude'].min()
    max_lon = current_route['longitude'].max()
    map = folium.Map( location=[min_lat + (max_lat - min_lat) / 2, min_lon + (max_lon - min_lon) / 2],
                      zoom_start=15, control_scale=True,)
    points = list(zip(current_route['latitude'], current_route['longitude']))
    folium.PolyLine(locations=points, color="red", weight=2.5, opacity=1).add_to(map)

    map_title = ("Time Taken: " + str(totalTime)[7:] + ". Distance: " + str(totalDistanceMi) +
                 " miles. Elevation Change: " + str(elevChangeFt) +" ft.")
    title_html = f'<h1 style="position:absolute;z-index:100000;left:10vw" >{map_title}</h1>'
    map.get_root().html.add_child(folium.Element(title_html))
    map.save('../Maps/' + str(route_num).zfill(4) + '.html')
