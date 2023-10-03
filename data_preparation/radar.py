import pandas as pd
import numpy as np
import rasterio
import os
import warnings
warnings.filterwarnings("ignore")

# ONLY FOR TESTING (set to None while running)
NROWS = 1000

def get_station_pixels(radar_data_path):
    '''
    Method to get the corresponding pixels of all rain gauge stations.

    @param radar_data_path str: Directory where the radar data is stored.

    @return station_loc DataFrame: Coordinates and corresponding pixels for all stations.
    '''

    # Load sattaship raster
    raster = radar_data_path + '/extract_radarpixel/raster_radar_sattahip.tif'

    # Load input coordinates
    station_loc = pd.read_excel(radar_data_path + '/extract_radarpixel/raingauge_coordinate.xlsx', sheet_name='Sheet1', nrows=NROWS)
    station_loc['pixel_x'] = np.nan
    station_loc['pixel_y'] = np.nan

    # Loop over all stations
    for i in station_loc.index:
        # Retrieve latitude and longitude 
        lat = float(station_loc['lat'].iloc[i])
        lon = float(station_loc['long'].iloc[i])

        # Map coordinates to pixels
        with rasterio.open(raster) as map_layer:
            pixels = map_layer.index(lon, lat) #input lon,lat

        # Store in the dataframe
        station_loc['pixel_y'].iloc[i] = pixels[0]
        station_loc['pixel_x'].iloc[i] = pixels[1]

    return station_loc


def prepare_radar_data(radar_data_path, noise_threshold, hail_threshold=53):
    '''
    Method to load radar data from csv files.

    @param radar_data_path str: Directory where the radar data is stored.
    @param noise_threshold float: Threshold underneath which is considered noise (in dBZ).
    @param hail_threshold float: Threshold above which is considered hail (in dBZ).

    @return df DataFrame: Reflectivity over time for all stations.
    '''

    # Get the pixels corresponding to each station
    station_loc = get_station_pixels(radar_data_path)
    subset = station_loc[['Name', 'pixel_y','pixel_x']]
    location_list = [tuple(x) for x in subset.to_numpy()]

    # Get list of radar files and count
    filelist = os.listdir(radar_data_path + '/radar_csv')
    num_files = len(filelist)

    # Create dataframe
    indices = []
    for i in range(1, num_files+1):
        indices.append(i)
    
    columns = []
    for j in location_list:
        columns.append(j[0])
    df = pd.DataFrame(index=indices,columns=columns)

    # Init datetime column
    DateTime = []
    # Loop over all radar files
    for file in filelist:
        # Get datetime from file name   
        Year = '20' + file[14:16]
        Month = file[16:18]
        Day = file[18:20]
        Hour = file[20:22]
        Minute = file[22:24]
        # Format datetime
        Date = Year + "-" + Month + "-" + Day + ' ' + Hour + ':' + Minute
        DateTime.append(Date)

        # Load radar data from file
        extract_data = np.arange(len(location_list), dtype=float)
        df_data = pd.read_csv(radar_data_path + '/radar_csv/' + file, skiprows=3, index_col=None, header=None)

        # Loop over locations of stations
        for location in location_list:
            # Get the data corresponding to the pixel locations
            pixel_x = int(location[2])
            pixel_y = int(location[1])
            value = df_data.iloc[pixel_y, pixel_x]
            extract_data[location_list.index(location)] = value

        # Store in dataframe
        df.iloc[filelist.index(file)] = extract_data

    # Set datetime as index column
    df_datetime = pd.DataFrame(DateTime)
    df_datetime.index = np.arange(1, len(df_datetime)+1)
    data_datetime = df_datetime.astype('datetime64[ns]')
    df.insert(loc=0, column='Datetime', value=data_datetime)
    df.set_index('Datetime', inplace=True)

    # Set data to Thai local time
    df = df.shift(7, freq='H')

    # Filter noise and hail
    df[df < noise_threshold] = 0
    df[df > hail_threshold] = hail_threshold

    # Convert dBZ to Z
    df = 10**(df/10)
    df = df.replace(1,0)

    # Average over hours
    df = df.resample('H').mean()

    return df