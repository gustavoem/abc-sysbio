import numpy as np
from numpy import random as rnd

import copy
import time

from abcsysbio import euclidian
from abcsysbio import kernels
from abcsysbio import statistics

from KernelType import KernelType
from PriorType import PriorType


"""
priors: 
              a 2D list.
              priors[model_number][parameter_number] is a NamedTuple of type prior.
              The .type attribute is a PriorType object (one of PriorType.constant, PriorType.uniform, PriorType.normal,
              PriorType.lognormal).
              The other attributes store the appropriate parameters.

fit:      
              a 2D list of strings.
              This list contains the fitting instructions and therefore defines how to fit the
              experimental data to the systems variables. The first dimension represents the 
              models to be investigated, the second dimension represents the amount of data.
              
              Example:
              1 model with 7 species, 3 data series
              fit = [ ['species1+species2' , 'species5' , '3*species4-species7'], ]
              2 models with each 7 species, 2 data series
              fit = [ ['species1' , 'species2*species3'] , ['species1' , 'species2*species4'] ]
              
              The default value is 'None', i.e. the order of data series corresponds exactly 
              to the order of species.
"""


# distances are stored as [nparticle][nbeta][d1, d2, d3 .... ]
# trajectories are stored as [nparticle][nbeta][ species ][ times ]

print ">>>>>>> Using local version of abcsmc.py"

class AbcsmcResults:
    def __init__(self,
                 naccepted,
                 sampled,
                 rate,
                 trajectories,
                 distances,
                 margins,
                 models,
                 weights,
                 parameters,
                 epsilon):
        self.naccepted = naccepted
        self.sampled = sampled
        self.rate = rate
        self.trajectories = copy.deepcopy(trajectories)
        self.distances = np.array(distances)
        self.margins = np.array(margins)
        self.models = np.array(models)
        self.weights = np.array(weights)
        self.parameters = np.array(parameters)
        self.epsilon = epsilon


