# Parameters and settings for boundary forcing
#   Default boundary forcing
"""
Description:

This is the default file for boundary forcing settings for the Dedalus experiment. This file will be used when there has been no other boundary forcing file specified.
"""

import numpy as np

###############################################################################
# Boundary forcing parameters

# Characteristic stratification
N_0 = 1.0 # [rad/s]
# Horizontal wavelength (3 across top boundary)
lam_x = 0.5 / 3.0 #L_x / 3.0
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
"""
###############################################################################
# Polarization relation from Cushman-Roisin and Beckers eq (13.7)
#   (signs implemented later)
PolRel = {'u': sbp.A*(sbp.g*sbp.omega*sbp.k_z)/(sbp.N_0**2*sbp.k_x),
          'w': sbp.A*(sbp.g*sbp.omega)/(sbp.N_0**2),
          'b': sbp.A*sbp.g}

###############################################################################
# Parameters for boundary forcing
problem.parameters['kx'] = sbp.k_x
problem.parameters['kz'] = sbp.k_z
problem.parameters['omega'] = sbp.omega
problem.parameters['grav'] = sbp.g # can't use 'g' because Dedalus already uses that for grid
problem.parameters['T'] = sbp.T # period of oscillation
problem.parameters['nT'] = sbp.nT # number of periods for the ramp
#problem.parameters['z_top'] = sbp.z_t
problem.substitutions['window'] = "1" # effectively, no window
# Ramp in time
problem.substitutions['ramp'] = "(1/2)*(tanh(4*t/(nT*T) - 2) + 1)"
# Substitutions for boundary forcing (see C-R & B eq 13.7)
problem.substitutions['fu'] = "-BFu*sin(kx*x + kz*z - omega*t)*window*ramp"
problem.substitutions['fw'] = " BFw*sin(kx*x + kz*z - omega*t)*window*ramp"
problem.substitutions['fb'] = "-BFb*cos(kx*x + kz*z - omega*t)*window*ramp"
#problem.substitutions['fp'] = "-BFp*sin(kx*x + kz*z - omega*t)*window*ramp"
"""
