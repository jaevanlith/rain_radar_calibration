import pandas as pd

# ONLY FOR TESTING (set to None while running)
NROWS = 10000

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
    rain_EWS = pd.read_csv(rain_gauge_data_path + '/EWS_15min/EWS_station_phetchaburi_project_15m_' + str(year) + '.csv', index_col=0, parse_dates=['Datetime'], date_format='%d/%m/%Y %H:%M', nrows=NROWS)
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


def prepare_rain_gauge_data(rain_gauge_data_path, year):
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

    #TODO add Kagan analysis to filter out unreliable data (replace placeholder)
    rain_gauge_data = rain_merged_60min

    return rain_gauge_data