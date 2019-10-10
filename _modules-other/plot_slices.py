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

def main(filename, start, count, output):
    """Save plot of specified tasks for given range of analysis writes."""

    # To import the switchboard
    import sys
    switch_path = "../" + NAME
    sys.path.insert(0, switch_path) # Adds higher directory to python modules path
    import switchboard as sbp

    # Get relevant parameters from switchboard
    L_x_dis = sbp.L_x_dis
    L_z_dis = sbp.L_z_dis
    # Calculate aspect ratio
    AR = L_x_dis / L_z_dis

    # Change the size of the text overall
    font = {'size' : 12}
    plt.rc('font', **font)
    # Plot settings
    tasks = ['b', 'p', 'u', 'w']
    scale = 2.5
    dpi = 100
    title_func = lambda sim_time: 't = {:.3f}'.format(sim_time)
    savename_func = lambda write: 'write_{:06}.png'.format(write)
    # Layout
    nrows, ncols = 2, 2
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
                # Build subfigure axes
                i, j = divmod(n, ncols)
                axes = mfig.add_axes(i, j, [0, 0, 1, 1])
                # Call 3D plotting helper, slicing in time
                dset = file['tasks'][task]
                plot_tools.plot_bot_3d(dset, 0, index, axes=axes, title=task, even_scale=True)
            # Add time title
            title = title_func(file['scales/sim_time'][index])
            title_height = 1 - 0.5 * mfig.margin.top / mfig.fig.y
            fig.suptitle(title, x=0.48, y=title_height, ha='left')
            # Save figure
            savename = savename_func(file['scales/write_number'][index])
            savepath = output.joinpath(savename)
            fig.savefig(str(savepath), dpi=dpi)
            fig.clear()
    plt.close(fig)


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
