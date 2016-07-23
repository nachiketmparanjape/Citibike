import requests
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style="whitegrid", color_codes=True)

#to fetch online data from a json file
r = requests.get('http://www.citibikenyc.com/stations/json')

#Prepare a keys' list for the keys inside stationBeanList - list of a station's attributes at a certain point in time.
#Extract Nested Keys

key_list = []

for station in r.json()['stationBeanList']:
    for key in station.keys():
        if key not in key_list:
            key_list.append(key)
            
#Put the data in a pandas DataFrame
from pandas.io.json import json_normalize
df = json_normalize(r.json()['stationBeanList'])

#Get a visual overview of the data / distributions

df['availableBikes'].hist(bins=100)
plt.show()
df['sv'] = df['statusValue'].astype('category') #Setting a catergorical variable in pandas
sns.factorplot(data=df,x='statusValue',kind='count') #Visualizing Categorical Data Using Seaborn

#Get Statistical Overview of the data
df['totalDocks'].mean()
condition = (df['statusValue']=='In Service')
df[condition]['totalDocks'].mean()

#SQL database Creation

import sqlite3 as lite

con = lite.connect('citi_bike.db')
cur = con.cursor()

with con:
    cur.execute('CREATE TABLE citibike_reference (id INT PRIMARY KEY, totalDocks INT, city TEXT, altitude INT, stAddress2 TEXT, longitude NUMERIC, postalCode TEXT, testStation TEXT, stAddress1 TEXT, stationName TEXT, landMark TEXT, latitude NUMERIC, location TEXT )')

##TABLE NO 1## REFERENCE TABLE
#prepared SQL statement we're going to execute over and over again
sql = "INSERT INTO citibike_reference (id, totalDocks, city, altitude, stAddress2, longitude, postalCode, testStation, stAddress1, stationName, landMark, latitude, location) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)"

#for loop to populate values in the database
with con:
    for station in r.json()['stationBeanList']:
        #id, totalDocks, city, altitude, stAddress2, longitude, postalCode, testStation, stAddress1, stationName, landMark, latitude, location)
        cur.execute(sql,(station['id'],station['totalDocks'],station['city'],station['altitude'],station['stAddress2'],station['longitude'],station['postalCode'],station['testStation'],station['stAddress1'],station['stationName'],station['landMark'],station['latitude'],station['location']))