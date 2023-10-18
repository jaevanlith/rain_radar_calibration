import argparse
from data_preparation.rain_gauge import prepare_rain_gauge_data
from data_preparation.radar import prepare_radar_data
from event_selection import select_all_events
from calibration import calibrate

if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--rain_gauge_data_path', type=str, default="./data/rain_gauge")
    parser.add_argument('--radar_data_path', type=str, default="./data/radar")
    parser.add_argument('--year', type=int, default=2022)
    parser.add_argument('--station_threshold', type=float, default=40, help='Threshold percentage of non-missing data per station')
    parser.add_argument('--noise_threshold', type=float, default=15, help='Threshold underneath which is considered noise (in dBZ).')
    parser.add_argument('--hail_threshold', type=float, default=53, help='Threshold above which is considered hail (in dBZ).')
    parser.add_argument('--max_no_rain', type=int, default=2, help='Maximum number of hours without rain within one event')
    args = dict(vars(parser.parse_args()))
    
    ########## DATA PREPARATION ###########
    # Initialize provided arguments
    rain_gauge_data_path = args['rain_gauge_data_path']
    radar_data_path = args['radar_data_path']
    year = args['year']
    station_threshold = args['station_threshold']
    noise_threshold = args['noise_threshold']
    hail_threshold = args['hail_threshold']

    # Prepare rain gauge data per hour in mm
    print('Preparing rain gauge data...')
    rain_gauge_data, dm_results, surrounding_stations = prepare_rain_gauge_data(rain_gauge_data_path, year, station_threshold, nrows=100)
    print('Done')

    # Prepare radar data in per hour in Z
    print('Preparing radar data...')
    months = ['01']
    days = ['01', '02']
    radar_data = prepare_radar_data(radar_data_path, year, noise_threshold, hail_threshold, months=months, days=days)
    print('Done')

    ############ EVENT SELECTION ##########
    # Initialize provided arguments
    max_no_rain = args['max_no_rain']

    # Select events based on prepared data
    print('Selecting events...')
    events, Z, R = select_all_events(rain_gauge_data, radar_data, max_no_rain)
    print(events)

    ########### CALIBRATION ###########
    print('Calibrating...')
    a, b = calibrate(Z, R)
    print('Optimal a: ', a)
    print('Optimal b: ', b)
