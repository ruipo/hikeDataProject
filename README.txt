Steps to run hike data analysis:

1. Export Apple health data from health app
2. Save xml files and workout route folder to '/Users/Rui/Documents/hikeData/Data/raw/'
3. Clear files in all directories in '/Users/Rui/Documents/hikeData/Data/csv/'
4. Run parseAppleHealthData.py
5. Run parseGpxFiles.py
6. Connect to HikeData database through terminal and drop all tables (\d to view tables, DROP TABLE NAME; to drop tables)
7. Run createSqlDatabase.py
8. Run runAnalysis.py, setting reAnalyze and remakePlots to True