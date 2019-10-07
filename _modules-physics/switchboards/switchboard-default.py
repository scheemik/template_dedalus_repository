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
stop_sim_time  = 15         # [s] to be calculated from stop_n_periods later
# Time step size
dt = 0.125
# Determine whether adaptive time stepping is on or off
adapt_dt = False            # {T/F}
# Restart simulation parameters
restart_add_time = stop_sim_time
restart_file  = 'restart.h5'

###############################################################################
# Domain parameters

# Dimensions of simulated domain
L_x = 4.0                   # [m]
L_z = 1.0                   # [m]

# Dimensions of displayed domain (should be leq simulated domain)
L_xdis = 1.0                # [m]
L_zdis = 1.0                # [m]
# Display buffer (measured from top left corner)
L_xdis_buff = 0.0           # [m]
L_zdis_buff = 0.0           # [m]

###############################################################################
# Physical parameters
Prandtl = 1.
Rayleigh = 1e6

###############################################################################
# Snapshot parameters
snapshots_dir = 'snapshots'
snap_dt = 0.25
snap_max_writes = 50

###############################################################################
# CFL parameters
CFL_cadence = 10
CFL_safety  = 1
CFL_max_change = 1.5
CFL_min_change = 0.5
CFL_max_dt = 0.125
CFL_threshold = 0.05

###############################################################################
# Flow properties
flow_cadence = 10
flow_property = "sqrt(u*u + w*w) / R"
flow_name = 'Re'
