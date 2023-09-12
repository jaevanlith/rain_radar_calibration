import pandas as pd
import numpy as np
import rasterio
import warnings
warnings.filterwarnings("ignore")

# ONLY FOR TESTING (set to None while running)
NROWS = 100

def load_radar_data(radar_data_path):
    '''
    Method to load radar data from csv files.
    '''

    # Load sattaship raster
    raster = radar_data_path + '/extract_radarpixel/raster_radar_sattahip.tif'

    # Load input coordinates
    rain_gauge_coords = pd.read_excel(radar_data_path + '/extract_radarpixel/raingauge_coordinate.xlsx', sheet_name='Sheet1', nrows=NROWS)
    rain_gauge_coords['pixel_x'] = np.nan
    rain_gauge_coords['pixel_y'] = np.nan

    # Loop over all stations
    for i in rain_gauge_coords.index:
        # Retrieve latitude and longitude 
        lat = float(rain_gauge_coords['lat'].iloc[i])
        lon = float(rain_gauge_coords['long'].iloc[i])

        # Map coordinates to pixels
        with rasterio.open(raster) as map_layer:
            pixels = map_layer.index(lon, lat) #input lon,lat

        # Store in the dataframe
        rain_gauge_coords['pixel_y'].iloc[i] = pixels[0]
        rain_gauge_coords['pixel_x'].iloc[i] = pixels[1]

    print(rain_gauge_coords)

path = './data/radar'
load_radar_data(path)