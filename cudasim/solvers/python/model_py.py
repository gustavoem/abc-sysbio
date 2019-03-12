import numpy

from cudasim.solvers.python import abcodesolve
from cudasim.solvers.python import sdeint
from cudasim.solvers.python import GillespieAlgorithm


class Model:
    # instantiation
    def __init__(self, name, nspecies, nparameters, prior, x0prior, source, integration, fit, dt, atol, rtol, logp):

        self.name = name
        self.nspecies = nspecies

        # combine the parameters with the species
        self.kparameters = nparameters
        self.nparameters = nparameters + nspecies

        self.prior = prior
        self.prior.extend(x0prior)

        self.source = source
        self.integration = integration
        self.fit = fit

        self.module = __import__(source)

        self.dt = dt
        self.atol = atol
        self.rtol = rtol
        self.logp = logp

        if self.integration == 'ODE':
            self.simulate = self.simulate_ode
        elif self.integration == 'SDE':
            self.simulate = self.simulate_sde
        elif self.integration == 'Gillespie':
            self.simulate = self.simulate_mjp

    def simulate_ode(self, p, t, n, beta):
        # must return a structure of the form [n][nbeta][ntimepoints][nspecies]
        ret = numpy.zeros([n, beta, len(t), self.nspecies])

        for i in range(n):
            for j in range(beta):
                if not self.logp:
                    par = p[i][0:self.kparameters]
                else:
                    par = numpy.power(10, p[i][0:self.kparameters])

                dat = abcodesolve.abcodeint(func=self.module, init_values=p[i][self.kparameters:self.nparameters],
                                            timepoints=t, parameters=par, dt=self.dt, atol=self.atol, rtol=self.rtol)
                for k in range(len(t)):
                    for l in range(self.nspecies):
                        ret[i, j, k, l] = dat[k, l]

        return ret

    def simulate_sde(self, p, t, n, beta):
        # must return a structure of the form [n][nbeta][ntimepoints][nspecies]
        ret = numpy.zeros([n, beta, len(t), self.nspecies])

        for i in range(n):
            for j in range(beta):
                if not self.logp:
                    par = p[i][0:self.kparameters]
                else:
                    par = numpy.power(10, p[i][0:self.kparameters])

                dat = sdeint.sdeint(func=self.module, init_values=p[i][self.kparameters:self.nparameters],
                                    parameter=par, timepoints=t, dt=self.dt)
                for k in range(len(t)):
                    for l in range(self.nspecies):
                        ret[i, j, k, l] = dat[k, l]

        return ret

    def simulate_mjp(self, p, t, n, beta):
        # must return a structure of the form [n][nbeta][ntimepoints][nspecies]
        ret = numpy.zeros([n, beta, len(t), self.nspecies])

        for i in range(n):
            for j in range(beta):
                if not self.logp:
                    par = p[i][0:self.kparameters]
                else:
                    par = numpy.power(10, p[i][0:self.kparameters])

                dat = GillespieAlgorithm.gillespie_int(func=self.module,
                                                       init_values=p[i][self.kparameters:self.nparameters],
                                                       parameters=par, outputtimes=t)
                for k in range(len(t)):
                    for l in range(self.nspecies):
                        ret[i, j, k, l] = dat[k, l]

        return ret
