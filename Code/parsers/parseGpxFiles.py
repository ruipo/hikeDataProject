import os
from gpx_converter import Converter

gpxFolderPath = '/Users/Rui/Documents/hikeData/Data/raw/workout-routes'

for filename in os.scandir(gpxFolderPath):
    if filename.is_file():
        Converter(input_file=filename.path).gpx_to_csv(output_file='/Users/Rui/Documents/hikeData/Data/csv'
                                                                   '/workoutRoutes/'
                                                                   + filename.name[0:-3] + 'csv')
