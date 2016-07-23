import time
from dateutil.parser import parse
import collections
import sqlite3 as lite
import requests
import datetime

con = lite.connect('citi_bike.db')
cur = con.cursor()

r = requests.get('http://www.citibikenyc.com/stations/json')
from pandas.io.json import json_normalize
df = json_normalize(r.json()['stationBeanList'])

#extract the column from the DataFrame and put them into a list
station_ids = df['id'].tolist() 

#add the '_' to the station name and also add the data type for SQLite
station_ids = ['_' + str(x) + ' INT' for x in station_ids]

#create the table
#in this case, we're concatenating the string and joining all the station ids (now with '_' and 'INT' added)
with con:
    cur.execute("CREATE TABLE available_bikes ( execution_time INT, " +  ", ".join(station_ids) + ");")

    cur.execute("DELETE FROM available_bikes")
for i in range(60):
    r = requests.get('http://www.citibikenyc.com/stations/json')
    exec_time = parse(r.json()['executionTime']).strftime("%Y-%m-%dT%H:%M:%S")

    cur.execute('INSERT INTO available_bikes (execution_time) VALUES (?)', ((exec_time - datetime.datetime(1970,1,1)).total_seconds(),))

    for station in r.json()['stationBeanList']:
        cur.execute("UPDATE available_bikes SET _%d = %d WHERE execution_time = %s" % (station['id'], station['availableBikes'], (exec_time - datetime.datetime(1970,1,1)).total_seconds()))
    con.commit()

    time.sleep(60)

con.close() #close the database connection when done