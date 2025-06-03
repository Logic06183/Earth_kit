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
ref_data = data_celsius.sel(
    time=lambda t: (t.dt.year >= REFERENCE_PERIOD[0]) & 
                  (t.dt.year <= REFERENCE_PERIOD[1]) &
                  (t.dt.month == month_idx)
)
ref_mean = ref_data.mean(dim="time")

# Calculate the anomaly for the latest year
latest_year = DATA_PERIOD[1]
latest_data = data_celsius.sel(
    time=lambda t: (t.dt.year == latest_year) & (t.dt.month == month_idx)
)
anomaly = latest_data - ref_mean

# Create a figure with a map projection
fig = earthkit.plots.geomap(projection="PlateCarree")

# Add coastlines to the map
fig.add_coastlines()

# Add gridlines to the map
fig.add_gridlines()

# Plot the temperature anomaly
fig.add_data(
    anomaly.squeeze(),
    colorbar_label=f"Temperature anomaly (°C)",
    title=f"{MONTH} {latest_year} 2m temperature anomaly rel. to {REFERENCE_PERIOD}",
    style={
        "contour": False,
        "colors": "RdBu_r",
        "vmin": -5,
        "vmax": 5,
    }
)

# Add a marker for Johannesburg
fig.add_marker(lon=JOHANNESBURG_LON, lat=JOHANNESBURG_LAT, marker='o', color='black', markersize=8, label='Johannesburg')

# Show the plot (this would be displayed in Jupyter notebook)
fig.show()

# Create a second figure focusing on South Africa region
fig_sa = earthkit.plots.geomap(projection="PlateCarree", extent=[16, 33, -35, -22])
fig_sa.add_coastlines()
fig_sa.add_gridlines()

# Plot the temperature anomaly for South Africa region
fig_sa.add_data(
    anomaly.squeeze(),
    colorbar_label=f"Temperature anomaly (°C)",
    title=f"{MONTH} {latest_year} temperature anomaly - South Africa region",
    style={
        "contour": False,
        "colors": "RdBu_r",
        "vmin": -5,
        "vmax": 5,
    }
)

# Add a marker for Johannesburg
fig_sa.add_marker(lon=JOHANNESBURG_LON, lat=JOHANNESBURG_LAT, marker='o', color='black', markersize=8, label='Johannesburg')

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
jburg_ref_temp = ref_mean.isel(latitude=lat_idx, longitude=lon_idx).values.item()

print(f"\nJohannesburg, South Africa - {MONTH} {latest_year}:")
print(f"  Temperature: {jburg_latest_temp:.2f}°C")
print(f"  Reference period ({REFERENCE_PERIOD[0]}-{REFERENCE_PERIOD[1]}) average: {jburg_ref_temp:.2f}°C")
print(f"  Anomaly: {jburg_anomaly:.2f}°C")

# To save the plots to files, uncomment the following lines:
# fig.save("global_temperature_anomaly.png", dpi=300)
# fig_sa.save("south_africa_temperature_anomaly.png", dpi=300)

print(f"\nCreated temperature anomaly maps focusing on Johannesburg, South Africa")
