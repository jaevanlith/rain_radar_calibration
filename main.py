import argparse
from data_preparation.rain_gauge import load_rain_gauge_data
from event_selection import select_all_events
from calibration import calibrate

if __name__ == '__main__':
    # Parse ommand line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--example', type=str, default="hello")
    args = dict(vars(parser.parse_args()))

    # Load data from data preparation
    rain_HII_2022, location_HII = load_rain_gauge_data()

    # Select events
    events = select_all_events(rain_HII_2022)

    # Calibration
    A, b = calibrate(events)
