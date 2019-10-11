import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from dedalus.extras import plot_tools

def test_plot(vert, hori, plt_title, x_label, y_label, y_lims):
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

z_b = -2*np.pi
z_t = 0.0

z = np.linspace(z_b, z_t, 50)
a = np.sin(z)

fig = test_plot(z, a, 'title', 'a', 'z', [z_b, z_t])
plt.show()
