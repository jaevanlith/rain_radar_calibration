import pandas as pd

class Event:
    '''
    Rainfall event class
    '''
    
    def __init__(self, start_time, end_time, station, reflectivity=None, rainfall=None):
        self.start_time = start_time
        self.end_time = end_time
        self.station = station
        self.reflectivity = reflectivity
        self.rainfall = rainfall


def select_events_single_station(station, vals, datetime, k, l, h):
    '''
    Method to select events per station.

    @param station str: Name of station
    @param vals list[float]: Rain data of given station for one year
    @param datetime list[date]: List of dates and times per hour for the entire year 
    @param k float: Rainfall threshold
    @param l float: Minimum number of hours rain that an event should have
    @param h float: Maximum number of hours no rain within one event

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
                #Retrieve value
                val = vals.iloc[j]

                # Check if value is above threshold
                if val >= k:
                    # Reset statistic
                    consecutive_hours_no_rain = 0
                    # Add to event
                    candidate_event.append(val)
                else:
                    # Update statistic
                    consecutive_hours_no_rain += 1
                    # Check if max hours without rain is exceeded
                    if consecutive_hours_no_rain > h:
                        # Add to event
                        candidate_event.append(val)

                        # Check if min length is reached
                        if len(candidate_event) >= l:
                            # Create new event
                            start_time = datetime[i]
                            end_time = datetime[j - h]
                            tot_rainfall = sum(candidate_event[0:-consecutive_hours_no_rain])
                            new_event = Event(start_time, end_time, station, rainfall=tot_rainfall)

                            # Print to terminal
                            print('NEW EVENT SELECTED:')
                            print('Start time: ', start_time)
                            print('End time: ', end_time)
                            print('Station: ', station)
                            print('Rainfall: ', tot_rainfall)

                            # Add to events list
                            events.append(new_event)

                            # Continue events selection after end of new event
                            i = j + 1
                            break
                        else:
                            # Discard event when total length is too short
                            i += 1
                            break
            
        # Go to next timestep
        i += 1

    return events


def select_all_events(rain_df, k, l, h):
    '''
    Method that selects rain events from the gauge data.

    @param rain_df DataFrame: Rain data for one year of all stations
    @param k int: Rainfall threshold
    @param l int: Minimum number of hours rain that an event should have
    @param h int: Maximum number of hours no rain within one event

    @return events list[Event]: List of events at this station for the given year
    '''

    # Init event list
    events = []

    # Get time column
    datetime = rain_df.index

    # Loop over stations and correspoding values
    for (station, vals) in rain_df.items():
        # Select events for single station
        events = events + select_events_single_station(station, vals, datetime, k, l, h)

    #TODO retrieve total reflection and
    #  save events in file 

    return events

# rain_HII_2022 = pd.read_excel('data/HII_10min/raingauge_HII_Phetchaburi_10min_2022.xlsx', index_col=0, parse_dates=True)
# col = rain_HII_2022['ATG011']
# datetime = rain_HII_2022.index
# print(col[0:100])
# events = select_events_single_station('ATG011', col, datetime, k=2, l=6, h=2)
# events = select_all_events(rain_HII_2022, k=2, l=6, h=2)
# print(len(events))