class Abcsmc:

    def __init__(self,
                 models,
                 nparticles,
                 modelprior,
                 data,
                 beta,
                 nbatch,
                 model_kernel,
                 debug,
                 timing,
                 distancefn=euclidian.euclidian_distance,
                 kernel_type=KernelType.component_wise_uniform,
                 kernelfn=kernels.get_kernel,
                 kernelpdffn=kernels.get_parameter_kernel_pdf,
                 perturbfn=kernels.perturb_particle):
        """

        Parameters
        ----------
        models : list of model objects
        nparticles : number of particles
        modelprior
        data
        beta
        nbatch
        model_kernel
        debug
        timing
        distancefn
        kernel_type
        kernelfn
        kernelpdffn
        perturbfn

        Returns
        -------

        """

        self.nmodel = len(models)
        self.models = copy.copy(models)
        self.data = copy.deepcopy(data)

        self.nparticles = nparticles

        self.model_prev = [0] * nparticles
        self.weights_prev = [0] * nparticles
        self.parameters_prev = [[] for _ in range(self.nparticles)]
        self.margins_prev = [0] * self.nmodel

        self.model_curr = [0] * nparticles
        self.weights_curr = [0] * nparticles
        self.parameters_curr = [[] for _ in range(self.nparticles)]
        self.margins_curr = [0] * self.nmodel

        self.b = [0] * nparticles
        self.distances = []
        self.trajectories = []

        self.distancefn = distancefn
        self.kernel_type = kernel_type
        self.kernelfn = kernelfn
        self.kernelpdffn = kernelpdffn
        self.perturbfn = perturbfn

        self.beta = beta
        self.dead_models = []
        self.nbatch = nbatch
        self.debug = debug
        self.timing = timing

        self.modelprior = modelprior[:]
        self.modelKernel = model_kernel
        self.kernel_aux = [0] * nparticles

        self.kernels = list()
        # self.kernels is a list of length the number of models
        # self.kernels[i] is a list of length 2 such that :
        # self.kernels[i][0] contains the index of the non constant parameters for the model i
        # self.kernels[i][1] contains the information required to build the kernel and given by the input_file
        # self.kernels[i][2] is filled in during the kernelfn step and contains values/matrix etc depending on kernel
        kernel_option = list()
        for i in range(self.nmodel):
            if self.kernel_type == KernelType.multivariate_normal_nn:
                # Option for K nearest neigbours - user should be able to specify
                kernel_option.append(int(nparticles / 4))
            else:
                kernel_option.append(0)

        # get the list of parameters with non constant prior
        for i in range(self.nmodel):
            ind = list()
            for j in range(self.models[i].nparameters):
                if not (self.models[i].prior[j].type == PriorType.constant):
                    ind.append(j)
            # kernel info will get set after first population
            self.kernels.append([ind, kernel_option[i], 0])

            # get
        self.special_cases = [0] * self.nmodel
        if self.kernel_type == KernelType.component_wise_uniform:

            for m in range(self.nmodel):
                all_uniform = True
                for j in range(self.models[m].nparameters):
                    if self.models[m].prior[j].type not in [PriorType.constant, PriorType.uniform]:
                        all_uniform = False
                if all_uniform:
                    self.special_cases[m] = 1
                    print "### Found special kernel case 1 for model ", m, "###"

        self.hits = []
        self.sampled = []
        self.rate = []
        self.dead_models = []
        self.sample_from_prior = True

    def run_fixed_schedule(self, epsilon, io, store_all_results=False):
        all_start_time = time.time()
        all_results = []
        for pop in range(len(epsilon)):
            start_time = time.time()
            if pop == 0 and self.sample_from_prior:
                results = self.iterate_one_population(epsilon[pop], prior=True)
            else:
                results = self.iterate_one_population(epsilon[pop], prior=False)

            if store_all_results:
                all_results.append(results)
            end_time = time.time()

            io.write_pickled(self.nmodel, self.model_prev, self.weights_prev, self.parameters_prev, self.margins_prev,
                             self.kernels)
            io.write_data(pop, results, end_time - start_time, self.models, self.data)

            if self.debug == 1:
                epsilon_string = map(lambda x: "%0.2f" % x, epsilon[pop])
                print "### iteration:%d, eps=%s, sampled=%d, accepted=%.1f%%" % (pop + 1, epsilon_string,
                                                                                  self.sampled[pop], self.rate[pop]*100)
                print "\t model marginals                  :", self.margins_prev

                if len(self.dead_models) > 0:
                    print "\t dead models                      :", self.dead_models
                if self.timing:
                    print "\t timing:                          :", end_time - start_time

        if self.timing:
            print "#### final time:", time.time() - all_start_time
        return all_results

    def run_automated_schedule(self, final_epsilon, alpha, io, store_all_results=False):
        all_start_time = time.time()
        all_results = []

        done = False
        final = False
        pop = 0
        epsilon = [1e10] * len(final_epsilon)

        while not done:
            if final:
                done = True

            start_time = time.time()
            if pop == 0 and self.sample_from_prior:
                results = self.iterate_one_population(epsilon, prior=True)
            else:
                results = self.iterate_one_population(epsilon, prior=False)

            if store_all_results:
                all_results.append(results)
            end_time = time.time()

            io.write_pickled(self.nmodel, self.model_prev, self.weights_prev, self.parameters_prev, self.margins_prev,
                             self.kernels)
            io.write_data(pop, results, end_time - start_time, self.models, self.data)

            final, epsilon = self.compute_next_epsilon(results, final_epsilon, alpha)

            if self.debug == 1:
                print "### population ", pop + 1
                print "\t sampling steps / acceptance rate :", self.sampled[pop], "/", self.rate[pop]
                print "\t model marginals                  :", self.margins_prev
                print "\t next epsilon                     :", epsilon

                if len(self.dead_models) > 0:
                    print "\t dead models                      :", self.dead_models
                if self.timing:
                    print "\t timing:                          :", end_time - start_time

            pop += 1

        if self.timing:
            print "#### final time:", time.time() - all_start_time
        return all_results

    def compute_next_epsilon(self, results, target_epsilon, alpha):
        """

        Automatically chooses a new epsilon value, based on the results from the previously used epsilon.

        Parameters
        ----------
        results :
        target_epsilon : list of minimum ('target') epsilon values, one per statistic
        alpha :

        Returns
        -------
        finished - Boolean indicating if this is the last population to run
        ret_epsilon - new value of epsilon
        """

        nepsilon = len(target_epsilon)

        distance_values = []
        for i in range(self.nparticles):
            for j in range(self.beta):
                distance_values.append(results.distances[i][j])

        # Important to remember that the initial sort on distance is done on the first distance value
        distance_values = np.sort(distance_values, axis=0)
        ntar = int(alpha * self.nparticles)

        new_epsilon = [round(distance_values[ntar, ne], 4) for ne in range(nepsilon)]
        ret_epsilon = [0] * nepsilon

        # Set the next epsilon as the new calculated epsilon
        for ne in range(nepsilon):
            ret_epsilon[ne] = new_epsilon[ne]

        # if any entry of ret_epsilon is below the target, replace with the target;
        # if all are below the target we are done
        finished = True
        for ne in range(nepsilon):
            if ret_epsilon[ne] < target_epsilon[ne] or np.fabs(ret_epsilon[ne] - target_epsilon[ne]) < 1e-3:
                ret_epsilon[ne] = target_epsilon[ne]
            else:
                finished = False

        print "new/ret epsilon:", new_epsilon, ret_epsilon, finished

        return finished, ret_epsilon

    def run_simulations(self, io):

        num_accepted = 0
        sampled = 0

        while num_accepted < self.nparticles:
            if self.debug == 2:
                print "\t****batch"
            sampled_model_indexes = self.sample_model_from_prior()
            sampled_params = self.sample_parameters_from_prior(sampled_model_indexes)

            accepted_index, distances, traj = self.simulate_and_compare_to_data(sampled_model_indexes, sampled_params,
                                                                                epsilon=0, do_comp=False)

            for i in range(self.nbatch):
                if num_accepted < self.nparticles:
                    sampled += 1

                if num_accepted < self.nparticles and accepted_index[i] > 0:

                    self.model_curr[num_accepted] = sampled_model_indexes[i]
                    if self.debug == 2:
                        print "\t****accepted", i, accepted_index[i], sampled_model_indexes[i]

                    for p in range(self.models[sampled_model_indexes[i]].nparameters):
                        self.parameters_curr[num_accepted].append(sampled_params[i][p])

                    self.b[num_accepted] = accepted_index[i]
                    self.trajectories.append(copy.deepcopy(traj[i]))
                    self.distances.append(copy.deepcopy(distances[i]))

                    num_accepted += 1

            if self.debug == 2:
                print "#### current num_accepted:", num_accepted

            if self.debug == 2:
                print "\t****end  batch num_accepted/sampled:", num_accepted, sampled

        if self.debug == 2:
            print "**** end of population num_accepted/sampled:", num_accepted, sampled

        results = AbcsmcResults(num_accepted, sampled, num_accepted / float(sampled), self.trajectories, self.distances,
                                0, self.model_curr, 0, self.parameters_curr, 0)

        io.write_data_simulation(results, self.models, self.data)

    def iterate_one_population(self, next_epsilon, prior):
        if self.debug == 2:
            print "\n\n****iterate_one_population: next_epsilon, prior", next_epsilon, prior

        naccepted = 0
        sampled = 0

        while naccepted < self.nparticles:
            if self.debug == 2:
                print "\t****batch"
            if not prior:
                sampled_model_indexes = self.sample_model()
                sampled_params = self.sample_parameters(sampled_model_indexes)
            else:
                sampled_model_indexes = self.sample_model_from_prior()
                sampled_params = self.sample_parameters_from_prior(sampled_model_indexes)

            accepted_index, distances, traj = self.simulate_and_compare_to_data(sampled_model_indexes, sampled_params,
                                                                                next_epsilon)

            for i in range(self.nbatch):
                if naccepted < self.nparticles:
                    sampled += 1

                if naccepted < self.nparticles and accepted_index[i] > 0:

                    self.model_curr[naccepted] = sampled_model_indexes[i]
                    if self.debug == 2:
                        print "\t****accepted", i, accepted_index[i], sampled_model_indexes[i]

                    for p in range(self.models[sampled_model_indexes[i]].nparameters):
                        self.parameters_curr[naccepted].append(sampled_params[i][p])

                    self.b[naccepted] = accepted_index[i]
                    self.trajectories.append(copy.deepcopy(traj[i]))
                    self.distances.append(copy.deepcopy(distances[i]))

                    naccepted += 1

            if self.debug == 2:
                print "#### current naccepted:", naccepted

            if self.debug == 2:
                print "\t****end  batch naccepted/sampled:", naccepted, sampled

        # Finished loop over particles
        if self.debug == 2:
            print "**** end of population naccepted/sampled:", naccepted, sampled

        if not prior:
            self.compute_particle_weights()
        else:
            for i in range(self.nparticles):
                self.weights_curr[i] = self.b[i]

        self.normalize_weights()
        self.update_model_marginals()

        if self.debug == 2:
            print "**** end of population: particles"
            for i in range(self.nparticles):
                print i, self.weights_curr[i], self.model_curr[i], self.parameters_curr[i]
            print self.margins_curr

        # Prepare for next population
        self.margins_prev = self.margins_curr[:]
        self.weights_prev = self.weights_curr[:]
        self.model_prev = self.model_curr[:]
        self.parameters_prev = []
        for i in range(self.nparticles):
            self.parameters_prev.append(self.parameters_curr[i][:])

        self.model_curr = [0] * self.nparticles
        self.weights_curr = [0] * self.nparticles
        self.parameters_curr = [[] for _ in range(self.nparticles)]
        self.margins_curr = [0] * self.nmodel

        self.b = [0] * self.nparticles

        # Check for dead models
        self.dead_models = []
        for j in range(self.nmodel):
            if self.margins_prev[j] < 1e-6:
                self.dead_models.append(j)

        # Compute kernels
        for model_index in range(self.nmodel):
            this_model_index = np.arange(self.nparticles)[np.array(self.model_prev) == model_index]
            this_population = np.zeros([len(this_model_index), self.models[model_index].nparameters])
            this_weights = np.zeros(len(this_model_index))

            # if we have just sampled from the prior we shall initialise the kernels using all available particles
            if prior:
                for it in range(len(this_model_index)):
                    this_population[it, :] = self.parameters_prev[this_model_index[it]][:]
                    this_weights[it] = self.weights_prev[this_model_index[it]]
                tmp_kernel = self.kernelfn(self.kernel_type, self.kernels[model_index], this_population, this_weights)
                self.kernels[model_index] = tmp_kernel[:]

            else:
                # only update the kernels if there are > 5 particles
                if len(this_model_index) > 5:
                    for it in range(len(this_model_index)):
                        this_population[it, :] = self.parameters_prev[this_model_index[it]][:]
                        this_weights[it] = self.weights_prev[this_model_index[it]]
                    tmp_kernel = self.kernelfn(self.kernel_type, self.kernels[model_index], this_population, this_weights)
                    self.kernels[model_index] = tmp_kernel[:]

        # Kernel auxilliary information
        self.kernel_aux = kernels.get_auxilliary_info(self.kernel_type, self.model_prev, self.parameters_prev,
                                                      self.models, self.kernels)[:]

        self.hits.append(naccepted)
        self.sampled.append(sampled)
        self.rate.append(naccepted / float(sampled))

        results = AbcsmcResults(naccepted,
                                sampled,
                                naccepted / float(sampled),
                                self.trajectories,
                                self.distances,
                                self.margins_prev,
                                self.model_prev,
                                self.weights_prev,
                                self.parameters_prev,
                                next_epsilon)

        self.trajectories = []
        self.distances = []

        return results
 
    def fill_values(self, particle_data):
        """
        Save particle data from pickled array into the corresponding attributes of this abc_smc object.

        Parameters
        ----------
        particle_data : particle data, in form:
         [model_pickled, weights_pickled, parameters_pickled, margins_pickled, kernel]

        """
        self.model_prev = particle_data[0][:]

        self.weights_prev = particle_data[1][:]

        self.parameters_prev = []
        for it in range(len(particle_data[2])):
            self.parameters_prev.append(particle_data[2][it][:])

        self.margins_prev = particle_data[3][:]

        self.kernels = []
        for i in range(self.nmodel):
            self.kernels.append([])
            for j in range(len(particle_data[4][i])):
                self.kernels[i].append(particle_data[4][i][j])

        self.dead_models = []
        for j in range(self.nmodel):
            if self.margins_prev[j] < 1e-6:
                self.dead_models.append(j)

        self.sample_from_prior = False

    def simulate_and_compare_to_data(self, sampled_model_indexes, sampled_params, epsilon, do_comp=True):
        """
        Perform simulations

        Parameters
        ----------
        sampled_model_indexes : list of sampled model numbers
        sampled_params : a list, each element of which is a list of sampled parameters
        epsilon : value of epsilon
        do_comp : if False, do not actually calculate distance between simulation results and experimental data, and
            instead assume this is 0.

        Returns
        -------
        accepted
        distances
        traj

        """

        if self.debug == 2:
            print '\t\t\t***simulate_and_compare_to_data'

        accepted = [0] * self.nbatch
        traj = [[] for _ in range(self.nbatch)]
        distances = [[] for _ in range(self.nbatch)]

        models = np.array(sampled_model_indexes)

        for model in range(self.nmodel):

            # create a list of indexes for the simulations corresponding to this model
            mapping = np.arange(self.nbatch)[models == model]
            if self.debug == 2:
                print "\t\t\tmodel / mapping:", model, mapping

            num_simulations = len(mapping)
            if num_simulations == 0:
                continue

            this_model_parameters = []
            for i in range(num_simulations):
                this_model_parameters.append(sampled_params[mapping[i]])

            sims = self.models[model].simulate(this_model_parameters, self.data.timepoints, num_simulations, self.beta)

            if self.debug == 2:
                print '\t\t\tsimulation dimensions:', sims.shape

            for i in range(num_simulations):
                # store the trajectories and distances in a list of length beta
                this_dist = []
                this_traj = []
                simulation_number = mapping[i]

                for k in range(self.beta):
                    sample_points = sims[i, k, :, :]
                    points = transform_data_for_fitting(self.models[model].fit, sample_points)

                    if do_comp:
                        distance = self.distancefn(points, self.data.values, this_model_parameters[i], model)
                        dist = check_below_threshold(distance, epsilon)
                    else:
                        distance = 0
                        dist = True

                    this_dist.append(distance)
                    this_traj.append(points)

                    if dist:
                        accepted[simulation_number] += 1

                    if self.debug == 2:
                        print '\t\t\tdistance/this_epsilon/mapping/b:', distance, epsilon, \
                            simulation_number, accepted[simulation_number]

                traj[simulation_number] = copy.deepcopy(this_traj)
                distances[simulation_number] = copy.deepcopy(this_dist)

        return accepted, distances, traj

    def sample_model_from_prior(self):
        """
        Returns a list of model numbers, of length self.nbatch, drawn from a categorical distribution with probabilities
         self.modelprior

        """
        models = [0] * self.nbatch
        if self.nmodel > 1:
            for i in range(self.nbatch):
                models[i] = statistics.w_choice(self.modelprior)

        return models

    def sample_model(self):
        """
        Returns a list of model numbers, of length self.nbatch, obtained by sampling from a categorical distribution
        with probabilities self.modelprior, and then perturbing with a uniform model perturbation kernel.
        """

        models = [0] * self.nbatch

        if self.nmodel > 1:
            # Sample models from prior distribution
            for i in range(self.nbatch):
                models[i] = statistics.w_choice(self.margins_prev)

            # perturb models
            if len(self.dead_models) < self.nmodel - 1:

                for i in range(self.nbatch):
                    u = rnd.uniform(low=0, high=1)

                    if u > self.modelKernel:
                        # sample randomly from other (non dead) models
                        not_available = set(self.dead_models[:])
                        not_available.add(models[i])

                        available_indexes = np.array(list(set(range(self.nmodel)) - not_available))
                        rnd.shuffle(available_indexes)
                        perturbed_model = available_indexes[0]

                        models[i] = perturbed_model
        return models[:]

    def sample_parameters_from_prior(self, sampled_model_indexes):
        """
        For each model whose index is in sampled_model_indexes, draw a sample of the corresponding parameters.

        Parameters
        ----------
        sampled_model_indexes : a list of model indexes, of length self.nbatch

        Returns
        -------
        a list of length self.nbatch, each entry of which is a list of parameter samples (whose length is
                model.nparameters for the corresponding model)

        """
        samples = []

        for i in range(self.nbatch):
            model = self.models[sampled_model_indexes[i]]
            sample = [0] * model.nparameters

            for param in range(model.nparameters):
                if model.prior[param].type == PriorType.constant:
                    sample[param] = model.prior[param].value

                if model.prior[param].type == PriorType.normal:
                    sample[param] = rnd.normal(loc=model.prior[param].mean, scale=np.sqrt(model.prior[param].variance))

                if model.prior[param].type == PriorType.uniform:
                    sample[param] = rnd.uniform(low=model.prior[param].lower_bound, high=model.prior[param].upper_bound)

                if model.prior[param].type == PriorType.lognormal:
                    sample[param] = rnd.lognormal(mean=model.prior[param].mu, sigma=np.sqrt(model.prior[param].sigma))

            samples.append(sample[:])

        return samples

    def sample_parameters(self, sampled_model_indexes):
        """
        For each model index in sampled_model_indexes, sample a set of parameters by sampling a particle from
        the corresponding model (with probability biased by the particle weights), and then perturbing using the
        parameter perturbation kernel; if this gives parameters with probability <=0 the process is repeated.

        Parameters
        ----------
        sampled_model_indexes : a list of model indexes, of length self.nbatch


        Returns
        -------
        a list of length self.nbatch, each entry of which is a list of parameter samples (whose length is
            model.nparameters for the corresponding model)

        """
        if self.debug == 2:
            print "\t\t\t***sampleTheParameter"
        samples = []

        for i in range(self.nbatch):
            model = self.models[sampled_model_indexes[i]]
            model_num = sampled_model_indexes[i]

            num_params = model.nparameters
            sample = [0] * num_params

            prior_prob = -1
            while prior_prob <= 0:

                # sample putative particle from previous population
                particle = sample_particle_from_model(self.nparticles, model_num, self.margins_prev, self.model_prev,
                                                      self.weights_prev)

                # Copy this particle's params into a new array, then perturb this in place using the parameter
                #  perturbation kernel
                for param in range(num_params):
                    sample[param] = self.parameters_prev[particle][param]
                self.perturbfn(sample, model.prior,\
                        self.kernels[model_num], self.kernel_type, \
                        self.special_cases[model_num])
                
                prior_prob = self.compute_particle_prior (sample, model)
            samples.append(sample)
        return samples


    def compute_particle_prior(self, particle, model):
        particle_prior = 1
        for n in range (len (model.prior)):
            x = 1.0
            this_prior = model.prior[n]

            if this_prior.type == PriorType.constant:
                x = 1

            if this_prior.type == PriorType.normal:
                x = statistics.get_pdf_gauss(this_prior.mean, np.sqrt(this_prior.variance), particle[n])

            if this_prior.type == PriorType.uniform:
                x = statistics.get_pdf_uniform(this_prior.lower_bound, this_prior.upper_bound, particle[n])

            if this_prior.type == PriorType.lognormal:
                x = statistics.get_pdf_lognormal(this_prior.mu, np.sqrt(this_prior.sigma), particle[n])

            particle_prior = particle_prior * x
        return particle_prior


    def compute_particle_weights(self):
        """
        Calculate the weight of each particle.
        This is given by $w_t^i = \frac{\pi(M_t^i, \theta_t^i) P_{t-1}(M_t^i = M_{t-1}) }{S_1 S_2 }$, where
        $S_1 = \sum_{j \in M} P_{t-1}(M^j_{t-1}) KM_t(M_t^i | M^j_{t-1})$ and
        $S_2 = \sum_{k \in M_t^i = M_{t-1}} w^k_{t-1} K_{t, M^i}(\theta_t^i | \theta_{t-1}^k)$

        (See p.4 of SOM to 'Bayesian design of synthetic biological systems', except that here we have moved model
        marginal out of s2 into a separate term)
        """
        if self.debug == 2:
            print "\t***computeParticleWeights"

        for k in range(self.nparticles):
            model_num = self.model_curr[k]
            model = self.models[model_num]

            this_param = self.parameters_curr[k]

            model_prior = self.modelprior[model_num]

            particle_prior = 1
            for n in range(len(self.parameters_curr[k])):
                x = 1.0
                this_prior = model.prior[n]

                if this_prior.type == PriorType.constant:
                    x = 1

                if this_prior.type == PriorType.normal:
                    x = statistics.get_pdf_gauss(this_prior.mean, np.sqrt(this_prior.variance), this_param[n])

                if this_prior.type == PriorType.uniform:
                    x = statistics.get_pdf_uniform(this_prior.lower_bound, this_prior.upper_bound, this_param[n])

                if this_prior.type == PriorType.lognormal:
                    x = statistics.get_pdf_lognormal(this_prior.mu, np.sqrt(this_prior.sigma), this_param[n])

                particle_prior = particle_prior * x

            # self.b[k] is a variable indicating whether the simulation corresponding to particle k was accepted
            numerator = self.b[k] * model_prior * particle_prior

            s1 = 0
            for i in range(self.nmodel):
                s1 += self.margins_prev[i] * get_model_kernel_pdf(model_num, i, self.modelKernel, self.nmodel,
                                                                  self.dead_models)
            s2 = 0
            for j in range(self.nparticles):
                if int(model_num) == int(self.model_prev[j]):

                    if self.debug == 2:
                        print "\tj, weights_prev, kernelpdf", j, self.weights_prev[j],
                        self.kernelpdffn(this_param, self.parameters_prev[j], model.prior,
                                         self.kernels[model_num], self.kernel_aux[j], self.kernel_type)

                    kernel_pdf = self.kernelpdffn(this_param, self.parameters_prev[j], model.prior,
                                                  self.kernels[model_num], self.kernel_aux[j], self.kernel_type)
                    s2 += self.weights_prev[j] * kernel_pdf

                if self.debug == 2:
                    print "\tnumer/s1/s2/m(t-1) : ", numerator, s1, s2, self.margins_prev[model_num]

            self.weights_curr[k] = self.margins_prev[model_num] * numerator / (s1 * s2)

    def normalize_weights(self):
        """
        Normalize weights by dividing each by the total.
        """
        n = sum(self.weights_curr)
        for i in range(self.nparticles):
            self.weights_curr[i] /= float(n)

    def update_model_marginals(self):
        """
        Re-calculate the marginal probability of each model as the sum of the weights of the corresponding particles.
        """
        for model in range(self.nmodel):
            self.margins_curr[model] = 0
            for particle in range(self.nparticles):
                if int(self.model_curr[particle]) == int(model):
                    self.margins_curr[model] += self.weights_curr[particle]


