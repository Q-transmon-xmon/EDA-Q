#########################################################################
# File Name: _generate_graphics.py
# Description: Generates icons for circuit components.
#              Uses the matplotlib library to draw circuit component graphics and save them as PNG and JPG formats.
#########################################################################

import os
from copy import deepcopy
from core import string_to_component
from _constants import *
from plotting_settings import *
from plotting_settings import plotting_parameters_GUI
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# Define the directory to save icons
png_directory = os.path.join(os.path.dirname(__file__), ".graphics")
try:
    os.mkdir(png_directory)
except FileExistsError:
    pass
# Set the resolution of the icons
dpi = 300


class DummyCircuit(object):
    def __init__(self):
        self._pp = plotting_parameters_GUI


def generate_icon(comp, hover=False, selected=False):
    """
    Generate an icon for a circuit component.

    Input:
        comp: Circuit component object.
        hover: Boolean, indicating whether the component is in hover state.
        selected: Boolean, indicating whether the component is selected.

    Output:
        None
    """
    pp = deepcopy(plotting_parameters_GUI)
    comp._node_minus_plot = '0,0'
    comp._node_plus_plot = '1,0'
    comp._set_plot_coordinates()

    comp._circuit = DummyCircuit()
    xs, ys, line_type = comp._draw()

    fig = plt.figure(figsize=(1, 0.5))
    ax = fig.add_subplot(111)
    ax.set_axis_off()
    plt.margins(x=0., y=0.)
    ax.set_ylim(-0.25, 0.25)
    ax.set_xlim(0., 1.)
    plt.subplots_adjust(left=0., right=1., top=1., bottom=0.)

    rect_args = pp['rect_args']
    rect_kwargs = pp['rect_kwargs']

    if hover and selected:
        pp['W']['lw'] += pp['hover_increment']
        pp['C']['lw'] += pp['hover_increment']
        pp['L']['lw'] += pp['hover_increment']
        pp['R']['lw'] += pp['hover_increment']
        pp['J']['lw'] += pp['hover_increment']
        state_string = '_hover_selected'
        ax.add_patch(Rectangle(*rect_args, edgecolor=blue, **rect_kwargs))
    elif hover:
        pp['W']['lw'] += pp['hover_increment']
        pp['C']['lw'] += pp['hover_increment']
        pp['L']['lw'] += pp['hover_increment']
        pp['R']['lw'] += pp['hover_increment']
        pp['J']['lw'] += pp['hover_increment']
        state_string = '_hover'
    elif selected:
        state_string = '_selected'
        ax.add_patch(
            Rectangle(*rect_args, edgecolor=light_blue, **rect_kwargs))
    else:
        state_string = ''

    for i in range(len(xs)):
        ax.plot(xs[i], ys[i], color=pp["color"], lw=pp[line_type[i]]['lw'])

    fig.savefig(
        os.path.join(png_directory,
                     comp.__class__.__name__ + state_string + '.png'),
        transparent=True,
        dpi=dpi)
    fig.savefig(
        os.path.join(png_directory,
                     comp.__class__.__name__ + state_string + '.jpg'),
        transparent=True,
        dpi=dpi)
    plt.close()


# Generate different icons for each type of circuit component
for el in ['R', 'C', 'L', 'J', 'G']:
    generate_icon(string_to_component(el, None, None, ''))
    generate_icon(string_to_component(el, None, None, ''), hover=True)
    generate_icon(string_to_component(el, None, None, ''), selected=True)
    generate_icon(
        string_to_component(el, None, None, ''), hover=True, selected=True)