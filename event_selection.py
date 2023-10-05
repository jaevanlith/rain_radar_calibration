class Event:
    '''
    Rainfall event class
    '''
    
    def __init__(self, start_time, end_time, stations, reflectivity, rainfall):
        self.start_time = start_time
        self.end_time = end_time
        self.stations = stations
        self.reflectivity = reflectivity
        self.rainfall = rainfall

        # Set duration
        self.duration = int((end_time - start_time).total_seconds() // 3600)

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

    def to_string(self):
        return (
            'Start time: ' + str(self.start_time) + 
            '\nEnd time: ' + str(self.end_time) + 
            '\nDuration: ' + str(self.duration) +
            '\nStation: ' + str(self.stations) +
            '\nReflectivity: ' + str(self.reflectivity) +
            '\nRainfall: ' + str(self.rainfall) +
            '\nType: ' + self.type
        )

def select_events_single_station(station, vals, datetime, radar_df, max_no_rain, k=0.1):
    '''
    Method to select events per station.

    @param station str: Name of station
    @param vals list[float]: Rain data of given station for one year
    @param datetime list[date]: List of dates and times per hour for the entire year
    @param radar_df DataFrame: Radar data for one year of all stations
    @param max_no_rain float: Maximum number of hours without rain within one event
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
                    if consecutive_hours_no_rain > max_no_rain:
                        # Create new event
                        start_time = datetime[i]
                        end_time = datetime[j - max_no_rain]
                        tot_rainfall = sum(candidate_event[:-consecutive_hours_no_rain])
                        # avg_reflect = radar_df.loc[start_time:end_time][station].mean()
                        avg_reflect = 100

                        new_event = Event(start_time, end_time, [station], avg_reflect, tot_rainfall)

                        # # Print to terminal
                        # print('NEW EVENT SELECTED:')
                        # print(new_event.to_string())

                        # Add to events list
                        events.append(new_event)

                        # Continue events selection after end of new event
                        i = j + 1
                        break
            
        # Go to next timestep
        i += 1

    return events


def merge_overlapping_events(events):
    '''
    Method to merge single-station events that overlap in time.

    @param events list[Event]: Events detected per station

    @return result list[Event]: Events including multiple stations
    '''
    # Sort the events on start time
    events.sort(key=lambda e: e.start_time)

    # Init list to store the merged events and store first event
    result = [events[0]]

    # Loop over events (and skip the first)
    for e in events[1:]:
        # Check if current event and last merged event overlap
        if e.start_time <= result[-1].end_time:
            # Merge events and overwrite last one in result
            result[-1] = merge_two_events(result[-1], e)
        else:
            # If event is later than last merged, add event to the result
            result.append(e)

    return result


def merge_two_events(e1, e2):
    '''
    Method to merge two events.

    @param e1 Event: Event to be merged.
    @param e2 Event: Event to be merged.

    @return merged_event Event: Merged event.
    '''
    # Pick earliest start time
    start_time = min(e1.start_time, e2.start_time)
    # Pick latest end time
    end_time = max(e1.end_time, e2.end_time)
    # Concat lists of stations
    stations = e1.stations + e2.stations
    # Recompute average reflectivity
    reflectivity = (e1.reflectivity * e1.duration + e2.reflectivity * e2.duration) / (e1.duration + e2.duration)
    # Add cummulative rainfall
    rainfall = e1.rainfall + e2.rainfall

    # Create new event
    merged_event = Event(start_time, end_time, stations, reflectivity, rainfall)

    return merged_event


def select_all_events(rain_df, radar_df, max_no_rain, k=0.1):
    '''
    Method that selects rain events from the rain gauge data.

    @param rain_df DataFrame: Rain data for one year of all stations
    @param radar_df DataFrame: Radar data for one year of all stations
    @param max_no_rain int: Maximum number of hours without rain within one event
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
        events = events + select_events_single_station(station, vals, datetime, radar_df, max_no_rain, k)

    # Merge single-station events that overlap in time
    events = merge_overlapping_events(events)

    return events