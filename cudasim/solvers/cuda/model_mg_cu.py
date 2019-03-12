import numpy
import multiprocessing

import cudasim.solvers.cuda.Lsoda_mg as Lsoda_mg
import cudasim.solvers.cuda.EulerMaruyama_mg as EulerMaruyama_mg
import cudasim.solvers.cuda.Gillespie_mg as Gillespie_mg


class CudaModel:
    # instantiation
    def __init__(self, name, nspecies, nparameters, prior, x0prior, source, integration, fit, dt, beta, timepoints,
                 logp, ngpu):
        self.nspecies = nspecies
        self.name = name

        # combine the parameters with the species
        self.kparameters = nparameters
        self.nparameters = nparameters + nspecies

        self.prior = prior
        self.prior.extend(x0prior)

        self.source = source
        self.integration = integration
        self.fit = fit
        self.cudaCode = self.name + '.cu'
        self.dt = dt
        self.beta = beta
        self.timepoints = timepoints
        self.logp = logp
        self.ngpu = ngpu

    def simulate(self, p, t, n, beta):
        gpu_threads = []
        output_cpu = multiprocessing.Queue()

        # distribute the particles across the cards
        n_per_card = [0 for i in range(self.ngpu)]
        nc = int(n / self.ngpu)
        for i in range(self.ngpu - 1):
            n_per_card[i] = int(n / self.ngpu)

        n_per_card[self.ngpu - 1] = n - (self.ngpu - 1) * nc

        for c in range(self.ngpu):

            # Create local parameter and species arrays
            species = numpy.zeros([n_per_card[c], self.nspecies])
            pp = numpy.zeros([n_per_card[c], self.kparameters])

            # Fill species and parameters
            for i in range(n_per_card[c]):
                place_mark = sum(n_per_card[0:c])
                species[i, :] = p[place_mark + i][self.kparameters:self.nparameters]

                if not self.logp:
                    pp[i, :] = p[place_mark + i][0:self.kparameters]
                else:
                    pp[i, :] = numpy.power(10, p[place_mark + i][0:self.kparameters])

            # Run on multiple GPUs
            gpu_thread = Lsoda_mg.Lsoda(self.timepoints, self.cudaCode, pp, species, output_cpu, card=c, dt=self.dt,
                                        dump=False, info=False, timing=False)
            gpu_threads.append(gpu_thread)
            gpu_thread.start()

        result_dict = {}
        for gpu_pro in gpu_threads:
            thread_id, results = output_cpu.get(gpu_pro)
            result_dict[thread_id] = results

        result = numpy.vstack(result_dict.values())
        return result
