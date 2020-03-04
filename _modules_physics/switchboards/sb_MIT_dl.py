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
n_x = 512                   # []
n_z = 512                   # []
# Dealias factor
dealias = 3/2               # []
# Stopping conditions for the simulation
stop_n_periods = 15          # [] oscillation periods
stop_wall_time = 180        # [minutes]
stop_iteration = np.inf     # []
stop_sim_time  = 3          # [s] to be calculated from stop_n_periods later

# If True, the program will use stop_sim_time, if False, stop_n_periods*T
use_stop_sim_time = False
# Initial time step size
dt = 0.125
# Determine whether adaptive time stepping is on or off
adapt_dt = False             # {T/F}

###############################################################################
# Domain parameters

# Dimensions of simulated domain
L_x = 1.5                   # [m]
L_z = 1.0                   # [m] Does not include absorbing bottom layer

# Constraints on display domain
#   If True, display domain will be exactly the simulated domain
#   If False, display only the specified domain
dis_eq_sim = False
# Dimensions of displayed domain if dis_eq_sim==False
L_x_dis = 0.5               # [m] (should be leq simulated domain)
L_z_dis = 0.5               # [m] (should be leq simulated domain)
# Display buffer if dis_eq_sim==False (measured from top left corner)
Dis_buff_x = 0.3            # [m]
Dis_buff_z = 0.3            # [m]
# Upper left corner of display domain is always (0, 0)
abs_div = -L_z              # [m] The dividing line of the absorbing layer

###############################################################################
# ON / OFF Switches for Modules / Physics

# Terms in equations of motion
viscous_term            = True
pressure_term           = True
advection_term          = True
buoyancy_term           = True
diffusivity_term        = True
rotation_term           = False

# Diffusion / dissipation of reflections
use_sponge              = False
use_rayleigh_friction   = True

# Measurements
take_ef_comp  = True # Energy flux terms recorded separately
# Records snapshots of total vertical energy flux
take_ef_snaps = True # Total energy flux recorded

###############################################################################
# Physical parameters
nu          = 1.0E-6        # [m^2/s] Viscosity (momentum diffusivity)
kappa       = 1.4E-7        # [m^2/s] Thermal diffusivity
Prandtl     = nu / kappa    # [] Prandtl number, about 7.0 for water at 20 C
Rayleigh    = 1e6
g           = 9.81          # [m/s^2] Acceleration due to gravity

###############################################################################
# Plotting parameters

# Dark mode on or off (ideally would make plots that have white text and alpha background)
dark_mode = False
cmap = 'RdBu_r'
import colorcet as cc
cmap = cc.CET_D4

# Presentation mode on or off (increases size of fonts and contrast of colors)
presenting = False

# Vertical profile and Wave field animation
# If True, plots b, p, u, and w. If false, plots profile and w
plot_all_variables = False
# If True, the sponge layer plot will be plotted to the right of the animation
plot_sponge        = False
# If True, the Rayleigh friction plot will replace background profile
plot_rf            = False
plot_twin          = False

# Auxiliary snapshot plots
plot_ef_total = True
plot_ef_comps = False

# Miscellaneous
# Fudge factor to make plots look nicer
buffer = 0.04
# Extra buffer for a constant vertical profile
extra_buffer = 0.5
# Display ratio of vertical profile plot
vp_dis_ratio = 2.0 # Profile plot gets skinnier as this goes up
# The number of ticks on the top color bar
n_clrbar_ticks = 3
# Overall font size of plots
font_size   = 15
scale       = 2.5
dpi         = 100

# Animation parameters
fps = 20

###############################################################################
# Snapshot parameters
snapshots_dir   = 'snapshots'
snap_dt         = 0.25
snap_max_writes = 25

# Background profile snapshot parameters
take_bp_snaps   = True
# Sponge layer snapshot parameters
take_sl_snaps   = True
# Rayleigh friction snapshot parameters
take_rf_snaps   = True

# Define all vertical profile snapshots in an array of dictionaries
#   Meant for profiles that are constant in time
take_vp_snaps = True
vp_snap_dir = 'vp_snapshots'
vp_snap_dicts = [
           {'take_vp_snaps':   take_bp_snaps,
            'vp_task':         "N0*BP",
            'vp_task_name':    'bp'},

           {'take_vp_snaps':   take_sl_snaps,
            'vp_task':         "SL",
            'vp_task_name':    'sl'},

           {'take_vp_snaps':   take_rf_snaps,
            'vp_task':         "RF",
            'vp_task_name':    'rf'}
            ]

