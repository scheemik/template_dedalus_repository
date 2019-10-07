"""
Core code of Dedalus script

Modified by Mikhail Schee from the script for 2D Rayleigh-Benard convection in the Dedalus example files.

This script is NOT meant to be run directly.

The parameters of an experiment are controlled through the switchboard file.
To start a new experiment, run the `make_new_exp.sh` script using the `-n` flag to specify the experiment's name and the `-s` flag to specify the switchboard file.
    $ sh make_new_exp.sh -n my_new_exp -s switchboard-default.py

This will create a new directory for your experiment under `_experiments`. Edit the switchboard file in that directory to specify the parameters of the experiment before running.

To run an experiment, run the `run.sh` script with the `-n`, `-c`, `-l`, `-v` flags, as specified in that script's header. Running an experiment again will overwrite the old outputs.
    $ sh run.sh -n my_new_exp -c 2 -l 1 -v 1

This script can restart the simulation from the last save of the original
output to extend the integration.  This requires that the output files from
the original simulation are merged, and the last is symlinked or copied to
`restart.h5`.

To run the original example and the restart, you could use:
    $ mpiexec -n 4 python3 rayleigh_benard.py
    $ mpiexec -n 4 python3 -m dedalus merge_procs snapshots
    $ ln -s snapshots/snapshots_s2.h5 restart.h5
    $ mpiexec -n 4 python3 rayleigh_benard.py

The simulations should take a few process-minutes to run.

"""

import numpy as np
from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()

import time
import pathlib

from dedalus import public as de
from dedalus.extras import flow_tools

import logging
logger = logging.getLogger(__name__)

###############################################################################
# Command line arguments
import sys
# Arguments must be passed in the correct order
arg_array = sys.argv
filename = str(arg_array[0])
switchboard = str(arg_array[1])

if rank==0:
    # Check number of arguments passed in
    if (len(arg_array) != 2):
        print("Wrong number of arguments passed to core code")
    print('Core code filename:', filename)
    print('Using switchboard:', switchboard)
    print("")

###############################################################################
# Importing parameters from switchboard
import importlib

# Import SwitchBoard Parameters (sbp)
sbp = importlib.import_module(switchboard)

# Call parameters from sbp.some_param. For example:
nx = sbp.n_x #256
nz = sbp.n_z #64

###############################################################################
# Create bases and domain
x_basis = de.Fourier('x',   nx, interval=(0, sbp.L_x), dealias=sbp.dealias)
z_basis = de.Chebyshev('z', nz, interval=(-sbp.L_z/2, sbp.L_z/2), dealias=sbp.dealias)
domain = de.Domain([x_basis, z_basis], grid_dtype=np.float64)

# 2D Boussinesq hydrodynamics
problem = de.IVP(domain, variables=['p','b','u','w','bz','uz','wz'])
problem.meta['p','b','u','w']['z']['dirichlet'] = True
problem.parameters['P'] = (sbp.Rayleigh * sbp.Prandtl)**(-1/2)
problem.parameters['R'] = (sbp.Rayleigh / sbp.Prandtl)**(-1/2)
problem.parameters['F'] = F = 1
problem.add_equation("dx(u) + wz = 0")
problem.add_equation("dt(b) - P*(dx(dx(b)) + dz(bz)) - F*w       = -(u*dx(b) + w*bz)")
problem.add_equation("dt(u) - R*(dx(dx(u)) + dz(uz)) + dx(p)     = -(u*dx(u) + w*uz)")
problem.add_equation("dt(w) - R*(dx(dx(w)) + dz(wz)) + dz(p) - b = -(u*dx(w) + w*wz)")
problem.add_equation("bz - dz(b) = 0")
problem.add_equation("uz - dz(u) = 0")
problem.add_equation("wz - dz(w) = 0")
problem.add_bc("left(b) = 0")
problem.add_bc("left(u) = 0")
problem.add_bc("left(w) = 0")
problem.add_bc("right(b) = 0")
problem.add_bc("right(u) = 0")
problem.add_bc("right(w) = 0", condition="(nx != 0)")
problem.add_bc("right(p) = 0", condition="(nx == 0)")

# Build solver
solver = problem.build_solver(de.timesteppers.RK222)
logger.info('Solver built')

###############################################################################
# Initial conditions or restart
if not pathlib.Path(sbp.restart_file).exists():

    # Initial conditions
    x = domain.grid(0)
    z = domain.grid(1)
    b = solver.state['b']
    bz = solver.state['bz']

    # Random perturbations, initialized globally for same results in parallel
    gshape = domain.dist.grid_layout.global_shape(scales=1)
    slices = domain.dist.grid_layout.slices(scales=1)
    rand = np.random.RandomState(seed=42)
    noise = rand.standard_normal(gshape)[slices]

    # Linear background + perturbations damped at walls
    zb, zt = z_basis.interval
    pert =  1e-3 * noise * (zt - z) * (z - zb)
    b['g'] = F * pert
    b.differentiate('z', out=bz)

    # Timestepping and output
    dt = sbp.dt
    stop_sim_time = sbp.stop_sim_time
    fh_mode = 'overwrite'

else:
    # Restart
    write, last_dt = solver.load_state(restart_file, -1)

    # Timestepping and output
    dt = last_dt
    stop_sim_time = sbp.stop_sim_time + sbp.restart_add_time
    fh_mode = 'append'

###############################################################################
# Integration parameters
solver.stop_sim_time  = stop_sim_time # deliberately not sbp
solver.stop_wall_time = sbp.stop_wall_time
solver.stop_iteration = sbp.stop_iteration

###############################################################################
# Analysis
snapshots = solver.evaluator.add_file_handler(sbp.snapshots_dir, sim_dt=sbp.snap_dt, max_writes=sbp.snap_max_writes, mode=fh_mode)
snapshots.add_system(solver.state)

###############################################################################
# CFL
CFL = flow_tools.CFL(solver, initial_dt=dt, cadence=sbp.CFL_cadence,
                     safety=sbp.CFL_safety, max_change=sbp.CFL_max_change,
                     min_change=sbp.CFL_min_change, max_dt=sbp.CFL_max_dt,
                     threshold=sbp.CFL_threshold)
CFL.add_velocities(('u', 'w'))

###############################################################################
# Flow properties
flow = flow_tools.GlobalFlowProperty(solver, cadence=sbp.flow_cadence)
flow.add_property(sbp.flow_property, name=sbp.flow_name)

###############################################################################
# Main loop
try:
    logger.info('Sim end time: %e' %(solver.stop_sim_time))
    logger.info('Starting loop')
    start_time = time.time()
    while solver.ok:
        dt = CFL.compute_dt()
        dt = solver.step(dt)
        if (solver.iteration-1) % 10 == 0:
            logger.info('Iteration: %i, Time: %e, dt: %e' %(solver.iteration, solver.sim_time, dt))
            logger.info('Max Re = %f' %flow.max(sbp.flow_name))
except:
    logger.error('Exception raised, triggering end of main loop.')
    raise
finally:
    end_time = time.time()
    logger.info('Iterations: %i' %solver.iteration)
    logger.info('Sim end time: %f' %solver.sim_time)
    logger.info('Run time: %.2f sec' %(end_time-start_time))
    logger.info('Run time: %f cpu-hr' %((end_time-start_time)/60/60*domain.dist.comm_cart.size))
