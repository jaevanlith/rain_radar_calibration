import numpy as np
import pandas as pd
import geopy.distance
import matplotlib # For plot
import matplotlib.pyplot as plt
from scipy.signal import correlate
import tkinter as tk
from tkinter import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random


def compute_station_distances(location_filtered):
    # Init empty distance matrix
    empty_gauges = np.zeros((len(location_filtered), len(location_filtered)))

    # Loop over stations
    for i in range(len(location_filtered)):
        # Retrieve its coordinates
        coordinate_1 = (location_filtered['LAT'].iloc[i], location_filtered['LONG'].iloc[i])
        # Loop over remaining stations
        for j in range(i, len(location_filtered)):
            # Retrieve its coordinates
            coordinate_2 = (location_filtered['LAT'].iloc[j], location_filtered['LONG'].iloc[j])
            # Compute distance between stations
            empty_gauges[i, j] = geopy.distance.geodesic(coordinate_1, coordinate_2).km

    # Convert distance matrix into DataFrame
    index_distances_1 = location_filtered.index
    distances_gauges = pd.DataFrame(data=empty_gauges, index=index_distances_1, columns=index_distances_1)

    return distances_gauges, index_distances_1


def correl(station_1, station_2):
    '''
    Method to calculate correlation between 2 rain gauges
    @param station_1 array: First station rain data
    @param station_2 array: Second station rain data

    @return correlation float: Correlation between stations
    '''
    # Retrieve correlation matrix
    correlation = np.corrcoef(station_1, station_2)

    # Only diagonal entry is needed so value at 1x2 or 2x1
    return correlation[0,1]


def compute_correlations(location_filtered, rain_data_daily, index_distances_1):
    # Init correlation matrix
    corr_empty = np.empty((len(location_filtered), len(location_filtered)))

    # Loop over stations
    for i in range(len(location_filtered)):
        # Get rain data of station
        array_filtered_1 = rain_data_daily.iloc[:, i]
        # Loop over remaining stations
        for j in range(len(location_filtered)):
            # Get rain data of station
            array_filtered_2 = rain_data_daily.iloc[:, j]
            # Compute and store correlation between stations
            corr_empty[i, j] = correl(array_filtered_1, array_filtered_2)

    # Convert correlation matrix to DataFrame
    corr_matrix = pd.DataFrame(data=corr_empty, index=index_distances_1, columns=index_distances_1)
    # Make the matrix triangular
    corr_matrix *= 1 - np.tri(*corr_matrix.shape, k = -1)

    return corr_matrix


def maximum_radius(distance_df, correlation_df, min_correlation, max_error, max_radius_lim):
    """
    maximum radius in which 2 stations have a high enough correlation. It has the following input parameters:
    distance_df = the dataframe that is created before with distances between 2 stations
    correlation_df = the dataframe that is created before with correlation between 2 stations
    min_correlation = minimum required acceptable correlation (standard is 0.6)
    max_error = amount of which the point found can deviate from 0.6 
    (max_error = 0.10 means that a correlation value of 0.70 can be found because the radius is higher at this point)
    max_radius_lim = realistic value for maximum radius. If max_radius goes to 600 this is probably not realistic
    """
    stations = [int(i) for i in range(0, len(distance_df))]
    max_distance = -1
    max_distance_stations = None
    max_radius = float('inf')

    for i in range(len(distance_df)):
        for j in range(i+1, len(distance_df)):
            distance = distance_df.iloc[i, j]
            correlation = correlation_df.iloc[i, j]

            if correlation >= min_correlation and abs(correlation - min_correlation) <= max_error:
                if distance > max_distance:
                    max_distance = distance
                    max_distance_stations = (stations[i], stations[j])
                    max_radius = distance_df.iloc[max_distance_stations[0], max_distance_stations[1]]

    max_radius = min(max_radius, max_radius_lim)

    return max_radius