# Auxiliary snapshot directory
aux_snap_dir = 'aux_snapshots'

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

###############################################################################
################    Shouldn't need to edit below here    #####################
###############################################################################

###############################################################################
# Calculating domain parameters

# Constraints on display domain
#   If True, display domain will be exactly the simulated domain
#   If False, display only the specified domain
if dis_eq_sim==True:
    # Dimensions of displayed domain
    L_x_dis = L_x               # [m]
    L_z_dis = L_z               # [m]
    # Display buffer (measured from top left corner)
    Dis_buff_x = 0.0            # [m]
    Dis_buff_z = 0.0            # [m]
# Upper left corner of display domain is always (0, 0)
x_0     = 0.0
z_0     = 0.0
# Therefore, the upper left corner of the simulated domain is
x_sim_0 = x_0 - Dis_buff_x
z_sim_0 = z_0 + Dis_buff_z
# Lower right corner of simulated domain
x_sim_f = x_sim_0 + L_x
z_sim_f = z_sim_0 - L_z

###############################################################################
# Imports for preparing physics modules
from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
from shutil import copy2, rmtree
import os
import sys
p_module_dir = './_modules_physics/'

###############################################################################
# Boundary forcing

# Need to add the path before every import
sys.path.insert(0, p_module_dir)
import boundary_forcing as bf
# See boundary forcing file for the meaning of these variables
N_0     = bf.N_0        # [rad s^-1]
k       = bf.k          # [m^-1]
omega   = bf.omega      # [rad s^-1]
theta   = bf.theta      # [rad]
k_x     = bf.k_x        # [m^-1]
k_z     = bf.k_z        # [m^-1]
lam_x   = bf.lam_x      # [m]
lam_z   = bf.lam_z      # [m]
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

# Calculate stop_sim_time if use_stop_sim_time=False
if use_stop_sim_time == False:
    stop_sim_time = stop_n_periods * T
# Set restart simulation parameters
restart_add_time = stop_sim_time
restart_file  = 'restart.h5'

###############################################################################
# Equations of Motion and Boundary Conditions

# Need to add the path before every import
sys.path.insert(0, p_module_dir)
import eqs_and_bcs as eq
# Equations of motion
eq1_mc      = eq.eq1_mc
eq2_es      = eq.eq2_es
eq3_hm      = eq.eq3_hm
eq4_vm      = eq.eq4_vm
eq5_bz      = eq.eq5_bz
eq6_uz      = eq.eq6_uz
eq7_wz      = eq.eq7_wz
# Boundary contitions
bc1         = eq.bc1_u_bot
bc2         = eq.bc2_u_top
bc3         = eq.bc3_w_bot
bc3_cond    = eq.bc3_w_cond
bc4         = eq.bc4_w_top
bc5         = eq.bc5_b_bot
bc6         = eq.bc6_b_top
bc7         = eq.bc7_p_bot
bc7_cond    = eq.bc7_p_cond

###############################################################################
# Background Density Profile

# Need to add the path before every import
sys.path.insert(0, p_module_dir)
import background_profile as bp
# The background profile generator function
build_bp_array = bp.build_bp_array

###############################################################################
# Sponge Layer Profile

# Need to add the path before every import
sys.path.insert(0, p_module_dir)
import sponge_layer as sl
if take_sl_snaps==False:
    plot_sponge = False
if use_sponge==True:
    # The sponge layer profile generator function
    build_sl_array = sl.build_sl_array
    # Redefine the vertical domain length if need be
    L_z = L_z + sl.sl_thickness
    z_sim_f = sl.z_sl_bot
    if dis_eq_sim==True:
        L_z_dis = L_z
else:
    build_sl_array = sl.build_no_sl_array

###############################################################################
# Rayleigh Friction Profile

# Need to add the path before every import
sys.path.insert(0, p_module_dir)
import rayleigh_friction as rf
if take_rf_snaps==False:
    plot_rf = False
if use_rayleigh_friction==True:
    # The sponge layer profile generator function
    build_rf_array = rf.build_rf_array
    # Redefine the vertical domain length if need be
    if use_sponge==False:
        L_z = L_z + rf.rf_thickness
        z_sim_f = rf.z_rf_bot
        if dis_eq_sim==True:
            L_z_dis = L_z
else:
    build_rf_array = rf.build_no_rf_array

###############################################################################
# Energy Flux Measurements

# Need to add the path before every import
sys.path.insert(0, p_module_dir)
import energy_flux as ef
if take_ef_snaps==False and take_ef_comp==False:
    plot_ef = False
ef_snap_dicts = ef.ef_snap_dicts

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
