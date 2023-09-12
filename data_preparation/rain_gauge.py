import pandas as pd

def load_rain_gauge_data():
    '''
    Method to load data from excel files.
    '''

    rain_HII_2022 = pd.read_excel('data/raingauge_HII_Phetchaburi_10min_2022.xlsx', index_col=0, parse_dates=True, nrows=10)
    location_HII = pd.read_excel('data/HII_location.xlsx', index_col=0, nrows=10)
    
    return rain_HII_2022, location_HII

#TODO add Kagan analysis to filter out unreliable data