import os
from PIL import Image
import numpy as np
import pandas as pd
import rasterio
import csv
import xarray as xr


def group_files_by_hours(filelist):
    '''
    Method to group files in a directory by hours.

    @param filelist list[str]: List of png files in directory of form YYYYMMDDHHMMSS.png

    @return result dict{int: str}: Dictionary with hours as key and filenames within that hour as value
    '''
    # Init empty dict with hours as key
    result = {h: [] for h in range(0,24)}
    
    # Loop over files in list
    for file in filelist:
        # Retrieve its hour
        hour = int(file[8:10])
        # Store in dict
        result[hour] = result[hour] + [file]

    return result


def generate_percipitation_maps(radar_data_path, year, a, b, save_path, months=None, days=None, resolution=800, measurements_per_hour=10, noise_threshold=15, hail_threshold=53):
    '''
    Method to generate percipitation maps from radar data.

    @param radar_data_path str: Directory where the radar data is stored.
    @param year int: Year to analyse the data from.
    @param a float: Calibrated parameter a.
    @param b float: Calibrated parameter a.
    @param save_path: Directory where the rain csv's should be stored.
    @param months list[str]: List of months to generate for.
    @param days list[str]: List of days to generate for.
    @param resolution int: Resolution of radar image.
    '''

    # Set the root path of the year under investigation
    radar_png_path = radar_data_path + '/radar_png/' + str(year)

    # If months not specified, derive from directory
    if months is None:
        months = os.listdir(radar_png_path)

    # Check if days specified
    if days is None:
        days_specified = False
    else:
        days_specified = True

    # Loop over months
    for month in months:
        # Set path for this month
        radar_png_month_path = radar_png_path + '/' + month
        # Create save path if it does not exist yet
        if not os.path.exists(save_path + '/' + month):
            os.makedirs(save_path + '/' + month)

        # If days not specified, derive from directory
        if not days_specified:
            days = os.listdir(radar_png_month_path)

        # Loop over days
        for day in days:
            # Set path for this day
            radar_png_day_path = radar_png_month_path + '/' + day
            # Create save path if it does not exist yet
            if not os.path.exists(save_path + '/' + month + '/' + day):
                os.makedirs(save_path + '/' + month + '/' + day)

            # Get list of files and sort
            filelist = os.listdir(radar_png_day_path)
            filelist.sort()

            # Group files by hour
            files_per_hour = group_files_by_hours(filelist)

            # Loop over all hours in this day
            for hour in range(0,24):
                # Init empty array to store hourly result
                result_hour = np.empty((resolution,resolution))
                
                # Count unopened files
                num_unopened = 0

                # If files missing in this hour, result is nan (assuming 6min measurement interval)
                if len(files_per_hour[hour]) != measurements_per_hour:
                    result_hour[:] = np.nan
                else:
                    # Loop over files in this hour
                    for file in files_per_hour[hour]:
                        # Try to open the png file, otherwise print that it gave issues and continue to next
                        try:
                            # Load radar data from file
                            data_png = Image.open(radar_png_day_path + '/' + file)
                            data_radar = np.array(data_png)

                            # Filter noise and hail
                            data_radar[data_radar < noise_threshold] = 0
                            data_radar[data_radar > hail_threshold] = hail_threshold

                            # Convert from dBZ to Z
                            data_radar = 10**(data_radar/10)
                            data_radar[data_radar == 1] = 0

                            # Convert to rain intensity
                            data_rain = (data_radar/a)**(1/b)

                            # Accumulate to hourly result
                            result_hour += data_rain

                        except:
                            print("Unable to open: " + radar_png_day_path + '/' + file)
                            num_unopened += 1
                
                # If all files unable to open, set to nan
                if num_unopened > 0:
                    result_hour[:] = np.nan

                # Take avg of hour
                result_intensity = result_hour / measurements_per_hour

                # Write hourly result to csv file
                df = pd.DataFrame(columns=np.arange(0,resolution), index=np.arange(0,resolution), data=result_intensity)
                df.to_csv(save_path + '/' + month + '/' + day + '/' + str(year) + month + day + f"{hour:02}" + '00.csv')


