"""
Core code of Dedalus script

Modified by Mikhail Schee from the script for 2D Rayleigh-Benard convection in the Dedalus example files.

*This script is NOT meant to be run directly.*

To make a new experiment, run:
    $ bash make_new_exp.sh -n <my_new_exp>

This will create a new directory for your experiment under `_experiments`. Edit the switchboard and select_modules files in that directory to specify parameters of the experiment before running.

To run an experiment, run (-c, -l, and -v are optional):
    $ bash run.sh -n <my_new_exp> -c 2 -l 1 -v 1

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
# Checking command line arguments
import sys
# Arguments must be passed in the correct order
arg_array = sys.argv
filename = str(arg_array[0])
switchboard = str(arg_array[1])

if rank==0:
    # Check number of arguments passed in
    if (len(arg_array) != 2):
        print("Wrong number of arguments passed to core code")
        print("")

###############################################################################
# Import SwitchBoard Parameters (sbp)
#   This runs the switchboard file, which moves files around when the code is run for the first time
#   This import assumes the switchboard is in the same directory as the core code
import switchboard as sbp

# Call parameters by sbp.some_param. For example:
nx = sbp.n_x
nz = sbp.n_z

###############################################################################
# Create bases and domain
x_basis = de.Fourier('x',   nx, interval=(sbp.x_sim_0, sbp.x_sim_f), dealias=sbp.dealias)
z_basis = de.Chebyshev('z', nz, interval=(sbp.z_sim_f, sbp.z_sim_0), dealias=sbp.dealias)
domain = de.Domain([x_basis, z_basis], grid_dtype=np.float64)
# Get x and z grids into variables. Used for BP and initial conditions
x = domain.grid(0)
z = domain.grid(1)

###############################################################################
# 2D Boussinesq hydrodynamics
problem = de.IVP(domain, variables=['p','b','u','w','bz','uz','wz'])
# From Nico: all variables are dirchlet by default, so only need to
#   specify those that are not dirchlet (variables w/o top & bottom bc's)
problem.meta['p','bz','uz','wz']['z']['dirichlet'] = False
# Parameters for the equations of motion
problem.parameters['NU'] = sbp.nu
problem.parameters['KA'] = sbp.kappa
problem.parameters['N0'] = sbp.N_0

###############################################################################
# Forcing from the boundary

# Polarization relation from boundary forcing file
PolRel = sbp.PolRel
# Creating forcing amplitudes
for fld in ['u', 'w', 'b']:#, 'p']:
    BF = domain.new_field()
    BF.meta['x']['constant'] = True  # means the NCC is constant along x
    BF['g'] = PolRel[fld]
    problem.parameters['BF' + fld] = BF  # pass function in as a parameter.
    del BF
# Parameters for boundary forcing
problem.parameters['kx']        = sbp.k_x
problem.parameters['kz']        = sbp.k_z
problem.parameters['omega']     = sbp.omega
problem.parameters['grav']      = sbp.g # can't use 'g': Dedalus uses that for grid
problem.parameters['T']         = sbp.T # [s] period of oscillation
problem.parameters['nT']        = sbp.nT # number of periods for the ramp
# Spatial window and temporal ramp for boundary forcing
problem.parameters['slope']     = sbp.bf_slope
problem.parameters['left_edge'] = sbp.bfl_edge
problem.parameters['right_edge']= sbp.bfr_edge
problem.substitutions['window'] = sbp.window
problem.substitutions['ramp']   = sbp.ramp
# Substitutions for boundary forcing (see C-R & B eq 13.7)
problem.substitutions['fu']     = sbp.fu
problem.substitutions['fw']     = sbp.fw
problem.substitutions['fb']     = sbp.fb
#problem.substitutions['fp']     = sbp.fp

###############################################################################
# Background Profile (BP) as an NCC
BP = domain.new_field()
BP.meta['x']['constant'] = True  # means the NCC is constant along x
BP_array = sbp.build_bp_array(z)
BP['g'] = BP_array
problem.parameters['BP'] = BP

###############################################################################
# Sponge Layer (SL) as an NCC
SL = domain.new_field()
SL.meta['x']['constant'] = True  # means the NCC is constant along x
SL_array = sbp.build_sl_array(z)
SL['g'] = SL_array
problem.parameters['SL'] = SL

###############################################################################
# Rayleigh Friction (RF) as an NCC
RF = domain.new_field()
RF.meta['x']['constant'] = True  # means the NCC is constant along x
RF_array = sbp.build_rf_array(z)
RF['g'] = RF_array
problem.parameters['RF'] = RF

###############################################################################
# Equations of motion - See physics module eqs_and_bcs
problem.add_equation(sbp.eq1_mc)
problem.add_equation(sbp.eq2_es)
problem.add_equation(sbp.eq3_hm)
problem.add_equation(sbp.eq4_vm)
problem.add_equation(sbp.eq5_bz)
problem.add_equation(sbp.eq6_uz)
problem.add_equation(sbp.eq7_wz)

###############################################################################
# Boundary contitions - See physics module eqs_and_bcs
problem.add_bc(sbp.bc1)
problem.add_bc(sbp.bc2)
problem.add_bc(sbp.bc3, condition=sbp.bc3_cond) # redunant in constant mode (nx==0)
problem.add_bc(sbp.bc4)
problem.add_bc(sbp.bc5)
problem.add_bc(sbp.bc6)
problem.add_bc(sbp.bc7, condition=sbp.bc7_cond) # because of above redundancy

###############################################################################
# Build solver
solver = problem.build_solver(de.timesteppers.RK222)
logger.info('Solver built')

###############################################################################
# Initial conditions or restart
if not pathlib.Path(sbp.restart_file).exists():

    # Initial conditions
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
    b['g'] = pert * 0.0 # F * pert
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
solver.stop_wall_time = sbp.stop_wall_time * 60.0 # to get minutes
solver.stop_iteration = sbp.stop_iteration

###############################################################################
# Analysis
def add_new_file_handler(snapshot_directory, dt=sbp.snap_dt):
    return solver.evaluator.add_file_handler(snapshot_directory, sim_dt=dt, max_writes=sbp.snap_max_writes, mode=fh_mode)

# Add file handler for snapshots and output state of variables
snapshots = add_new_file_handler(sbp.snapshots_dir)
snapshots.add_system(solver.state)

# Add file handlers for all vertical profiles
if sbp.take_vp_snaps:
    vp_snapshots = add_new_file_handler(sbp.snapshots_dir + '/' + sbp.vp_snap_dir, dt=stop_sim_time)
    for vp_dict in sbp.vp_snap_dicts:
        if vp_dict['take_vp_snaps']:
            vp_snapshots.add_task(vp_dict['vp_task'], layout='g', name=vp_dict['vp_task_name'])

# Add file handler for auxiliary snapshots
aux_snapshots = add_new_file_handler(sbp.snapshots_dir + '/' + sbp.aux_snap_dir, dt=dt)
# Add file handlers for all energy flux components
if sbp.take_ef_snaps or sbp.take_ef_comp:
    for ef_dict in sbp.ef_snap_dicts:
        if ef_dict['take_ef_snaps']:
            aux_snapshots.add_task(ef_dict['ef_task'], layout='g', name=ef_dict['ef_task_name'])

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
# Set logger parameters if using stop_time or stop_oscillations
use_sst = sbp.use_stop_sim_time
if use_sst:
    endtime_str   = 'Sim end time: %f'
    iteration_str = 'Iteration: %i, Time: %e, dt: %e'
    time_factor   = 1.0
else:
    endtime_str   = 'Sim end period: %f'
    iteration_str = 'Iteration: %i, t/T: %e, dt/T: %e'
    time_factor   = sbp.T

###############################################################################
# Main loop
try:
    logger.info(endtime_str %(solver.stop_sim_time/time_factor))
    logger.info('Starting loop')
    start_time = time.time()
    while solver.ok:
        # Adaptive time stepping controlled from switchboard
        if (sbp.adapt_dt):
            dt = CFL.compute_dt()
        dt = solver.step(dt)
        if (solver.iteration-1) % 10 == 0:
            logger.info(iteration_str %(solver.iteration, solver.sim_time/time_factor, dt/time_factor))
            logger.info(sbp.flow_log_message.format(flow.max(sbp.flow_name)))
            if np.isnan(flow.max(sbp.flow_name)):
                raise NameError('Code blew up it seems')
except:
    logger.error('Exception raised, triggering end of main loop.')
    raise
finally:
    end_time = time.time()
    logger.info('Iterations: %i' %solver.iteration)
    logger.info(endtime_str %(solver.sim_time/time_factor))
    logger.info('Run time: %.2f sec' %(end_time-start_time))
    logger.info('Run time: %f cpu-hr' %((end_time-start_time)/60/60*domain.dist.comm_cart.size))
