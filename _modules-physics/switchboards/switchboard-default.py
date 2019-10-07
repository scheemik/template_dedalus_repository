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
L_xdis = 1.0                # [m]
L_zdis = 1.0                # [m]
# Display buffer (measured from top left corner)
L_xdis_buff = 0.0           # [m]
L_zdis_buff = 0.0           # [m]

###############################################################################
# Physical parameters
nu          = 1.0E-6        # [m^2/s] Viscosity (momentum diffusivity)
kappa       = 1.4E-7        # [m^2/s] Thermal diffusivity
Prandtl     = nu / kappa    # [] Prandtl number, about 7.0 for water at 20 C
Rayleigh    = 1e6
g           = 9.81          # [m/s^2] Acceleration due to gravity

###############################################################################
# Boundary forcing parameters

# Characteristic stratification
N_0 = 1.0 # [rad/s]
# Horizontal wavelength (3 across top boundary)
lam_x = L_x / 3.0
# Oscillation frequency = N_0 * cos(theta), from dispersion relation
omega = 0.7071 # [rad s^-1]
# Angle of beam w.r.t. the horizontal
theta = np.arccos(omega/N_0) # [rad]
# Horizontal wavenumber
k_x    = 2*np.pi/lam_x # [m^-1] k*cos(theta)
# Characteristic wavenumber
k   = k_x*N_0/omega # [m^-1]
# Vertical wavenumber
k_z   = k*np.sin(theta) # [m^-1] k*sin(theta)

# Oscillation period = 2pi / omega
T = 2*np.pi / omega
# Forcing amplitude modifier
A = 2.0e-4
# Forcing amplitude ramp (number of oscillations)
nT = 3.0

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
flow_property = "(kx*u + kz*w)/omega"#"sqrt(u*u + w*w) / R"
flow_name = 'Lin_Criterion'#'Re'
flow_log_message = 'Max linear criterion = {0:f}'#'Max Re = %f'
