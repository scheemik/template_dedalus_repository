# Equations of motion and boundary conditions
#   Default equations and boundary conditions
"""
Description:

This is the default file of equations of motion and boundary conditions for the Dedalus experiment. This file will be used when there has been no other file specified.
"""

###############################################################################
# Equations of motion (non-linear terms on RHS)
#   Mass conservation equation
eq1_mc      = "dx(u) + wz = 0"
#   Equation of state (in terms of buoyancy)
eq2_es      = "dt(b) - KA*(dx(dx(b)) + dz(bz))" \
                + "= -((N0*BP)**2)*w - (u*dx(b) + w*bz)"
#   Horizontal momentum equation
eq3_hm      = "dt(u) -SL*NU*dx(dx(u)) - NU*dz(uz) + dx(p) + RF*u" \
                + "= - (u*dx(u) + w*uz)"
#   Vertical momentum equation
eq4_vm      = "dt(w) -SL*NU*dx(dx(w)) - NU*dz(wz) + dz(p) + RF*w - b" \
                + "= - (u*dx(w) + w*wz)"
# Required for solving differential equations in Chebyshev dimension
eq5_bz      = "bz - dz(b) = 0"
eq6_uz      = "uz - dz(u) = 0"
eq7_wz      = "wz - dz(w) = 0"

###############################################################################
# Boundary contitions
#	Using Fourier basis for x automatically enforces periodic bc's
#   Left is bottom, right is top for z direction
# Neumann boundary conditions (derivatives) <- usually not used
bc1_uz_top  = "left(uz) = 0"
bc2_uz_bot  = "right(uz) = 0"
# Dirchlet boundary conditions
bc1_u_bot   = "left(u) = 0"             # solid boundary
bc2_u_top   = "right(u) = right(fu)"    # forced at the boundary
# Boundary condition for w redundant in constant mode
bc3_w_bot   = "left(w) = 0"             # solid boundary
bc3_w_cond  = "(nx != 0)"               # redunant in constant mode (nx==0)
bc4_w_top   = "right(w) = right(fw)"    # forced at the boundary
# Buoyancy
bc5_b_bot   = "left(b) = 0"             # solid boundary
bc6_b_top   = "right(b) = right(fb)"    # forced at the boundary
# Sets gauge pressure to zero in the constant mode
#   Required because of above redundancy
bc7_p_bot   = "left(p) = 0"
bc7_p_cond  = "(nx == 0)"
