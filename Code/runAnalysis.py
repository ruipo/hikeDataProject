import utilityFunctions as uf
import pandas as pd
import numpy as np
from datetime import datetime
import seaborn as sns
import matplotlib.pylab as plt
import folium
# Connect to healthdata database
connection = uf.create_db_connection('localhost', 'Rui', 'rui123chen45',
                                     'healthdata', 5432)

# Read data from PostgreSQL database table and load into a DataFrame instance
workout_routes = pd.read_sql("select * from workout_routes", connection)
heartRate = pd.read_sql("select * from heart_rate", connection)
walkingSpeed = pd.read_sql("select * from walking_speed", connection)
runningSpeed = pd.read_sql("select * from running_speed", connection)
connection.close()

# Compute total time, distance, and elevation change of each hike
current_route = workout_routes[workout_routes['workout_id'] == 69]
startTime = current_route['time'].iloc[0]
endTime = current_route['time'].iloc[-1]
elevChangeFt = np.round(current_route['altitude'].max() - current_route['altitude'].min(),2)
totalDistanceMi = uf.compute_total_distance_mi(current_route)
totalTime = endTime - startTime
print('Total time (Days HH:MM:SS): ' + str(totalTime))
print('Total Distance: ' + str(totalDistanceMi) + ' miles')
print('Total Elevation Change: ' + str(elevChangeFt) + ' ft')

# Find heart rate and speed info for each hike
current_route_heartRate = heartRate[(heartRate['time'] <= np.datetime64(endTime)) &
                                    (heartRate['time'] >= np.datetime64(startTime))]
current_route_walkingSpeed = walkingSpeed[(walkingSpeed['time'] <= np.datetime64(endTime)) &
                                    (walkingSpeed['time'] >= np.datetime64(startTime))]
current_route_runningSpeed = runningSpeed[(runningSpeed['time'] <= np.datetime64(endTime)) &
                                    (runningSpeed['time'] >= np.datetime64(startTime))]

# Plot
plt.figure(figsize=(12, 6))
ax1 = plt.subplot(3,2,2)
sns.lineplot(x = "time", y = "altitude", data = current_route)
ax2 = plt.subplot(3,2,4)
sns.lineplot(x = "time", y = "heart_rate", data = current_route_heartRate)
ax3 = plt.subplot(3,2,6)
sns.lineplot(x = "time", y = "speed", data = current_route_walkingSpeed)
ax4 = plt.subplot(1,2,1)
## Create empty map with zoom level 16
min_lat = current_route['latitude'].min()
max_lat = current_route['latitude'].max()
min_lon = current_route['longitude'].min()
max_lon = current_route['longitude'].max()
map = folium.Map( location=[min_lat + (max_lat - min_lat) / 2, min_lon + (max_lon - min_lon) / 2], zoom_start=16)
points = list(zip(current_route['latitude'], current_route['longitude']))
folium.PolyLine(locations=points, color="red", weight=2.5, opacity=1).add_to(map)
axes = [ax1, ax2, ax3, ax4]
plt.show()
map.show_in_browser()