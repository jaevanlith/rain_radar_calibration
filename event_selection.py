import pandas as pd

class Event:
    '''
    Rainfall event class
    '''
    
    def __init__(self, start_time, end_time, station, reflectivity, rainfall):
        self.start_time = start_time
        self.end_time = end_time
        self.station = station
        self.reflectivity = reflectivity
        self.rainfall = rainfall

        # Set duration
        self.duration = (end_time - start_time).total_seconds() // 3600

        # Set type
        avg_rainfall = rainfall / self.duration
        if avg_rainfall <= 5.0:
            self.type = "light"
        elif avg_rainfall <= 25.0:
            self.type = "moderate"
        elif avg_rainfall <= 50.0:
            self.type = "heavy"
        else:
            self.type = "extreme"


def select_events_single_station(station, vals, datetime, radar_df, h, k=0.1):
    '''
    Method to select events per station.

    @param station str: Name of station
    @param vals list[float]: Rain data of given station for one year
    @param datetime list[date]: List of dates and times per hour for the entire year
    @param radar_df DataFrame: Radar data for one year of all stations
    @param h float: Maximum number of hours no rain within one event
    @param k float: Rainfall threshold (always 0.1)

    @return events list[Event]: List of events at this station for the given year
    '''
    events = []

    i = 0
    while i < len(vals):
        # Check if value is above threshold
        if vals.iloc[i] >= k:
            # Init statistics for event
            candidate_event = []
            consecutive_hours_no_rain = 0

            # Loop over remaining values
            for j in range(i, len(vals)):
                # Retrieve value
                val = vals.iloc[j]
                # Add to event
                candidate_event.append(val)

                # Check if value is above threshold
                if val >= k:
                    # Reset statistic
                    consecutive_hours_no_rain = 0
                else:
                    # Update statistic
                    consecutive_hours_no_rain += 1
                    # Check if max hours without rain is exceeded
                    if consecutive_hours_no_rain > h:
                        # Create new event
                        start_time = datetime[i]
                        end_time = datetime[j - h]
                        tot_rainfall = sum(candidate_event[:-consecutive_hours_no_rain])
                        # avg_reflect = radar_df.loc[start_time:end_time][station].mean()
                        avg_reflect = 100

                        new_event = Event(start_time, end_time, station, avg_reflect, tot_rainfall)

                        # Print to terminal
                        print('NEW EVENT SELECTED:')
                        print('Start time: ', new_event.start_time)
                        print('End time: ', new_event.end_time)
                        print('Duration: ', new_event.duration)
                        print('Station: ', new_event.station)
                        print('Reflectivity: ', new_event.reflectivity)
                        print('Rainfall: ', new_event.rainfall)
                        print('Type: ', new_event.type)

                        # Add to events list
                        events.append(new_event)

                        # Continue events selection after end of new event
                        i = j + 1
                        break
            
        # Go to next timestep
        i += 1

    return events


def select_all_events(rain_df, radar_df, h, k=0.1):
    '''
    Method that selects rain events from the gauge data.

    @param rain_df DataFrame: Rain data for one year of all stations
    @param radar_df DataFrame: Radar data for one year of all stations
    @param h int: Maximum number of hours no rain within one event
    @param k int: Rainfall threshold (always 0.1)

    @return events list[Event]: List of events for the given year
    '''

    # Init event list
    events = []

    # Get time column
    datetime = rain_df.index

    # Loop over stations and correspoding values
    for (station, vals) in rain_df.items():
        # Select events for single station
        events = events + select_events_single_station(station, vals, datetime, radar_df, h, k)

    return events