import pandas as pd
import sqlite3 as lite
import collections
import datetime
import matplotlib.pyplot as plt

con = lite.connect('citi_bike.db')
cur = con.cursor()

df = pd.read_sql_query("SELECT * FROM available_bikes ORDER BY execution_time",con,index_col='execution_time')

hour_change = collections.defaultdict(int)
for col in df.columns:
    station_vals = df[col].tolist()
    station_id = col[1:] #trim the "_"
    station_change = 0
    for k,v in enumerate(station_vals):
        if k < len(station_vals) - 1:
            try:
                station_change += abs(station_vals[k] - station_vals[k+1])
            except TypeError as e:
                pass
                #print("Warning - " + str(e))
    hour_change[int(station_id)] = station_change #convert the station id back to integer
    
                
def keywithmaxval(d):
    """Find the key with the greatest value"""
    return max(d, key=lambda k: d[k])

# assign the max key to max_station
max_station = keywithmaxval(hour_change)


#query sqlite for reference information
cur.execute("SELECT id, stationname, latitude, longitude FROM citibike_reference WHERE id = ?", (max_station,))
data = cur.fetchone()
print("\nThe most active station is station id %s at %s latitude: %s longitude: %s " % data)
print("\nWith %d bicycles coming and going in the hour between %s and %s" % (
    hour_change[max_station],
    datetime.datetime.fromtimestamp(int(df.index[0])).strftime('%Y-%m-%dT%H:%M:%S'),
    datetime.datetime.fromtimestamp(int(df.index[-1])).strftime('%Y-%m-%dT%H:%M:%S'),
))


# Data Visualization


# Bar Chart of Activity and Station ID
plt.figure(figsize=(16,8))
plt.bar(list(hour_change.keys()), list(hour_change.values()))
plt.xlabel("Station ID")
plt.ylabel("Activity (Total Number of Bicycles Taken Out or Returned")
plt.title("Activity in 1 hour v Station ID")
plt.savefig("bike_activity.png")

# Scatter Plot of Activity and Station Locations
coord = pd.read_sql_query("SELECT longitude, latitude FROM citibike_reference", con)
lon = coord["longitude"].tolist()
lat = coord["latitude"].tolist()
size = [s ** 1.5 for s in hour_change.values()]

plt.figure(figsize=(10, 10))
plt.scatter(lon, lat, s=size, alpha=0.5)
plt.scatter(data[3], data[2], s=hour_change[max_station] ** 1.5, alpha=1, c="r")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.title("One hour CitiBike activity")
plt.savefig("activity_scatter.png")

plt.figure(figsize=(10, 10))
plt.scatter(lon, lat, c=list(hour_change.values()), s=size, cmap=plt.cm.Oranges)
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.title("Coloured Scatter plot for one hour of activity")
plt.colorbar(plt.scatter(lon, lat, c=list(hour_change.values()), s=size, cmap=plt.cm.Oranges))
plt.savefig("activity_scatter_colored.png")