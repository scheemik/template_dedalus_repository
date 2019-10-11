# Parameters and settings for the background density profile
#   Default background profile
"""
Description:

This is the default file for background profile settings for the Dedalus experiment. This file will be used when there has been no other background profile file specified.
"""

import numpy as np
# To import the switchboard
import sys
sys.path.append("..") # Adds higher directory to python modules path
import switchboard as sbp

###############################################################################
# Background profile parameters

# Non-linear system of 3 equations with 6 unknowns, need to specify 3:
# 1. Characteristic stratification (eventually from the background profile)
N_0     = 1.0                   # [rad/s]
# 2. Characteristic wavenumber
k       = 45                    # [m^-1]
# 3. Oscillation frequency
omega   = 0.7071                # [rad s^-1]
# Use the equations given in Cushman-Roisin and Beckers ch 13 for the rest:
# 4. Angle of beam w.r.t. the horizontal (eq 13.6, dispersion relation)
theta   = np.arccos(omega/N_0)  # [rad]
# 5. Horizontal wavenumber = k*cos(\theta)
k_x     = k*omega/N_0           # [m^-1]
# 6. Vertical wavenumber
k_z     = k*np.sin(theta)       # [m^-1]

# Other parameters specified by relations
# Horizontal wavelength
lam_x   = 2*np.pi / k_x         # [m]
# Oscillation period = 2pi / omega
T       = 2*np.pi / omega       # [s]

###############################################################################
# Background profile function

def build_bp_array(z):
    BP_array = z*0.0 + 1.0
    return BP_array
