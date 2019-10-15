import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from dedalus.extras import plot_tools

# To import the switchboard
import sys
#switch_path = "../" + NAME
this_path = "~/Documents/Dedalus_Projects/example_projects/template_dedalus_repository/_modules_physics/background_profile/"
that_path = "./_modules_physics/background_profile"
#sys.path.insert(0, this_path) # Adds higher directory to python modules path
sys.path.append(that_path)
import Foran_profile as fp

def dedalus_plot(vert, hori, plt_title, x_label, y_label, y_lims):
    #matplotlib.use('Agg')
    scale = 2.5
    image = plot_tools.Box(1, 1) # aspect ratio of figure
    pad = plot_tools.Frame(0.2, 0.2, 0.15, 0.15)
    margin = plot_tools.Frame(0.3, 0.2, 0.1, 0.1)
    # Create multifigure
    mfig = plot_tools.MultiFigure(1, 1, image, pad, margin, scale)
    fig = mfig.figure
    ax = mfig.add_axes(0, 0, [0, 0, 1, 1])
    #fg, ax = plt.subplots(1,1)
    ax.set_title(plt_title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_ylim(y_lims)
    ax.plot(hori, vert, 'k-')
    plt.grid(True)
    return fig

# Plotting function for sponge layer, background profile, etc.
def test_plot(hori, vert, plt_title, x_label=None, y_label=None, x_lims=None, y_lims=None):
    #with plt.rc_context({'axes.edgecolor':'white', 'text.color':'white', 'axes.labelcolor':'white', 'xtick.color':'white', 'ytick.color':'white', 'figure.facecolor':'black'}):
    fg, ax = plt.subplots(1,1)
    ax.set_title(plt_title)
    if x_label != None:
        ax.set_xlabel(x_label)
    if y_label != None:
        ax.set_ylabel(y_label)
    if x_lims != None:
        ax.set_xlim(x_lims)
    if y_lims != None:
        ax.set_ylim(y_lims)
    ax.plot(hori, vert, 'k-')
    plt.grid(True)
    return fg

z_b = -0.5
z_t =  0.0
n = 1
ml_b = -0.38
ml_t = -0.2
slope = 120
N_1 = 0.95
N_2 = 1.05

z = np.linspace(z_b, z_t, 100)
a = fp.Repro_profile(z, n, ml_b, ml_t, slope, N_1, N_2)

x_lims = [0, 1.5]
y_lims = [z_b, z_t]

plt_title = 'Plot title'
x_label = r'$N$ (s$^{-1}$)'
y_label = r'$z$ (m)'

fg = test_plot(a, z, plt_title, x_label, y_label, x_lims, y_lims)
plt.show()
