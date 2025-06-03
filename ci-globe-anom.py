#!/usr/bin/env python
# Converted from ci-globe-anom.ipynb

import earthkit.data
import earthkit.maps

# Load climate change anomaly data for surface air temperature for July 2023
data = earthkit.data.from_source(
    'cds', 'ecv-for-climate-change',
    {
        'format': 'zip',
        'variable': 'surface_air_temperature',
        'product_type': 'anomaly',
        'climate_reference_period': '1991_2020',
        'time_aggregation': '1_month_mean',
        'year': '2023',
        'month': '07',
        'origin': 'era5',
    },
)

# Extract the first field from the data
field = data[0]

# Create a world map visualization using earthkit.maps
fig = earthkit.maps.WorldMap(central_longitude=0)

# Add coastlines to the map
fig.add_feature.coastlines()

# Add country borders
fig.add_feature.borders()

# Add the temperature anomaly data to the map
fig.plot(
    field, 
    vmin=-4, 
    vmax=4, 
    cmap="RdBu_r", 
    colorbar_title="Temperature anomaly (K)",
    title="Surface Air Temperature Anomaly - July 2023 (ERA5)"
)

# Show the plot (this would be displayed in Jupyter notebook)
fig.show()

# To save the plot to a file, uncomment the following line:
# fig.save("temperature_anomaly_globe_july_2023.png", dpi=300)

print("Created global temperature anomaly map for July 2023 (ERA5 data)")