def get_coords(radar_data_path):
    '''
    Method to get the horizontal and vertical coordinates from a .tif file.
    '''
    # Open the file
    all_coords = rasterio.open(radar_data_path + '/extract_radarpixel/raster_radar_sattahip.tif')

    # Get horizontal and vertical coordinates
    X = [all_coords.xy(0, y)[0] for y in range(all_coords.height)]
    Y = [all_coords.xy(x, 0)[1] for x in range(all_coords.width)]

    return X, Y


def replace_indices(file_path, X, Y):
    '''
    Method to replace the indices in the excel files by coordinates.
    '''
    # Open the file
    with open(file_path, 'r', newline='') as file:
            # Read the CSV data
            reader = csv.reader(file)
            rows = list(reader)

    # Replace the indices of the columns by the horizontal coordinates
    rows[0][1:] = X

    # Replace the indices of the rows by the vertical coordinates
    for i in range(len(rows)-1):
        if i < len(Y):
            rows[i+1][0] = Y[i]

    # Write the modified data back to the CSV file
    with open(file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(rows)


def combine_csv_to_nc(radar_data_path, percip_path, save_path, months=None, days=None):
    '''
    Method to combine multiple .csv files into single .nc file
    '''
    i = 0
    # Init dataframe
    dfs = []

    # Get coordinates
    X, Y = get_coords(radar_data_path)
    print(len(X))
    print(len(Y))

    # If months not specified, derive from directory
    if months is None:
        months = os.listdir(percip_path)

    # Check if days specified
    if days is None:
        days_specified = False
    else:
        days_specified = True

    # Loop over months
    for month in months:
        # Set path for this month
        percip_month_path = percip_path + '/' + month

        # If days not specified, derive from directory
        if not days_specified:
            days = os.listdir()

        # Loop over days
        for day in days:
            # Set path for this day
            percip_day_path = percip_month_path + '/' + day
            # Create save path if it does not exist yet
            if not os.path.exists(save_path + '/' + month + '/' + day):
                os.makedirs(save_path + '/' + month + '/' + day)

            # Get list of files and sort
            filelist = os.listdir(percip_day_path)
            filelist.sort()

            # Loop over files
            for file in filelist:
                df_new = pd.read_csv(percip_day_path + '/' + file, index_col=0)
                print(df_new)
                dfs.append(df_new)
                i += 1
                if i == 2:
                    break

    print(dfs)

    # Convert each DataFrame to a DataArray and concatenate them along a new dimension
    data_arrays = [xr.DataArray(df) for df in dfs]
    merged_data = xr.concat(data_arrays, dim='new_dimension_name')
    
    print(merged_data)

    merged_data.to_netcdf(save_path + '/percipitation_maps.nc')

    # for csv_file in csv_files:
    #     df = pd.read_csv(csv_file)
    #     dataframes.append(df)

    # # Merge DataFrames into a single DataFrame
    # combined_df = pd.concat(dataframes, ignore_index=True)

    # # Convert the combined DataFrame to an xarray Dataset
    # ds = xr.Dataset.from_dataframe(combined_df)

    # # Save the xarray Dataset to a NetCDF file
    # ds.to_netcdf(save_path, format="NETCDF4")

    # csv_directory = './01_radar_csv'
    # save_path = './radar.nc'

    # # Get coordinates
    # X, Y = get_coords(radar_data_path)

    # # Get list of csv files
    # csv_files = [csv_directory + '/' + f for f in os.listdir(csv_directory) if os.path.isfile(os.path.join(csv_directory, f))]

    # # Replace indices of all csv files
    # for csv_file in csv_files
    #     replace_indices(csv_file, X, Y)

    # # Combine into .nc file
    # combine_csv_to_nc(csv_files, save_path)


combine_csv_to_nc("./data/radar", "./results/rain_csv", "./results", months=['01'], days=['21'])