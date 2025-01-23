# %%
import pandas as pd
import numpy as np

# Load data
df = pd.read_csv("/Users/mortunco/Desktop/Tunc_Sukru/evo_project/athena_output/trips_jan3rd.csv")

# Convert 'time1' to datetime
df['time1'] = pd.to_datetime(df['time1'], errors='coerce')
df['binned_time'] = df['time1'].dt.floor('8H')

# Annotation 1: binned_day_time
def format_binned_time(row):
    start_time = row['binned_time']
    end_time = start_time + pd.Timedelta(hours=8)
    day = start_time.strftime('%b %d').lstrip('0').replace(' 0', ' ')
    start_str = start_time.strftime('%H:%M')
    end_str = end_time.strftime('%H:%M')
    return f"{day} {start_str} - {end_str}"

df['binned_day_time'] = df.apply(format_binned_time, axis=1)

# Annotation 2: Day and Morning, Afternoon, Night Labels
def day_period_only_label(row):
    hour = row['time1'].hour
    if 0 <= hour < 12:
        period = "Morning"
    elif 12 <= hour < 18:
        period = "Afternoon"
    else:
        period = "Night"
    return f"{period}"
df['day_period'] = df.apply(day_period_only_label, axis=1)

# Annotation 2: Day and Morning, Afternoon, Night Labels
def day_period_label(row):
    hour = row['time1'].hour
    if 0 <= hour < 12:
        period = "Morning"
    elif 12 <= hour < 18:
        period = "Afternoon"
    else:
        period = "Night"
    return f"{row['binned_time'].strftime('%b %d')} {period}"

# Function to generate just the day
def get_day(row):
    return row['binned_time'].strftime('%b %d').lstrip('0').replace(' 0', ' ')

df['day_label'] = df.apply(get_day, axis=1)

def day_period_label(row):
    hour = row['time1'].hour
    if 0 <= hour < 12:
        period = "Morning"
    elif 12 <= hour < 18:
        period = "Afternoon"
    else:
        period = "Night"
    return f"{row['binned_time'].strftime('%b %d')}"

df['day_period_label'] = df.apply(day_period_label, axis=1)

# Add static location labels
df["label_lat"] = 49.307515
df["label_lon"] = -123.251125

# Drop unused columns
df.drop(["lat2", "long2", "time2"], inplace=True, axis=1)

df[["binned_time","binned_day_time","label_lat","label_lon","day_period_label","day_period","day_label"]].drop_duplicates().to_csv("/Users/mortunco/Desktop/Tunc_Sukru/evo_project/athena_output/trips_jan3rd_annotation_for_foursquare.csv",index=False)
df.drop(["binned_time","binned_day_time","day_period_label"],axis=1).to_csv("/Users/mortunco/Desktop/Tunc_Sukru/evo_project/athena_output/trips_jan3rd_for_foursquare.csv",index=False)

# %%
