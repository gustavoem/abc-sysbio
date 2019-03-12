import os

import numpy as np
import pycuda.driver as driver
import pycuda.compiler as compiler

import cudasim.solvers.cuda.Simulator as sim
import cudasim

class Lsoda(sim.Simulator):
    _param_tex = None

    _step_code = None
    _runtimeCompile = True

    _lsoda_source_ = """
    
    extern "C"{

    #include <stdio.h>
    
    __device__ myFex myfex;
    __device__ myJex myjex;
    
    __global__ void init_common(){
    int tid = blockDim.x * blockIdx.x + threadIdx.x;
    cuLsodaCommonBlockInit( &(common[tid]) );
    }
    
    __global__ void cuLsoda(int *neq, double *y, double *t, double *tout, int *itol, 
                double *rtol, double *atol, int *itask, int *istate, int *iopt, 
                            double *rwork, int *lrw, int *iwork, int *liw, int *jt)
    {
    int tid = blockDim.x * blockIdx.x + threadIdx.x;

    //if(tid==0){
    //printf("I am thread time %d %f\\n", tid, t[0] );
    //}

    dlsoda_(myfex, neq+tid, y+tid*NSPECIES, t+tid, tout+tid, itol+tid, rtol+tid, atol+tid, itask+tid, 
        istate+tid, iopt+tid, rwork+tid*RSIZE, lrw+tid, iwork+tid*ISIZE, liw+tid, myjex, jt+tid, &(common[tid]) );

    //if(tid==0){
    //printf("I am done %d %f\\n", tid, t[0] );
    //}
    }
    }
    
    """

    def _compile_at_runtime(self, step_code, parameters):
        # set beta to 1: repeats are pointless as simulation is deterministic
        self._beta = 1

        fc = open(os.path.join(os.path.split(os.path.realpath(__file__))[0], 'cuLsoda_all.cu'), 'r')

        _sourceFromFile_ = fc.read()

        _isize_ = "#define ISIZE " + repr(20 + self._speciesNumber) + "\n"
        _rsize_ = "#define RSIZE " + repr(22 + self._speciesNumber * max(16, self._speciesNumber + 9)) + "\n"

        _textures_ = "texture<float, 2, cudaReadModeElementType> param_tex;\n"
        _common_block_ = "__device__ struct cuLsodaCommonBlock common[" + repr(1 * 1) + "];\n"
        _code_ = _isize_ + _rsize_ + _textures_ + step_code + _sourceFromFile_ + _common_block_ + self._lsoda_source_

        if self._dump:
            of = open("full_ode_code.cu", "w")
            print >> of, _code_

        # dummy compile to determine optimal blockSize and gridSize
        compiled = compiler.SourceModule(_code_, nvcc="nvcc", options=[], no_extern_c=True, keep=False)

        blocks, threads = self._get_optimal_gpu_param(parameters, compiled.get_function("cuLsoda"))
        blocks = self._MAXBLOCKSPERDEVICE

        # real compile
        _common_block_ = "__device__ struct cuLsodaCommonBlock common[" + repr(blocks * threads) + "];\n"
        _code_ = _isize_ + _rsize_ + _textures_ + step_code + _sourceFromFile_ + _common_block_ + self._lsoda_source_

        if self._dump:
            of = open("full_ode_code.cu", "w")
            print >> of, _code_

        compiled = compiler.SourceModule(_code_, nvcc="nvcc", options=[], no_extern_c=True, keep=False)

        self._param_tex = compiled.get_texref("param_tex")

        lsoda_kernel = compiled.get_function("cuLsoda")
        return compiled, lsoda_kernel

    def _run_simulation(self, parameters, init_values, blocks, threads, in_atol=1e-6, in_rtol=1e-6):

        total_threads = threads * blocks
        experiments = len(parameters)

        neqn = self._speciesNumber

        # compile
        init_common_kernel = self._completeCode.get_function("init_common")
        init_common_kernel(block=(threads, 1, 1), grid=(blocks, 1))

        # output array
        ret_xt = np.zeros([total_threads, 1, self._resultNumber, self._speciesNumber])
        ret_istate = np.ones([total_threads], dtype=np.int32)

        # calculate sizes of work spaces
        isize = 20 + self._speciesNumber
        rsize = 22 + self._speciesNumber * max(16, self._speciesNumber + 9)

        # local variables
        t = np.zeros([total_threads], dtype=np.float64)
        jt = np.zeros([total_threads], dtype=np.int32)
        neq = np.zeros([total_threads], dtype=np.int32)
        itol = np.zeros([total_threads], dtype=np.int32)
        iopt = np.zeros([total_threads], dtype=np.int32)
        rtol = np.zeros([total_threads], dtype=np.float64)
        iout = np.zeros([total_threads], dtype=np.int32)
        tout = np.zeros([total_threads], dtype=np.float64)
        itask = np.zeros([total_threads], dtype=np.int32)
        istate = np.zeros([total_threads], dtype=np.int32)
        atol = np.zeros([total_threads], dtype=np.float64)

        liw = np.zeros([total_threads], dtype=np.int32)
        lrw = np.zeros([total_threads], dtype=np.int32)
        iwork = np.zeros([isize * total_threads], dtype=np.int32)
        rwork = np.zeros([rsize * total_threads], dtype=np.float64)
        y = np.zeros([self._speciesNumber * total_threads], dtype=np.float64)

        for i in range(total_threads):
            neq[i] = neqn
            t[i] = 0
            itol[i] = 1
            itask[i] = 1
            istate[i] = 1
            iopt[i] = 0
            jt[i] = 2
            atol[i] = in_atol
            rtol[i] = in_rtol

            liw[i] = isize
            lrw[i] = rsize

            try:
                # initial conditions
                for j in range(self._speciesNumber):
                    # loop over species
                    y[i * self._speciesNumber + j] = init_values[i][j]
                    ret_xt[i, 0, 0, j] = init_values[i][j]
            except IndexError:
                pass

        # allocate on device
        d_t = driver.mem_alloc(t.size * t.dtype.itemsize)
        d_jt = driver.mem_alloc(jt.size * jt.dtype.itemsize)
        d_neq = driver.mem_alloc(neq.size * neq.dtype.itemsize)
        d_liw = driver.mem_alloc(liw.size * liw.dtype.itemsize)
        d_lrw = driver.mem_alloc(lrw.size * lrw.dtype.itemsize)
        d_itol = driver.mem_alloc(itol.size * itol.dtype.itemsize)
        d_iopt = driver.mem_alloc(iopt.size * iopt.dtype.itemsize)
        d_rtol = driver.mem_alloc(rtol.size * rtol.dtype.itemsize)
        d_iout = driver.mem_alloc(iout.size * iout.dtype.itemsize)
        d_tout = driver.mem_alloc(tout.size * tout.dtype.itemsize)
        d_itask = driver.mem_alloc(itask.size * itask.dtype.itemsize)
        d_istate = driver.mem_alloc(istate.size * istate.dtype.itemsize)
        d_y = driver.mem_alloc(y.size * y.dtype.itemsize)
        d_atol = driver.mem_alloc(atol.size * atol.dtype.itemsize)
        d_iwork = driver.mem_alloc(iwork.size * iwork.dtype.itemsize)
        d_rwork = driver.mem_alloc(rwork.size * rwork.dtype.itemsize)

        # copy to device
        driver.memcpy_htod(d_t, t)
        driver.memcpy_htod(d_jt, jt)
        driver.memcpy_htod(d_neq, neq)
        driver.memcpy_htod(d_liw, liw)
        driver.memcpy_htod(d_lrw, lrw)
        driver.memcpy_htod(d_itol, itol)
        driver.memcpy_htod(d_iopt, iopt)
        driver.memcpy_htod(d_rtol, rtol)
        driver.memcpy_htod(d_iout, iout)
        driver.memcpy_htod(d_tout, tout)
        driver.memcpy_htod(d_itask, itask)
        driver.memcpy_htod(d_istate, istate)
        driver.memcpy_htod(d_y, y)
        driver.memcpy_htod(d_atol, atol)
        driver.memcpy_htod(d_iwork, iwork)
        driver.memcpy_htod(d_rwork, rwork)

        param = np.zeros((total_threads, self._parameterNumber), dtype=np.float32)
        try:
            for i in range(len(parameters)):
                for j in range(self._parameterNumber):
                    param[i][j] = parameters[i][j]
        except IndexError:
            pass

        # parameter texture
        ary = sim.create_2d_array(param)
        sim.copy_2d_host_to_array(ary, param, self._parameterNumber * 4, total_threads)
        self._param_tex.set_array(ary)

        if self._dt <= 0:
            for i in range(self._resultNumber):

                for j in range(total_threads):
                    tout[j] = self._timepoints[i]
                driver.memcpy_htod(d_tout, tout)

                self._compiledRunMethod(d_neq, d_y, d_t, d_tout, d_itol, d_rtol, d_atol, d_itask, d_istate,
                                        d_iopt, d_rwork, d_lrw, d_iwork, d_liw, d_jt, block=(threads, 1, 1),
                                        grid=(blocks, 1))

                driver.memcpy_dtoh(t, d_t)
                driver.memcpy_dtoh(y, d_y)
                driver.memcpy_dtoh(istate, d_istate)

                for j in range(total_threads):
                    for k in range(self._speciesNumber):
                        ret_xt[j, 0, i, k] = y[j * self._speciesNumber + k]

                    if istate[j] < 0:
                        ret_istate[j] = 0

                        # end of loop over time points

        else:
            tt = self._timepoints[0]

            for i in range(self._resultNumber):
                while 1:

                    next_time = min(tt + self._dt, self._timepoints[i])

                    for j in range(total_threads):
                        tout[j] = next_time
                    driver.memcpy_htod(d_tout, tout)

                    self._compiledRunMethod(d_neq, d_y, d_t, d_tout, d_itol, d_rtol, d_atol, d_itask, d_istate,
                                            d_iopt, d_rwork, d_lrw, d_iwork, d_liw, d_jt, block=(threads, 1, 1),
                                            grid=(blocks, 1))

                    driver.memcpy_dtoh(t, d_t)
                    driver.memcpy_dtoh(y, d_y)
                    driver.memcpy_dtoh(istate, d_istate)

                    if np.abs(next_time - self._timepoints[i]) < 1e-5:
                        tt = next_time
                        break

                    tt = next_time

                for j in range(total_threads):
                    for k in range(self._speciesNumber):
                        ret_xt[j, 0, i, k] = y[j * self._speciesNumber + k]

                    if istate[j] < 0:
                        ret_istate[j] = 0

        # loop over and check ret_istate
        # it will will be zero if there was problems
        for j in range(total_threads):
            if ret_istate[j] == 0:
                for i in range(self._resultNumber):
                    for k in range(self._speciesNumber):
                        ret_xt[j, 0, i, k] = float('NaN')

        return ret_xt[0:experiments]