def sample_particle_from_model(nparticle, selected_model, margins_prev, model_prev, weights_prev):
    """
    Select a particle from those in the previous generation whose model was the currently selected model, weighted by
    their previous weight.

    Parameters
    ----------
    nparticle : number of particles
    selected_model : index of the currently selected model
    margins_prev : the marginal probability of the selected model at the previous iteration (nb. this is the sum of the
        weights of the corresponding particles)
    model_prev : list recording the model index corresponding to each particle from the previous iteration
    weights_prev : list recording the weight of each particle from the previous iteration

    Returns
    -------
    the index of the selected particle
    """
    u = rnd.uniform(low=0, high=margins_prev[selected_model])
    f = 0

    for i in range(nparticle):
        if int(model_prev[i]) == int(selected_model):
            f = f + weights_prev[i]
            if f > u:
                return i
    return nparticle - 1


def transform_data_for_fitting(fitting_instruction, sample_points):
    """
    Given the results of a simulation, evaluate given functions of the state variables of the model.

    This accounts for the correspondance between species defined in the model being simulated and the experimental data
    being fit.

    Parameters
    ----------
    fitting_instruction : list of functions, one per dimension of the data to be fitted. Each is a string representation
        of an expression of the state variables of the model; dimension n  is represented by 'sample_points[:,n];.

    sample_points : a numpy.ndarray of simulation results, with shape (num_timepoints, model_dimension)

    Returns
    -------
    transformed_points : a numpy.ndarray of transformed simulation results, with shape (num_timepoints, data_dimension)

    """

    if fitting_instruction is not None:
        transformed_points = np.zeros([len(sample_points), len(fitting_instruction)])
        for i in range(len(fitting_instruction)):
            transformed_points[:, i] = np.squeeze(eval(fitting_instruction[i]))
    else:
        transformed_points = sample_points

    return transformed_points[:]


def get_model_kernel_pdf(new_model, old_model, model_k, num_models, dead_models):
    """
    Returns the probability of model number m0 being perturbed into model number m (assuming neither is dead).

    This assumes a uniform model perturbation kernel: with probability modelK the model is not perturbed; with
    probability (1-modelK) it is replaced by a model randomly chosen from the non-dead models (including the current
    model).

    Parameters
    ----------
    new_model : index of next model
    old_model : index of previous model
    model_k : model (non)-perturbation probability
    num_models : total number of models
    dead_models : number of models which are 'dead'
    """

    num_dead_models = len(dead_models)

    if num_dead_models == num_models - 1:
        return 1.0
    else:
        if new_model == old_model:
            return model_k
        else:
            return (1 - model_k) / (num_models - num_dead_models)


def check_below_threshold(distance, epsilon):
    """
    Return true if each element of distance is less than the corresponding entry of epsilon (and non-negative)

    Parameters
    ----------
    distance : list of distances
    epsilon : list of maximum acceptable distances

    """

    accepted = False
    for i in range(len(epsilon)):
        if epsilon[i] >= distance[i] >= 0:
            accepted = True
        else:
            accepted = False
            break
    return accepted
