"""
Creates a gif of a set of png images in the stated directory.

Usage:
    create_gif.py NAME FILENAME FRAMES_PATH

Arguments:
    NAME            name of experiment
    FILENAME        name for gif file
    FRAMES_PATH     path to frames of animation

Script created: 2019/03/19, Mikhail Schee

Last updated: 2019/07/31, Mikhail Schee
"""

"""
Using imageio
https://imageio.readthedocs.io/en/latest/installation.html
install using:
    conda install -c conda-forge imageio
OR
    pip install imageio

Skeleton script from
https://stackoverflow.com/questions/41228209/making-gif-from-images-using-imageio-in-python
"""

import os
import imageio
# For adding arguments when running
from docopt import docopt

gif_file = 'uh_oh.gif'

if __name__ == '__main__':
    arguments = docopt(__doc__)
    NAME = arguments.get('NAME')
    gif_file = arguments.get('FILENAME')
    png_dir = arguments.get('FRAMES_PATH')
    print('Gif saving to', gif_file)

# To import the switchboard
import sys
switch_path = "../" + NAME
sys.path.insert(0, switch_path) # Adds higher directory to python modules path
import switchboard as sbp
frame_duration = 1.0 / sbp.fps

images = []
# need to sort because os.listdir returns a list of arbitrary order
for file_name in sorted(os.listdir(png_dir)):
    if file_name.endswith('.png'):
        file_path = os.path.join(png_dir, file_name)
        images.append(imageio.imread(file_path))
imageio.mimsave(gif_file, images, duration=frame_duration)
