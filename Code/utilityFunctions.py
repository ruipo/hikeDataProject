import psycopg2 as psql
import geopy.distance as gpd
import numpy as np

# Function to connect to SQL database
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


# Function to execute SQL command
def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        # print('query executed successfully!')

    except Exception as err:
        print("Error executing query: " + str(err) + "...")


# Function to compute total distance travelled during a route dataframe
def compute_total_distance_mi(route):
    totalDistanceMi = 0
    route = route.reset_index(drop=True)
    for idx in np.arange(0, len(route['workout_id']) - 1):
        latStart = route['latitude'][idx]
        lonStart = route['longitude'][idx]
        latEnd = route['latitude'][idx + 1]
        lonEnd = route['longitude'][idx + 1]

        dist = gpd.geodesic((latStart, lonStart), (latEnd, lonEnd)).miles
        totalDistanceMi += dist

    return(np.round(totalDistanceMi,2))