def plot_kagan(distances_gauges, corr_matrix, max_radius, save_path=None):
    '''
    Method to plot and store the Kagan analysis.
    '''

    plt.scatter(distances_gauges, corr_matrix, s=0.1)
    plt.xlabel('Distance [km]')
    plt.ylabel('Correlation [-]')
    plt.axhline(0.6, c = 'r', ls ='--')
    plt.axvline(max_radius, c = 'r', ls = '--')
    plt.show()

    if save_path is not None:
        plt.savefig(save_path)


def compute_DM_data(distance_df, correlation_df, rain_gauge_df):
    max_radius = maximum_radius(distance_df, correlation_df, 0.6, 0.10, 50)
    
    stations_dict = {}
    
    for index in distance_df.index:
        stations_dict[index] = []
    
    for i in range(len(distance_df)):
        for j in range(i+1, len(distance_df)):
            distance = distance_df.iloc[i, j]
            
            if distance < max_radius:
                station_i = distance_df.index[i]
                station_j = distance_df.index[j]
                
                stations_dict[station_i].append(station_j)
                stations_dict[station_j].append(station_i)
            
    cumulative_rainfall_dict = {}   
    
    # Iterate through the keys (row indices) in stations_dict
    for index, stations in stations_dict.items():
        # Filter relevant columns based on the station's stations_dict entry
        relevant_columns = [station for station in stations if station in rain_gauge_df.columns]
        relevant_data = rain_gauge_df[relevant_columns]
        
        # Calculate the cumulative sum for each column separately
        cumulative_sums = relevant_data.cumsum()
        
        # Calculate the average cumulative sum across relevant columns (including the key column)
        average_cumulative_sum = cumulative_sums.mean(axis=1)
        
        # Store the average cumulative sum and the cumulative sum of the key column
        cumulative_rainfall_dict[index] = {
            'average_cum_sum': average_cumulative_sum,
            'key_column_cum_sum': rain_gauge_df[index].cumsum()  # Assuming index is the key column
        }
    
    return cumulative_rainfall_dict, stations_dict


def get_DM_curves_data(rain_df, location_HII, location_EWS, min_correlation=0.6, max_error=0.1, max_radius_limit=50):
    '''
    Method to analyse DM curves.

    @param rain_df DataFrame: Rain data per 60min from HII and EWS merged
    @param location_HII DataFrame: Coordinates of HII stations
    @param location_EWS DataFrame: Coordinates of EWS stations
    '''

    # Sort rain data and sample by day
    rain_sorted = rain_df.sort_index(axis=1)
    rain_data_daily = rain_sorted.resample('D').sum()

    # Get the stations under investigation
    column_keys = rain_data_daily.columns.tolist()

    # Merge the locations of HII and EWS stations
    location_gauges = pd.concat([location_HII.rename(columns={'tele_stati':'STN_ID', 'lat':'LAT', 'long':'LONG'}), location_EWS])
    location_gauges.index.name = 'STN_ID'
    location_gauges = location_gauges[~location_gauges.index.duplicated(keep='first')]

    # Drop stations that were already filtered out
    location_filtered = location_gauges[location_gauges.index.isin(column_keys)]

    # Compute the distances between the rain gauges
    distances_gauges, index_distances_1 = compute_station_distances(location_filtered)

    # Compute the correlations between the rain gauges
    corr_matrix = compute_correlations(location_filtered, rain_data_daily, index_distances_1)

    # Compute the maximum radius to consider as neighbouring stations by Kagan analysis
    max_radius = maximum_radius(distances_gauges, corr_matrix, min_correlation, max_error, max_radius_limit)

    # Plot the Kagan analysis
    plot_kagan(distances_gauges, corr_matrix, max_radius)

    # Compute data for the DM curves
    results, surrounding_stations = compute_DM_data(distances_gauges, corr_matrix, rain_data_daily)

    return results, surrounding_stations


