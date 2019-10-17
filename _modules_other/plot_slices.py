"""
Plot planes from joint analysis files.

Usage:
    plot_slices.py EXP_NAME <files>... [--output=<dir>]

Options:
    EXP_NAME            # Name of experiment to add switchboard module path
    --output=<dir>      # Output directory [default: ./frames]

"""

import h5py
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.ioff()
from dedalus.extras import plot_tools
# Import modified version of plot bot
from plot_tools_mod import plot_bot_3d_mod

###############################################################################
# Helper functions

# Sets parameters according to the switchboard settings
def flip_the_switches(plot_all_variables, use_sst, T):
    if plot_all_variables:
        tasks = ['b', 'p', 'u', 'w']
        nrows, ncols = 2, 2
    else:
        tasks = ['w']
        nrows, ncols = 1, 2
    if use_sst:
        title_str = r'{:}, $t$ = {:2.3f}'
        time_factor = 1.0
    else:
        title_str = r'{:}, $t/T$ = {:2.3f}'
        time_factor = T
    return tasks, nrows, ncols, title_str, time_factor

# Adds the title to a frame
def add_frame_title(fig, file, index, title_func):
    title = title_func(file['scales/sim_time'][index])
    fig.suptitle(title, fontsize='large')

# Saves figure as a frame
def save_fig_as_frame(fig, file, index, savename_func, output, dpi):
    savename = savename_func(file['scales/write_number'][index])
    savepath = output.joinpath(savename)
    fig.savefig(str(savepath), dpi=dpi)
    fig.clear()

# Plots one frame of one task (b, p, u, or w)
def plot_one_task(n, ncols, mfig, file, task, index, x_lims, y_lims, n_clrbar_ticks):
    # Build subfigure axes
    i, j = divmod(n, ncols)
    axes = mfig.add_axes(i, j, [0, 0, 1, 1])
    # Call 3D plotting helper, slicing in time
    dset = file['tasks'][task]
    plot_bot_3d_mod(dset, 0, index, x_limits=x_lims, y_limits=y_lims, n_cb_ticks=n_clrbar_ticks, axes=axes, title=task, even_scale=True)

# Extracts relevant arrays from a vertical profile snapshot
def extract_vp_snapshot(task_name):
    vp_snap_filepath = 'snapshots/bp_snaps/bp_snaps_s1.h5'
    with h5py.File(vp_snap_filepath, mode='r') as file:
        data = file['tasks'][task_name]
        temp = data[()]
        hori = temp[0][0]
        z_   = file['scales']['z']['1.0']
        vert = z_[()]
    return hori, vert

def plot_bp_on_left(bp_task_name, mfig, ylims=None):
    axes0 = mfig.add_axes(0, 0, [0, 0, 1.3, 1])#, sharey=axes1)
    axes0.set_title('Profile')
    axes0.set_xlabel(r'$N$ (s$^{-1}$)')
    axes0.set_ylabel(r'$z$ (m)')
    hori, vert = extract_vp_snapshot(bp_task_name)
    dis_ratio = 2.0 # Profile plot gets skinnier as this goes up
    buffer    = 0.04
    xleft  = min(hori)
    xright = max(hori)
    if ylims==None:
        ybott  = min(vert)
        ytop   = max(vert)
    else:
        ybott  = ylims[0]
        ytop   = ylims[1]
    # If the profile is constant,
    #   plot the straight line with a slight buffer on both sides
    if (xright-xleft == 0):
        xleft  =  xleft - 0.5 - buffer
        xright =  xright- 0.5 + buffer
    calc_ratio = abs((xright-xleft)/(ybott-ytop))*dis_ratio
    axes0.plot(hori, vert, 'k-')
    axes0.set_ylim([ybott-buffer,   ytop+buffer]) # fudge factor to line up y axes
    axes0.set_xlim([xleft,        xright+buffer])
    # Force display aspect ratio
    axes0.set_aspect(calc_ratio)

###############################################################################
def main(filename, start, count, output):
    """Save plot of specified tasks for given range of analysis writes."""

    # To import the switchboard
    import sys
    switch_path = "../" + NAME
    sys.path.insert(0, switch_path) # Adds higher directory to python modules path
    import switchboard as sbp

    # Get relevant parameters from switchboard used in loop
    plot_all        = sbp.plot_all_variables
    bp_task_name    = sbp.bp_task_name
    n_clrbar_ticks  = sbp.n_clrbar_ticks
    T               = sbp.T
    # Display parameters
    x_f             = sbp.x_0 + sbp.L_x_dis
    z_b             = sbp.z_t - sbp.L_z_dis

    # Calculate aspect ratio
    AR = sbp.L_x_dis / sbp.L_z_dis
    # Set tuples for display boundaries
    x_lims = [sbp.x_0, x_f]
    y_lims = [z_b, sbp.z_t]

    # Change the size of the text overall
    font = {'size' : sbp.font_size}
    plt.rc('font', **font)
    # Set parameters based on switches
    tasks, nrows, ncols, title_str, time_factor = flip_the_switches(plot_all, sbp.use_stop_sim_time, sbp.T)
    # Plot settings
    scale   = sbp.scale
    dpi     = sbp.dpi
    title_func = lambda sim_time: title_str.format(NAME, sim_time/time_factor)
    savename_func = lambda write: 'write_{:06}.png'.format(write)
    # Layout
    image = plot_tools.Box(AR, 1)
    pad = plot_tools.Frame(0.2, 0.2, 0.15, 0.15)
    margin = plot_tools.Frame(0.3, 0.2, 0.1, 0.1)

    # Create multifigure
    mfig = plot_tools.MultiFigure(nrows, ncols, image, pad, margin, scale)
    fig = mfig.figure
    # Plot writes
    with h5py.File(filename, mode='r') as file:
        for index in range(start, start+count):
            for n, task in enumerate(tasks):
                if (plot_all == False):
                    # Plot stratification profile on the left
                    plot_bp_on_left(bp_task_name, mfig, y_lims)
                    # shift n so that animation is on the right side
                    n = 1
                plot_one_task(n, ncols, mfig, file, task, index, x_lims, y_lims, n_clrbar_ticks)
            # Add title to frame
            add_frame_title(fig, file, index, title_func)
            # Save figure
            save_fig_as_frame(fig, file, index, savename_func, output, dpi)
    plt.close(fig)

###############################################################################
if __name__ == "__main__":

    import pathlib
    from docopt import docopt
    from dedalus.tools import logging
    from dedalus.tools import post
    from dedalus.tools.parallel import Sync

    args = docopt(__doc__)

    NAME = str(args['EXP_NAME'])

    output_path = pathlib.Path(args['--output']).absolute()
    # Create output directory if needed
    with Sync() as sync:
        if sync.comm.rank == 0:
            if not output_path.exists():
                output_path.mkdir()
    post.visit_writes(args['<files>'], main, output=output_path)
