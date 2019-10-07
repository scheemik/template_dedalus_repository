# Switchboard for Dedalus experiment
#   Default switchboard
"""
Description:

This is the default switchboard for the Dedalus experiment. This file will be used when there has been no other switchboard specified.
"""

# Stop times for the simulation
sim_period_stop = 10 # oscillation periods, time in seconds calculated below
wall_time_stop = 60 # min

# Determine whether adaptive time stepping is on or off
adapt_dt = False

# Number of points in each dimension
n_x = 256
n_z = 64
