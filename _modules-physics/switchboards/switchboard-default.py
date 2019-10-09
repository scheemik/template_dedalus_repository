# Switchboard for Dedalus experiment
#   Default switchboard
"""
Description:

This is the default switchboard for the Dedalus experiment. This file will be used when there has been no other switchboard specified.
"""

import numpy as np

###############################################################################
# Simulation parameters

# Number of grid points in each dimension
n_x = 256                   # []
n_z = 64                    # []
# Dealias factor
dealias = 3/2               # []
# Stopping conditions for the simulation
stop_n_periods = 10         # [] oscillation periods
stop_wall_time = 60         # [minutes]
stop_iteration = np.inf     # []
stop_sim_time  = 10         # [s] to be calculated from stop_n_periods later
# Time step size
dt = 0.125
# Determine whether adaptive time stepping is on or off
adapt_dt = True             # {T/F}
# Restart simulation parameters
restart_add_time = stop_sim_time
restart_file  = 'restart.h5'

###############################################################################
# Domain parameters

# Dimensions of simulated domain
L_x = 4.0                   # [m]
L_z = 1.0                   # [m]
z_t = 0.0

# Dimensions of displayed domain (should be leq simulated domain)
L_x_dis = 1.0               # [m]
L_z_dis = 1.0               # [m]

# Display buffer (measured from top left corner)
Dis_buff_x = 1.0            # [m]
Dis_buff_z = 0.0            # [m]

# Upper left corner of display domain is always (0, 0)
#   Therefore, the upper left corner of the simulated domain is
x_sim_0 = -Dis_buff_x
z_sim_0 =  Dis_buff_z

# not sure why, but this needs to be here, above imports from bf file
lam_x = L_x / 3.0

###############################################################################
# Physical parameters
nu          = 1.0E-6        # [m^2/s] Viscosity (momentum diffusivity)
kappa       = 1.4E-7        # [m^2/s] Thermal diffusivity
Prandtl     = nu / kappa    # [] Prandtl number, about 7.0 for water at 20 C
Rayleigh    = 1e6
g           = 9.81          # [m/s^2] Acceleration due to gravity

###############################################################################
# Select physics modules

# Boundary forcing
bf_module       = 'bf_default'

###############################################################################
# Snapshot parameters
snapshots_dir   = 'snapshots'
snap_dt         = 0.25
snap_max_writes = 50

###############################################################################
# CFL parameters
CFL_cadence     = 10
CFL_safety      = 1
CFL_max_change  = 1.5
CFL_min_change  = 0.5
CFL_max_dt      = 0.125
CFL_threshold   = 0.05

###############################################################################
# Flow properties
flow_cadence    = 10
flow_property   = "(kx*u + kz*w)/omega"
flow_name       = 'Lin_Criterion'
flow_log_message= 'Max linear criterion = {0:f}'

###############################################################################
################    Shouldn't need to edit below here    #####################
###############################################################################
# Imports for preparing physics modules
from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
from shutil import copy2, rmtree
import os
if rank==0:
    print('Preparing physics modules')
    print('')
# Add path to _modules-physics so python knows to look there on imports
import sys
p_module_dir = './_modules-physics/'
sys.path.insert(0, p_module_dir)

###############################################################################
# Boundary forcing

# Move over boundary forcing file
bf_path = p_module_dir + 'boundary_forcing/' + bf_module + '.py'
if os.path.isfile(bf_path):
    copy2(bf_path, p_module_dir + 'boundary_forcing.py')

import boundary_forcing as bf
# See boundary forcing file for the meaning of these variables
N_0     = bf.N_0        # [rad s^-1]
#lam_x   = L_x / 3.0     # [m]
omega   = bf.omega      # [rad s^-1]
theta   = bf.theta      # [rad]
k_x     = bf.k_x        # [m^-1]
k       = bf.k          # [m^-1]
k_z     = bf.k_z        # [m^-1]
T       = bf.T          # [s]
A       = bf.A          # []
nT      = bf.nT         # []
PolRel  = bf.PolRel     # Dictionary of coefficients for variables
# Dedalus specific string substitutions
bf_slope= bf.bf_slope
bfl_edge= bf.bfl_edge
bfr_edge= bf.bfr_edge
window  = bf.window
ramp    = bf.ramp
fu      = bf.fu
fw      = bf.fw
fb      = bf.fb
fp      = bf.fp

###############################################################################
# Cleaning up the _modules-physics directory tree
for some_dir in os.scandir(p_module_dir):
    # Iterate through subdirectories in _modules-physics
    if some_dir.is_dir():
        dir=some_dir.name
        # If the directory isn't __pycache__, then delete it
        if dir!='__pycache__':
            dir_path = p_module_dir + dir
            rmtree(dir_path, ignore_errors=True)
