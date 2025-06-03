#!/usr/bin/env python
# Converted from earthkit-plots-intro.ipynb
# Modified to focus on Johannesburg, South Africa

import calendar
from datetime import timedelta
import numpy as np

import earthkit.data
import earthkit.climate
import earthkit.plots

earthkit.aggregate = earthkit.climate.aggregate

# Constants
DATA_PERIOD = (1979, 2023)
REFERENCE_PERIOD = (1991, 2020)
MONTH = "July"  # Change this for a different monthly anomaly

# Johannesburg coordinates
JOHANNESBURG_LAT = -26.2041
JOHANNESBURG_LON = 28.0473

# Load ERA5 monthly averaged reanalysis 2m temperature data
data = earthkit.data.from_source(
    'cds',
    'reanalysis-era5-single-levels-monthly-means',
    {
        'product_type': 'monthly_averaged_reanalysis',
        'variable': '2m_temperature',
        'year': list(range(DATA_PERIOD[0], DATA_PERIOD[1]+1)),
        'month': f"{list(calendar.month_name).index(MONTH):02d}",
        'time': '00:00',
    },
)

# Convert to Celsius - properly handle the data format
# First, convert to xarray dataset
ds = data.to_xarray()

# The variable name might be 't2m' for 2m temperature
# Let's check what variables we have
print("Available variables in dataset:", list(ds.data_vars))
var_name = '2t'  # This is usually the variable name for 2m temperature in ERA5
if var_name in ds:
    data_celsius = ds[var_name] - 273.15  # Convert Kelvin to Celsius
else:
    # Try to get the first variable if the expected name is not found
    var_name = list(ds.data_vars)[0]
    print(f"Using variable: {var_name}")
    data_celsius = ds[var_name] - 273.15  # Convert Kelvin to Celsius

# Let's examine the dataset structure
print("\nDataset dimensions:", data_celsius.dims)
print("Dataset coordinates:", list(data_celsius.coords))

# We might need to adjust our expectations for time selection

# Calculate monthly climatology (mean of each month over reference period)
month_idx = list(calendar.month_name).index(MONTH)

# We need to filter dates by the forecast_reference_time dimension
# First, let's extract the years from forecast_reference_time
time_values = data_celsius.forecast_reference_time.values
print("Time values sample:", time_values[0])

# Filter for the reference period and the correct month
ref_mask = []
for t in time_values:
    # Convert to datetime if it's not already
    if not hasattr(t, 'year'):
        from datetime import datetime
        if isinstance(t, (int, float)):
            # Convert from timestamp if necessary
            dt = datetime.utcfromtimestamp(t)
        else:
            # Otherwise parse as string
            dt = datetime.fromisoformat(str(t).replace('Z', '+00:00'))
    else:
        dt = t
    
    # Check if in reference period and correct month
    if (REFERENCE_PERIOD[0] <= dt.year <= REFERENCE_PERIOD[1]) and dt.month == month_idx:
        ref_mask.append(True)
    else:
        ref_mask.append(False)

# Apply the mask to get reference data
ref_data = data_celsius.isel(forecast_reference_time=ref_mask).mean(dim="forecast_reference_time")

# Calculate the anomaly for the latest year
latest_year = DATA_PERIOD[1]

# Find the latest data using forecast_reference_time
latest_mask = []
for t in time_values:
    # Convert to datetime if it's not already
    if not hasattr(t, 'year'):
        from datetime import datetime
        if isinstance(t, (int, float)):
            # Convert from timestamp if necessary
            dt = datetime.utcfromtimestamp(t)
        else:
            # Otherwise parse as string
            dt = datetime.fromisoformat(str(t).replace('Z', '+00:00'))
    else:
        dt = t
    
    # Check if latest year and correct month
    if dt.year == latest_year and dt.month == month_idx:
        latest_mask.append(True)
    else:
        latest_mask.append(False)

# Apply the mask to get latest data
latest_data = data_celsius.isel(forecast_reference_time=latest_mask)

# Calculate anomaly (latest minus reference)
anomaly = latest_data - ref_data

# Create a map visualization
fig = earthkit.plots.Map()

# Add coastlines and gridlines
fig.coastlines()
fig.gridlines()

# Create a style for temperature anomaly
temp_style = earthkit.plots.styles.Style(
    colors="RdBu_r",  # Red-Blue colormap, reversed
    levels=range(-5, 6, 1),  # Levels from -5 to 5 in steps of 1
    units="celsius",  # Temperature in Celsius
    extend="both"  # Extend colorbar in both directions
)

# Plot the temperature anomaly
fig.quickplot(
    anomaly.squeeze(),
    style=temp_style
)

# Add title and colorbar
fig.title(f"{MONTH} {latest_year} 2m temperature anomaly rel. to {REFERENCE_PERIOD}")
fig.legend(label="Temperature anomaly (°C)")

# Add a marker for Johannesburg
fig.scatter(x=[JOHANNESBURG_LON], y=[JOHANNESBURG_LAT], marker='o', color='black', s=80, label='Johannesburg')

# Show the plot (this would be displayed in Jupyter notebook)
fig.show()

# Create a second figure focusing on South Africa region
fig_sa = earthkit.plots.Map(domain=[16, 33, -35, -22])
fig_sa.coastlines()
fig_sa.gridlines()

# Plot the temperature anomaly for South Africa region
fig_sa.quickplot(
    anomaly.squeeze(),
    style=temp_style  # Reuse the same style object
)

# Add title and colorbar
fig_sa.title(f"{MONTH} {latest_year} temperature anomaly - South Africa region")
fig_sa.legend(label="Temperature anomaly (°C)")

# Add a marker for Johannesburg
fig_sa.scatter(x=[JOHANNESBURG_LON], y=[JOHANNESBURG_LAT], marker='o', color='black', s=80, label='Johannesburg')

# Extract data for Johannesburg specifically
def find_nearest_grid_point(data, lat, lon):
    # Find indices of the closest grid point
    lat_idx = np.abs(data.latitude.values - lat).argmin()
    lon_idx = np.abs(data.longitude.values - lon).argmin()
    return lat_idx, lon_idx

# Get temperature anomaly for Johannesburg
lat_idx, lon_idx = find_nearest_grid_point(anomaly, JOHANNESBURG_LAT, JOHANNESBURG_LON)
jburg_anomaly = anomaly.isel(latitude=lat_idx, longitude=lon_idx).values.item()

# Get the actual latest temperature for Johannesburg
jburg_latest_temp = latest_data.isel(latitude=lat_idx, longitude=lon_idx).values.item()

# Get the reference period average for Johannesburg
jburg_ref_temp = ref_data.isel(latitude=lat_idx, longitude=lon_idx).values.item()

print(f"\nJohannesburg, South Africa - {MONTH} {latest_year}:")
print(f"  Temperature: {jburg_latest_temp:.2f}°C")
print(f"  Reference period ({REFERENCE_PERIOD[0]}-{REFERENCE_PERIOD[1]}) average: {jburg_ref_temp:.2f}°C")
print(f"  Anomaly: {jburg_anomaly:.2f}°C")

# To save the plots to files, uncomment the following lines:
# fig.save("global_temperature_anomaly.png", dpi=300)
# fig_sa.save("south_africa_temperature_anomaly.png", dpi=300)

print(f"\nCreated temperature anomaly maps focusing on Johannesburg, South Africa")
