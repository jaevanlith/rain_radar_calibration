import pandas as pd

class Event:
    '''
    Rainfall event class
    '''
    
    def __init__(self, start_time, end_time, reflectivity, rainfall):
        self.start_time = start_time
        self.end_time = end_time
        self.reflectivity = reflectivity
        self.rainfall = rainfall

    def to_string(self):
        return "Start time: " + str(self.start_time) \
            + "\nEnd time: " + str(self.end_time) \
            + "\nReflectivity: " + str(self.reflectivity) \
            + "\nRainfall: " + str(self.rainfall)


def select_events(rain_df: pd.DataFrame):
    '''
    Method that selects rain events from the radar and gauge data.
    '''

    # Placeholder event list
    events = []
    events.append(Event(0,1,10,100))

    return events

#TODO event selection based on given properties