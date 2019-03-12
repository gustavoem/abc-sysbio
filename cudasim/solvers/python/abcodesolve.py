import numpy

try:
    from scipy.integrate.odepack import odeint
except ImportError:

    def odeint(fun, conc, times, args, atol, rtol):
        return 0


def abcodeint(func, init_values, timepoints, parameters, dt=0.01, atol=None, rtol=None):
    """Call scipy.integrate.odeint.
    Return values for each species whose trajectory is described by func at timepoints given by timepoints.

    ***** args *****

    func:
            a function to integrate, generated by parseInfo.py from an SBML model.

    InitValues:
            a list of floats representing the initial values of the species whose trajectories are described by func.

    timepoints:
            a list of times at which values for the spec are required.

    parameters:
            a tuple of parameters to pass to func

    ***** kwargs *****

    dt:
            Internal timestep. scipy.integrate.odeint is forced to calculate values at this interval.
            For a stiff model a small dt is required for successful simulation.

    rtol:
            relative error tolerance.
            For a stiff model a small relative error tolerance is required for a successful simulation.

    atol:
            absolute error tolerance.
            For a stiff model a small absolute error tolerance is required for a successful simulation.

    """

    # array for the data that the user wants
    solutions_out = numpy.zeros([len(timepoints), len(init_values)])
    current_concentrations = tuple(init_values)
    # current_concentrations,parameters=func.rules(current_concentrations, parameters, timepoints[0])
    current_concentrations, parameters = func.rules(current_concentrations, parameters, 0)
    solutions_out[0] = current_concentrations

    counter = 0  # 1

    flag = True

    # intTime1 = timepoints[0]
    int_time1 = 0

    while flag:

        int_time2 = min(int_time1 + dt, timepoints[counter])

        data = odeint(func.modelfunction, current_concentrations, [int_time1, int_time2], args=(parameters,), atol=atol,
                      rtol=rtol)

        data[1], parameters = func.rules(data[1], parameters, int_time2)

        if (timepoints[counter] - int_time2) < 0.000000001:
            solutions_out[counter] = data[1]
            counter += 1
            if counter == len(timepoints):
                flag = False
        current_concentrations = data[1]
        int_time1 = int_time2

    return solutions_out


def abcodeint_onestep(func, current_concentrations, t1, t2, parameters, dt=0.01, atol=None, rtol=None):
    time = t1
    next_time = min(time + dt, t2)
    current_concentrations, parameters = func.rules(current_concentrations, parameters, time)

    while 1:
        # print time, next_time, t2, current_concentrations
        data = odeint(func.modelfunction, current_concentrations, [time, next_time], args=(parameters,), atol=atol,
                      rtol=rtol)

        current_concentrations, parameters = func.rules(current_concentrations, parameters, next_time)
        current_concentrations = data[1]

        if (t2 - next_time) < 0.000000001:
            return [current_concentrations, next_time, True]

        time = next_time
        next_time = min(time + dt, t2)

    return [current_concentrations, time, False]
