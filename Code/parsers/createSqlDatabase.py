import psycopg2 as psql
import pandas as pd
import os


def create_db_connection(host_name, user_name, user_pwd, db_name, db_port):
    connection = None
    try:
        connection = psql.connect(database=db_name,
                                  host=host_name,
                                  user=user_name,
                                  password=user_pwd,
                                  port=db_port)
        print('Successfully connected to database!')
    except Exception as err:
        print("Error connecting to database: " + str(err) + "...")
    return connection


def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        # print('query executed successfully!')

    except Exception as err:
        print("Error executing query: " + str(err) + "...")


# Connect to healthdata database
connection = create_db_connection('localhost', 'Rui', '**********',
                                  'healthdata', 5432)


# Create heartRate, walkingSpeed, runningSpeed tables
query = """
CREATE TABLE heart_rate (
time TIMESTAMP NOT NULL,
heart_rate DECIMAL(10,6) NOT NULL);
"""
execute_query(connection, query)
connection.commit()

query = """
CREATE TABLE walking_speed (
time TIMESTAMP NOT NULL,
speed DECIMAL(10,6) NOT NULL);
"""
execute_query(connection, query)
connection.commit()

query = """
CREATE TABLE running_speed (
time TIMESTAMP NOT NULL,
speed DECIMAL(10,6) NOT NULL);
"""
execute_query(connection, query)
connection.commit()

# Populate heart_rate table with csv data
dataFile = '/Users/Rui/Documents/hikeData/Data/csv/healthStats/HeartRate.csv'

print('Reading in heart rate data ...')
data = pd.read_csv(dataFile)
for tInd in range(0, len(data) - 1):
    pop_heart_rate = "INSERT INTO heart_rate VALUES " + \
                     "('" + str(data.startDate[tInd]) + "', '" \
                     + str(data.value[tInd]) + "');"
    execute_query(connection, pop_heart_rate)

# Populate walkingSpeed table with csv data
dataFile = '/Users/Rui/Documents/hikeData/Data/csv/healthStats/WalkingSpeed.csv'

print('Reading in walking speed data ...')
data = pd.read_csv(dataFile)
for tInd in range(0, len(data) - 1):
    pop_walking_speed = "INSERT INTO walking_speed VALUES " + \
                     "('" + str(data.startDate[tInd]) + "', '" \
                     + str(data.value[tInd]) + "');"
    execute_query(connection, pop_walking_speed)


# Populate runningSpeed table with csv data
dataFile = '/Users/Rui/Documents/hikeData/Data/csv/healthStats/RunningSpeed.csv'

print('Reading in running speed data ...')
data = pd.read_csv(dataFile)
for tInd in range(0, len(data) - 1):
    pop_running_speed = "INSERT INTO running_speed VALUES " + \
                     "('" + str(data.startDate[tInd]) + "', '" \
                     + str(data.value[tInd]) + "');"
    execute_query(connection, pop_running_speed)


# Create workoutRoutes table
query = """
CREATE TABLE workout_routes (
workout_id INT NOT NULL,
time TIMESTAMP NOT NULL,
latitude DECIMAL(10,6) NOT NULL,
longitude DECIMAL(10,6) NOT NULL,
altitude DECIMAL(10,6) NOT NULL );
"""
execute_query(connection, query)
connection.commit()

# Populate workoutRoutes table with csv data
workOutRoutesPath = '/Users/Rui/Documents/hikeData/Data/csv/workoutRoutes/'
workOutRoutesDir = os.listdir(workOutRoutesPath)
workOutFiles = [f for f in workOutRoutesDir if os.path.isfile(os.path.join(workOutRoutesPath, f))]
workOutID = 1

for f in workOutFiles:
    print('Reading in data files ' + str(workOutID) + '/' + str(len(workOutFiles)) + '...')
    data = pd.read_csv(os.path.join(workOutRoutesPath, f))
    for tInd in range(0, len(data) - 1):
        pop_workout_routes = "INSERT INTO workout_routes VALUES " + \
                             "(" + str(workOutID) + ", '" + str(data.time[tInd]) + "', '" \
                             + str(data.latitude[tInd]) + "', '" + str(data.longitude[tInd]) \
                             + "', '" + str(data.altitude[tInd]) + "');"
        execute_query(connection, pop_workout_routes)
    workOutID += 1

