import numpy as np
from scipy.optimize import minimize

def objective(params, Z, R):
    '''
    Method to solve the equation for a for fixed b.

    @param params tuple[float]: Parameters a and b.
    @param Z array[float]: Vector of reflectivity values of all events.
    @param R array[float]: Vector of rainfall values of all events.

    @return MSE float: Mean Squared Error to be minimized.
    '''
    # Extract parameters
    a, b = params

    # Compute radar rain
    radar_rain = (Z/a)**(1/b)
    # Convert from 6min to 60min
    radar_rain_hour = np.mean(radar_rain, axis=1)
    # Compute Mean Squared Error
    MSE = np.mean((radar_rain_hour - R)**2)

    return MSE


def calibrate(Z, R, a_guess=400, b_guess=1.6, b_lb=1.5, b_ub=1.6):
    '''
    Method which learns the parameters a and b in the relationship Z = aR^b.

    @param Z array[float]: Vector of reflectivity values of all events.
    @param R array[float]: Vector of rainfall values of all events.
    @param a_guess float: Initial guess for parameter a.
    @param b_guess float: Initial guess for parameter b.
    @param b_lb float: Lower bound for parameter b.
    @param b_ub float: Upper bound for parameter b.

    @return a float: Value for a that minimizes objective function.
    @return b float: Value for b that minimizes objective function.
    '''

    # Initial guess for a and b
    init_guess = [a_guess, b_guess]

    # Bounds
    bounds = ((None, None), (b_lb, b_ub))

    # Minimize objective
    result = minimize(objective, init_guess, args=(Z, R), bounds=bounds)

    # Extract optimal a and b
    a, b = result.x

    return a, b