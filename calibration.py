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

    # Compute Mean Squared Error
    MSE = np.mean((Z - a * R**b)**2)

    return MSE


def calibrate(events):
    '''
    Method which learns the parameters a and b in the relationship Z = aR^b.
    '''

    # Init vectors for reflectivity and rainfall
    n = len(events)
    Z = np.zeros(n)
    R = np.zeros(n)

    # Fill vectors with event data
    for i in range(len(events)):
        e = events[i]
        Z[i] = e.reflectivity
        R[i] = e.rainfall

    # Initial guess for a and b
    init_guess = [400, 1.6]

    # Minimize objective
    result = minimize(objective, init_guess, args=(Z, R))

    # Extract optimal a and b
    a, b = result.x

    return a, b