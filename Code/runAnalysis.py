import utilityFunctions as uf
import pandas as pd
import numpy as np
from datetime import datetime
import seaborn as sns
import matplotlib.pylab as plt
import matplotlib.dates as mdates
import folium

sns.set_palette("deep")
sns.set_color_codes("deep")
sns.set_context("notebook", font_scale=1.5, rc={"lines.linewidth": 2.5})
sns.set_style('whitegrid')

reAnalyze = False
remakePlots = False
if reAnalyze:
    # Connect to healthdata database
    connection = uf.create_db_connection('localhost', 'Rui', '***********',
                                         'healthdata', 5432)

    # Read data from PostgreSQL database table and load into a DataFrame instance
    workout_routes = pd.read_sql("select * from workout_routes", connection)
    workout_routes['altitude'] = workout_routes['altitude'] * 3.28084  # convert from m to ft
    heartRate = pd.read_sql("select * from heart_rate", connection)
    walkingSpeed = pd.read_sql("select * from walking_speed", connection)
    runningSpeed = pd.read_sql("select * from running_speed", connection)
    connection.close()

    totalDistanceList = []
    elevChangeList = []
    startTimeList = []
    totalTimeList = []
    # Run analysis
    for route_num in np.arange(1,workout_routes['workout_id'].max()+1):
        print("Analyzing Route " + str(route_num) + "/" + str(workout_routes['workout_id'].max()))

        # Compute total time, distance, and elevation change of each hike
        current_route = workout_routes[workout_routes['workout_id'] == route_num]
        startTime = current_route['time'].iloc[0]
        endTime = current_route['time'].iloc[-1]
        elevChangeFt = np.round(current_route['altitude'].max() - current_route['altitude'].min(),2)
        totalDistanceMi = uf.compute_total_distance_mi(current_route)
        totalTime = endTime - startTime

        # Gather results
        startTimeList.append(startTime)
        totalTimeList.append(totalTime)
        totalDistanceList.append(totalDistanceMi)
        elevChangeList.append(elevChangeFt)

        # Find heart rate and speed info for each hike
        current_route_heartRate = heartRate[(heartRate['time'] <= np.datetime64(endTime)) &
                                            (heartRate['time'] >= np.datetime64(startTime))]
        current_route_walkingSpeed = walkingSpeed[(walkingSpeed['time'] <= np.datetime64(endTime)) &
                                            (walkingSpeed['time'] >= np.datetime64(startTime))]
        current_route_runningSpeed = runningSpeed[(runningSpeed['time'] <= np.datetime64(endTime)) &
                                            (runningSpeed['time'] >= np.datetime64(startTime))]

        if remakePlots:
            print("Making plots for route number " + str(route_num) + "/" + str(workout_routes['workout_id'].max()))
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


    # Compute Summary
    summaryDict = {'time':startTimeList, 'total_time':totalTimeList,
                   'distance':totalDistanceMi, 'elevation_gain':elevChangeList}
    summary = pd.DataFrame(data=summaryDict)
    summary.to_pickle("../Data/dataframe_summary/summary.pkl")

# Load in summary if already computed
else:
    summary = pd.read_pickle("../Data/dataframe_summary/summary.pkl")

# Analyze summary
year = 2020
current_year_summary = summary[(summary['time'] >= np.datetime64(str(year)+"-01-01")) &
                                    (summary['time'] <= np.datetime64(str(year)+"-12-31"))]
print("Total time spent hiking in " + str(year) + ": " + str(current_year_summary['total_time'].sum()) + '.')
print("Total distance hiked in " + str(year) + ": " + str(current_year_summary['distance'].sum()) + ' miles.')
print("Total elevation gained in " + str(year) + ": " + str(current_year_summary['elevation_gain'].sum()) + ' ft.')

# Compute totals per month
months = np.arange(1,13)
totalTime_mos = []
totalDistance_mos = []
totalElevationGain_mos = []
for m in months:
    if m<12:
        current_month_summary = current_year_summary[
            (current_year_summary['time'] >= np.datetime64(str(year)+"-"+str(m).zfill(2)+"-01")) &
            (current_year_summary['time'] < np.datetime64(str(year)+"-"+str(m+1).zfill(2)+"-01"))]
    else:
        current_month_summary = current_year_summary[
            (current_year_summary['time'] >= np.datetime64(str(year) + "-" + str(m).zfill(2) + "-01"))]

    totalTime_mos.append(current_month_summary['total_time'].sum())
    totalDistance_mos.append(current_month_summary['distance'].sum())
    totalElevationGain_mos.append(current_month_summary['elevation_gain'].sum())

monthlySummaryDict = {'month':months, 'total_time':totalTime_mos,
                   'distance':totalDistance_mos, 'elevation_gain':totalElevationGain_mos}
monthly_summary =  pd.DataFrame(data=monthlySummaryDict)

# Plot monthly summary
fig, axes = plt.subplots(2,1,figsize=(10, 9))
fig.suptitle("Monthly Summary for " + str(year))
ax = sns.barplot(data=monthly_summary, x="month", y="distance", ax=axes[0], color="b")
# Add values above bars
for i, v in enumerate(np.round(monthly_summary['distance'],1)):
   ax.text(i, v + 0.2, str(v), ha='center', fontsize=12)
axes[0].set(ylabel='Distance Hiked (mi)')
axes[0].set(xlabel='Month')
axes[0].set_ylim([0,90])
axes[0].set_title("Total distance hiked " + ": "
                        + str(np.round(current_year_summary['distance'].sum(),2)) + " miles.")

ax = sns.barplot(data=monthly_summary, x="month", y="elevation_gain", ax=axes[1], color="y")
# Add values above bars
for i, v in enumerate(np.round(monthly_summary['elevation_gain'],1)):
   ax.text(i, v + 0.2, str(v), ha='center', fontsize=12)
axes[1].set(ylabel='Elevation Gained (ft)')
axes[1].set(xlabel='Month')
axes[1].set_ylim([0,11000])
axes[1].set_title("Total elevation gained " + ": "
                        + str(np.round(current_year_summary['elevation_gain'].sum(),1)) + " ft.")

plt.tight_layout()
plt.savefig('../Figures/monthlySummary/'+str(year)+'monthlySummary.png')