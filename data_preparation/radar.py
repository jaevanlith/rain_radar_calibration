import pandas as pd
import numpy as np
from PIL import Image
import os
import warnings
warnings.filterwarnings("ignore")


def prepare_radar_data(radar_data_path, year, noise_threshold, hail_threshold, months=None, days=None):
    '''
    Method to load radar data from csv files.

    @param radar_data_path str: Directory where the radar data is stored.
    @param noise_threshold float: Threshold underneath which is considered noise (in dBZ).
    @param hail_threshold float: Threshold above which is considered hail (in dBZ).

    @return df DataFrame: Reflectivity over time for all stations.
    '''

    # Get the pixels corresponding to each station
    station_loc = pd.read_excel(radar_data_path + '/extract_radarpixel/raingauge_coordinate.xlsx', sheet_name='Sheet1')
    subset = station_loc[['STN_ID', 'pixel_y','pixel_x']]
    location_list = [tuple(x) for x in subset.to_numpy()]

    # Filter out negative pixels (outside radar region)
    stations_outside_region = []
    location_list_filtered = []
    # Loop over stations and pixel coordinates
    for (id, pixel_y, pixel_x) in location_list:
        # Check if at least one pixel is outside region
        if pixel_y < 0 or pixel_x < 0:
            # Keep track of stations outside
            stations_outside_region.append(id)
        else:
            # Store stations inside region
            location_list_filtered.append((id, pixel_y, pixel_x))
    # Update location list
    location_list = location_list_filtered

    # Set the root path of the year under investigation
    radar_png_path = radar_data_path + '/radar_png/' + str(year)

    # Init dataframe to store radar data
    columns = [x[0] for x in location_list]
    radar_df = pd.DataFrame(columns=columns)
    # Init datetime column
    DateTime = []

    # If months not specified, derive from directory
    if months is None:
        months = os.listdir(radar_png_path)

    # Loop over months
    for month in months:
        # Set path for this month
        radar_png_month_path = radar_png_path + '/' + month

        # If days not specified, derive from directory
        if days is None:
            days = os.listdir(radar_png_month_path)

        # Loop over days
        for day in days:
            # Set path for this day
            radar_png_day_path = radar_png_month_path + '/' + day
            # Get list of files and count
            filelist = os.listdir(radar_png_day_path)

            # Loop over all radar files
            for file in filelist:
                # Get datetime from file name   
                Year = file[0:4]
                Month = file[4:6]
                Day = file[6:8]
                Hour = file[8:10]
                Minute = file[10:12]
                
                # Format datetime
                Date = Year + "-" + Month + "-" + Day + ' ' + Hour + ':' + Minute
                DateTime.append(Date)

                # Load radar data from file
                extract_data = np.arange(len(location_list), dtype=float)
                data_png = Image.open(radar_png_day_path + '/' + file)
                data_png_numpy = np.array(data_png)
                df_data = pd.DataFrame(data_png_numpy)

                # Loop over locations of stations
                for location in location_list:
                    # Get the data corresponding to the pixel locations
                    pixel_x = int(location[2])
                    pixel_y = int(location[1])
                    value = df_data.iloc[pixel_y, pixel_x]
                    extract_data[location_list.index(location)] = value

                # Store in dataframe
                radar_df.loc[len(radar_df)] = extract_data

    # Set datetime as index column
    df_datetime = pd.DataFrame(DateTime)
    df_datetime.index = np.arange(1, len(df_datetime)+1)
    data_datetime = df_datetime.astype('datetime64[ns]')
    radar_df.insert(loc=0, column='Datetime', value=data_datetime)
    radar_df.set_index('Datetime', inplace=True)
    radar_df = radar_df.sort_index(axis=1)

    # Set data to Thai local time
    radar_df = radar_df.shift(7, freq='H')

    # Filter noise and hail
    radar_df[radar_df < noise_threshold] = 0
    radar_df[radar_df > hail_threshold] = hail_threshold

    # Convert dBZ to Z
    radar_df = 10**(radar_df/10)
    radar_df = radar_df.replace(1,0)

    # Average over hours
    radar_df = radar_df.resample('H').mean()

    return radar_df, stations_outside_region