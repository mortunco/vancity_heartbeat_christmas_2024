# %%
import pandas as pd
import numpy as np

# Read the input data
df = pd.read_csv("/Users/mortunco/Desktop/Tunc_Sukru/evo_project/athena_output/trips_jan3rd_for_foursquare.csv")

# Convert 'time1' to datetime for sorting and aggregation
df['time1'] = pd.to_datetime(df['time1'], errors='coerce')
df=df[(df["day_label"] != "Dec 5") & (df["day_label"] != "Jan 3")].copy()

# Aggregate data by 'day_label' and 'day_period'
df_summary = (
    df.groupby(["day_label"])
    .agg(average_time=("time1", "mean"), count=("time1", "size"))
    .reset_index()
)

# Rectangle coordinates
top_left = (49.328426, -123.267230)
top_right = (49.328426, -123.178223)
bottom_left = (49.284663, -123.267230)

# Calculate latitude and longitude ranges
longitude_range = np.linspace(top_left[1], top_right[1], len(df_summary['day_label'].unique()) + 1)  # N+1 for X-axis
y_min, y_max = bottom_left[0], top_left[0]
latitude_range = y_max - y_min

# Sort by average_time to map earliest dates to the most west point
df_summary = df_summary.sort_values("average_time", ascending=True)

# Dynamically calculate the maximum count for normalization
max_count = df_summary['count'].max()

# Map coordinates
df_summary['longitude'] = np.linspace(top_left[1], top_right[1], len(df_summary))  # Assign longitudes in sorted order
df_summary['latitude'] = df_summary['count'].apply(lambda y: y_min + (y / max_count) * latitude_range)

df_summary["trips_dummy_variable"]="Trips"
# Save the data layer
data_file = "/Users/mortunco/Desktop/Tunc_Sukru/evo_project/athena_output/data_layer.csv"
df_summary.to_csv(data_file, index=False)

# %%
import pandas as pd
import numpy as np

# Input file for data layer
data_file = "/Users/mortunco/Desktop/Tunc_Sukru/evo_project/athena_output/data_layer.csv"

# Read the data layer
df = pd.read_csv(data_file)

# Determine ranges for X and Y axis
x_min, x_max = df['longitude'].min(), df['longitude'].max()
y_min, y_max = df['latitude'].min(), df['latitude'].max()

# X-axis: One tick for each unique day_label
x_ticks = df.groupby("day_label").first("longitude")["longitude"]
x_ticks = np.sort(x_ticks)  # Ensure sorted order

# Y-axis: Percentile-based ticks (5 evenly spaced)
y_ticks = np.linspace(y_min, y_max, 6)  # 0%, 25%, 50%, 75%, 100%

# Add a small margin for the X and Y axis lines
x_margin = 0.005  # Small horizontal margin
y_margin = 0.005  # Small vertical margin

# Define X-axis line
x_axis_line = {
    "x1": x_min - x_margin,
    "y1": y_min,
    "x2": x_max + x_margin,
    "y2": y_min
}

# Define Y-axis line
y_axis_line = {
    "x1": x_min,
    "y1": y_min - y_margin,
    "x2": x_min,
    "y2": y_max + y_margin
}

# Combine lines into a DataFrame
plot_lines = pd.DataFrame([x_axis_line, y_axis_line])

# Save plot lines to CSV
plot_lines_file = "/Users/mortunco/Desktop/Tunc_Sukru/evo_project/athena_output/plot_lines.csv"
plot_lines.to_csv(plot_lines_file, index=False)

# Prepare axis ticks
# X-axis ticks: All have the same latitude (y_min)
x_axis_ticks = [{"longitude": lon, "latitude": y_min, "label": None} for lon in x_ticks]

# Y-axis ticks: All have the same longitude (x_min)
y_axis_ticks = [{"longitude": x_min, "latitude": lat, "label": None} for lat in y_ticks]

# Map Y-axis labels to corresponding count values using df_summary
df_summary = df.groupby(["latitude"]).agg(count=("count", "mean")).reset_index()

# Find the closest latitude in df_summary for each Y-axis tick
for tick in y_axis_ticks:
    closest_index = (df_summary["latitude"] - tick["latitude"]).abs().idxmin()
    tick["label"] = int(df_summary.loc[closest_index, "count"])

# Combine X and Y ticks into a single DataFrame
axis_ticks = pd.DataFrame(y_axis_ticks)

# Save axis ticks to CSV
axis_ticks_file = "/Users/mortunco/Desktop/Tunc_Sukru/evo_project/athena_output/axis_ticks.csv"
axis_ticks.to_csv(axis_ticks_file, index=False)

# Print results for verification
print(f"Plot lines saved to: {plot_lines_file}")
print(plot_lines)
print(f"Axis ticks saved to: {axis_ticks_file}")
print(axis_ticks)


# %%
