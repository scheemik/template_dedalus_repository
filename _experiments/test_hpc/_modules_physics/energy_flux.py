# Parameters and settings for measuring energy flux
#   Default energy flux
"""
Description:

This is the default file for the settings of measuring energy flux for the Dedalus experiment. This file will be used when there has been no other energy flux file specified.
"""

import numpy as np
# To import the switchboard
import sys
sys.path.append("..") # Adds higher directory to python modules path
import switchboard as sbp

###############################################################################
# Energy flux parameters

# Define all energy flux snapshots in an array of dictionaries
ef_snap_dicts = [
           {'take_ef_snaps':   sbp.take_ef_comp,
            'ef_task':         "integ(0.5*(w*u**2 + w**3), 'x')",
            'ef_task_name':    'ef_advec'},

           {'take_ef_snaps':   sbp.take_ef_comp,
            'ef_task':         "integ(p*w, 'x')",
            'ef_task_name':    'ef_press'},

           {'take_ef_snaps':   sbp.take_ef_comp,
            'ef_task':         "integ(-NU*(u*uz + w*wz), 'x')",
            'ef_task_name':    'ef_visc'}
            ]
# Add up the tasks of the components for the total task
ef_total_task = ef_snap_dicts[0]['ef_task'] + "+" + \
                ef_snap_dicts[1]['ef_task'] + "+" + \
                ef_snap_dicts[2]['ef_task']
ef_total = {'take_ef_snaps':   sbp.take_ef_snaps,
            'ef_task':         ef_total_task,
            'ef_task_name':    'ef'}
# Append ef_total dictionary to list of dictionaries
ef_snap_dicts.append(ef_total)
