# Parameters and settings for the Rayleigh friction profile
#   Default Rayleigh friction profile
"""
Description:

This is the default file for Rayleigh friction settings for the Dedalus experiment. This file will be used when there has been no other Rayleigh friction file specified.

For a description of Rayleigh friction, see Jablonowski and Williamson 2011 section 13.4.5.1
"""

import numpy as np
# To import vertical profile helper functions
import sys
sys.path.append("../") # Adds higher directory to python modules path
import vert_profile_functs as vpf
sys.path.append("../switchboard")
#import switchboard as sbp

###############################################################################
# Rayleigh friction parameters

# Top boundary of Rayleigh friction
z_rf_top        = -0.5#sbp.z_sim_f               # [m]
# Thickness of Rayleigh friction layer
rf_thickness    = 0.197#sbp.lambda_z              # [m]
# Bottom boundary of Rayleigh friction layer
z_rf_bot        = z_rf_top - rf_thickness   # [m]
# Slope of Rayleigh friction layer ramp
slope           = 20.0                      # []
# Maximum coefficient ramped to at end of Rayleigh friction
max_coeff       = 0.6                      # []

###############################################################################
# Rayleigh friction function

def bottom_rf(z, z_rf_bot, z_rf_top, slope, max_coeff):
    # initialize array of values to be returned
    values = 0*z
    # Find height of the layer
    H = abs(z_rf_top - z_rf_bot)
    # Find 1/2 down the layer
    sp_c = z_rf_top - H/2.0
    # Add upper stratification
    values += vpf.tanh_(z, max_coeff, -slope, sp_c)
    return values

# For no Rayleigh friction, C_rf needs to be zero everywhere
def build_no_rf_array(z):
    RF_array = z*0.0
    return RF_array

def build_rf_array(z):
    RF_array = bottom_rf(z, z_rf_bot, z_rf_top, slope, max_coeff)
    return RF_array
