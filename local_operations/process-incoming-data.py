# %%
import pandas as pd
import numpy as np
import json
import glob
import os
import shutil
from datetime import datetime
import sys
import json
import math

def haversine(coord1, coord2):
    """
    Calculate the great-circle distance between two points on the Earth's surface.

    Parameters:
    coord1, coord2: Tuples containing the latitude and longitude of the two points in decimal degrees.

    Returns:
    Distance between the two points in kilometers.
    """
    # Radius of the Earth in kilometers
    R = 6371.0

    # Unpack latitude/longitude from input tuples
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Differences in coordinates
    delta_lat = lat2_rad - lat1_rad
    delta_lon = lon2_rad - lon1_rad

    # Haversine formula
    a = (math.sin(delta_lat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Distance in kilometers
    distance = R * c
    return distance


test_mode = False
if test_mode:
    json_file_path="test_car_status.json"
    # Sort the files by the timestamp in their filename
    snapshot_paths = sorted(
        glob.glob("testing/evo_*.csv"),
        key=lambda x: datetime.strptime(os.path.basename(x), "evo_%Y_%m_%d_%H_%M.csv")
    )
else:
    json_file_path="car_status.json" ### this file is very important. It keeps the last EVOs that did not go through a trip. In this way, we can calculate any batch any time with just checking this file.
    # Sort the files by the timestamp in their filename
    snapshot_paths = sorted(
        glob.glob("rawdata/evo_*.csv"),
        key=lambda x: datetime.strptime(os.path.basename(x), "evo_%Y_%m_%d_%H_%M.csv")
    )

if os.path.exists(json_file_path):
    with open(json_file_path, 'r') as json_file:
        car_status = json.load(json_file)
else:
    # File doesn't exist, create an empty dictionary
    car_status = {}

if len(snapshot_paths) == 0:
    raise ValueError("No file found in snapshots. Exitting.")
else:
    print(f"found {len(snapshot_paths)} new studies.")
    
trips=[]
for snapshot_path in snapshot_paths:
    print(snapshot_path)
    snapshot=pd.read_csv(snapshot_path)
    for _,car in snapshot.iterrows():
        if car["plate"] not in car_status:
            car_status[car["plate"]] = {"from_lat" : car["lat"], "from_lon" : car["lon"], "from_energylevel": car["energyLevel"], "from_date" :car["retrieved_datestamp"], "from_time":car["retrieved_timestamp"]}
        else:
            if car_status[car["plate"]]["from_lat"] == car["lat"] and car_status[car["plate"]]["from_lon"] == car["lon"]:
                car["from_date"] = car["retrieved_datestamp"]
                car["from_time"] = car["retrieved_timestamp"]
            else:
                trips.append([
                    car["plate"],
                    car_status[car["plate"]]["from_lat"],
                    car_status[car["plate"]]["from_lon"],
                    car_status[car["plate"]]["from_date"],
                    car_status[car["plate"]]["from_time"],
                    car_status[car["plate"]]["from_energylevel"],
                    car["lat"], # ,car_status["to_lat"],
                    car["lon"], #car_status["to_long"],
                    car["retrieved_datestamp"], #car_status["to_data"],
                    car["retrieved_timestamp"], #car_status["to_time"],
                    car["energyLevel"], #car_status["to_energylevel"]
                    haversine((car_status[car["plate"]]["from_lat"],car_status[car["plate"]]["from_lon"]), (car["lat"],car["lon"]))
                ])

                #When the trip is over
                car_status[car["plate"]]["from_lat"] = car["lat"] #car_status["to_lat"],
                car_status[car["plate"]]["from_lon"] = car["lon"] #car_status["to_long"],
                car_status[car["plate"]]["from_date"] = car["retrieved_datestamp"] #car_status["to_data"],
                car_status[car["plate"]]["from_time"] = car["retrieved_timestamp"] #car_status["to_time"],
                car_status[car["plate"]]["from_energylevel"] = car["energyLevel"] #car_status["to_energylevel"]
                
                #car_status.pop(car["plate"], None)
    if not test_mode:
        shutil.move(snapshot_path, "processed_data")

    with open(json_file_path, 'w') as json_file:
         json.dump(car_status, json_file, indent=4)

