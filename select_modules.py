# Module selection for Dedalus experiment
"""
Description:

This file contains the selection of the physics modules for this experiment. Based on the selected modules, this script will move and rename the relevant files before the experiment is executed, if needed.
"""

import numpy as np

###############################################################################
# Select physics modules

# Boundary forcing
bf_module       = 'bf_default'
# Background profile
bp_module       = 'bp_default'

###############################################################################
################    Shouldn't need to edit below here    #####################
###############################################################################
# Imports for preparing physics modules
from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
from shutil import copy2, rmtree
import os
# If this is the root thread, then do all this stuff
if rank==0:
    print('Preparing physics modules')
    print('')
    # Add path to _modules-physics so python knows to look there on imports
    import sys
    p_module_dir = './_modules_physics/'

    # Move the boundary forcing file up one directory level
    bf_path = p_module_dir + 'boundary_forcing/' + bf_module + '.py'
    if os.path.isfile(bf_path):
        copy2(bf_path, p_module_dir + 'boundary_forcing.py')
        print('Using ' + bf_module + '.py')
    # else:
    #     print(bf_module+'.py not found. Was it selected previously?')

    # Move the background profile file up one directory level
    bp_path = p_module_dir + 'background_profile/' + bp_module + '.py'
    if os.path.isfile(bp_path):
        copy2(bp_path, p_module_dir + 'background_profile.py')
        print('Using ' + bp_module + '.py')
    # else:
    #     print(bp_module+'.py not found. Was it selected previously?')

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
