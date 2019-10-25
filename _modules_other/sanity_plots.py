"""
A script to plot the vertical profiles (if used) and boundary forcing before executing the script in order to do a sanity check.
Needs to be run from the experiment directory

Usage:
    sanity_plots.py NAME RUN

Options:
    NAME	            # -n, Name of experiment
    RUN                 # Denotation of specific run of experiment (usually a datetime)

"""

import sys
import numpy as np
# For adding arguments when running
from docopt import docopt
# For plotting
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.gridspec as gridspec

###############################################################################

# Read in parameters from docopt
if __name__ == '__main__':
    arguments = docopt(__doc__)
    NAME = str(arguments['NAME'])
    RUN  = str(arguments['RUN'])

###############################################################################
# Fetch parameters from switchboard file

# To import the switchboard
import sys
switch_path = "../" + NAME
sys.path.insert(0, switch_path) # Adds higher directory to python modules path
import switchboard as sbp

# Grid resolution
nx      = int(sbp.n_x)
nz      = int(sbp.n_z)
# Domain ranges
x_l     = float(sbp.x_sim_0)
x_r     = float(sbp.x_sim_f)
z_b     = float(sbp.z_sim_f)
z_t     = float(sbp.z_sim_0)
Lx      = float(sbp.L_x)
Lz      = float(sbp.L_z) # including any absorbtion layers
# Domain display parameters
Lx_dis  = float(sbp.L_x_dis)
Lz_dis  = float(sbp.L_z_dis)
abs_div = float(sbp.abs_div)

# Construct arrays for x and z domains
x = np.linspace(x_l, x_r, num=nx)
z = np.linspace(z_b, z_t, num=nz)

# Get plotting parameters from switchboard
buffer = sbp.buffer
extra_buffer = sbp.extra_buffer
dis_ratio = sbp.vp_dis_ratio
ylims = [z_b, z_t]

# Set up multifigure plot
rows = 3
columns = 3
fig_len = 13
fig_wid = 13#columns*0.3*fig_len - 1
fig = plt.figure(figsize=(fig_wid, fig_len))
gridspec.GridSpec(rows, columns)
ax = []
# Change the size of the text overall
font = {'size' : sbp.font_size}
plt.rc('font', **font)

p_module_dir = './_modules_physics/'
o_module_dir = './_modules_other/'

sys.path.insert(0, o_module_dir)
import plot_slices as ps
bp_dict, sl_dict, rf_dict = ps.build_vp_dicts()

def set_vp_labels(axes, vp_dict):
    axes.set_title(vp_dict['vp_name'])
    axes.set_xlabel(vp_dict['vp_xlabel'])
    axes.set_ylabel(r'$z$ (m)')

###############################################################################
# Background Density Profile

# Need to add the path before every import
sys.path.insert(0, p_module_dir)
import background_profile as bp
# The background profile generator function
build_bp_array = bp.build_bp_array
bp_array = build_bp_array(z)
# Plotting
ax.append( plt.subplot2grid((rows, columns), (0,0), rowspan=2, fig=fig))
#ax.append( fig.add_subplot(rows,columns,1))
ax[0] = ps.make_vp_plot(ax[0], bp_array, z, sbp.buffer, sbp.extra_buffer, ylims, sbp.vp_dis_ratio, sbp.abs_div)
set_vp_labels(ax[0], bp_dict)

###############################################################################
# Sponge Layer Profile

# Need to add the path before every import
sys.path.insert(0, p_module_dir)
import sponge_layer as sl
# The background profile generator function
build_sl_array = sl.build_sl_array
sl_array = build_sl_array(z)
# Plotting
ax.append( plt.subplot2grid((rows, columns), (0,1), rowspan=2, fig=fig))
#ax.append( fig.add_subplot(rows,columns,2))
ax[1] = ps.make_vp_plot(ax[1], sl_array, z, sbp.buffer, sbp.extra_buffer, ylims, sbp.vp_dis_ratio, sbp.abs_div)
set_vp_labels(ax[1], sl_dict)

###############################################################################
# Sponge Layer Profile

# Need to add the path before every import
sys.path.insert(0, p_module_dir)
import rayleigh_friction as rf
# The background profile generator function
build_rf_array = rf.build_rf_array
rf_array = build_rf_array(z)
# Plotting
ax.append( plt.subplot2grid((rows, columns), (0,2), rowspan=2, fig=fig))
#ax.append( fig.add_subplot(rows,columns,3))
ax[2] = ps.make_vp_plot(ax[2], rf_array, z, sbp.buffer, sbp.extra_buffer, ylims, sbp.vp_dis_ratio, sbp.abs_div)
set_vp_labels(ax[2], rf_dict)

###############################################################################

# Need to add the path before every import
sys.path.insert(0, p_module_dir)
import boundary_forcing as bf
build_win_array = bf.build_win_array
window_array = build_win_array(x)
# Plotting
ax.append( plt.subplot2grid((rows, columns), (2,0), colspan=columns, fig=fig))
ax[3].plot(x, window_array)
ax[3].set_title('Boundary forcing window')
ax[3].set_xlabel(r'$x$ (m)')
ax[3].set_ylabel('Window coefficient')

# Characteristic stratification [rad/s]
N0     = float(sbp.N_0)
# Wavenumber
k      = float(sbp.k)
# Forcing oscillation frequency
omega  = float(sbp.omega)
# Angle of beam w.r.t. the horizontal
theta  = float(sbp.theta)
# Oscillation period = 2pi / omega
T      = float(sbp.T)
# Forcing amplitude modifier
A      = float(sbp.A)
# Horizontal wavelength
lam_x  = sbp.lam_x

fig.suptitle(NAME)
fig.savefig('outputs/' + RUN + '_sanity_plots.png', dpi=sbp.dpi)
