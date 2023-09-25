import pandas as pd
from datetime import datetime

# ONLY FOR TESTING (set to None while running)
NROWS = 1000

dateparse = lambda x: datetime.strptime(x, '%d/%m/%Y %H:%M')

def load_rain_gauge_data(rain_gauge_data_path, year):
    '''
    Method to load data from excel files per year.

    @param rain_gauge_data_path str: Directory containing the rain gauge data.
    @param year int: Year to analyse the data from.

    @return rain_HII DataFrame: HII rain data sampled every 10 mins.
    @return location_HII DataFrame: Locations of HII stations.
    @return rain_EWS DataFrame: EWS rain data sampled every 15 mins.
    @return location_EWS DataFrame: Locations of EWS stations.
    '''

    # Load HII data
    rain_HII = pd.read_excel(rain_gauge_data_path + '/HII_10min/raingauge_HII_Phetchaburi_10min_' + str(year) + '.xlsx', index_col=0, parse_dates=True, nrows=NROWS)
    location_HII = pd.read_excel(rain_gauge_data_path + '/HII_location.xlsx', index_col=0, nrows=NROWS)

    # Load EWS data
    # rain_EWS = pd.read_csv(rain_gauge_data_path + '/EWS_15min/EWS_station_phetchaburi_project_15m_' + str(year) + '.csv', index_col=0, parse_dates=['Datetime'], date_format='%d/%m/%Y %H:%M', nrows=NROWS)
    rain_EWS = pd.read_csv(rain_gauge_data_path + '/EWS_15min/EWS_station_phetchaburi_project_15m_' + str(year) + '.csv', index_col=0, parse_dates=['Datetime'], date_parser=dateparse, nrows=NROWS)
    location_EWS = pd.read_excel(rain_gauge_data_path + '/EWS_location.xlsx', index_col=0, nrows=NROWS)

    return rain_HII, location_HII, rain_EWS, location_EWS


def convert_and_merge(rain_HII_10min, rain_EWS_15min):
    '''
    Method to convert HII and EWS dataframes to hours and merge them.

    @param rain_HII_10min DataFrame: HII rain data sampled every 10 mins.
    @param rain_EWS_15min DataFrame: EWS rain data sampled every 15 mins.

    @return rain_merged_60min DataFrame: Combined data sampled every 60 mins.
    '''

    # Convert HII to hours
    rain_HII_60min = rain_HII_10min.resample('H').agg(pd.Series.sum, skipna=False)
    rain_HII_60min.reset_index(inplace=True)

    # Convert EWS to hours
    rain_EWS_60min = rain_EWS_15min.resample('H').agg(pd.Series.sum, skipna=False)
    rain_EWS_60min.reset_index(inplace=True)

    # Merge
    rain_merged_60min = pd.merge(rain_HII_60min, rain_EWS_60min, on='Datetime', how='outer')
    rain_merged_60min.set_index('Datetime', inplace=True)

    return rain_merged_60min


def percentage_station_filter(df, threshold):
    '''
    Method to filter out all stations with too much missing data.

    @param df DataFrame: Rain data to be filtered.
    @param threshold Float: Minimum percentage of values captured by station.

    @return df DataFrame: Rain data without stations with too much missing data.
    '''

    # Count number of columns
    n_col = df.shape[1]
    # Init bad stations list
    bad_st = []

    # Loop over columns
    for i in range(n_col):
        # Get column and count values
        col = df.iloc[:,i]
        total_values = len(col)
        nan_values = col.isna().sum()

        # Compute percentage
        if total_values > 0:
            percentage = 100 - (nan_values / total_values) * 100
        else:
            percentage = 100    # Avoid division by zero if column is empty

        # Bad station if too many missing values 
        if percentage < threshold:
            bad_st.append(col.name)

    # Remove all bad stations
    df.drop(columns=bad_st, inplace=True)

    return df


def prepare_rain_gauge_data(rain_gauge_data_path, year, station_threshold):
    '''
    Method to prepare rain gauge data entirely.

    @param rain_gauge_data_path str: Directory containing the rain gauge data.
    @param year int: Year to analyse the data from.

    @return rain_gauge_data DataFrame: Final rain gauge data passed to next component.
    '''

    # Load HII and EWS data from files
    rain_HII_10min, location_HII, rain_EWS_15min, location_EWS = load_rain_gauge_data(rain_gauge_data_path, year)

    # Convert data to hours and merge HII and EWS
    rain_merged_60min = convert_and_merge(rain_HII_10min, rain_EWS_15min)

    # Filter out stations based when too much missing data
    rain_filtered = percentage_station_filter(rain_merged_60min, station_threshold)

    #TODO add Kagan analysis to filter out unreliable data (replace placeholder)
    rain_gauge_data = rain_filtered

    return rain_gauge_data