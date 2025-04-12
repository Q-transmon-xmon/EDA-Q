#########################################################################
# File Name: plotting_settings.py
# Description: Defines the plotting settings for QuCAT, including colors, graphical parameters, etc.
#########################################################################

from copy import deepcopy

# Color definitions
gray = "#666666"
light_black = "#1c1c1c"
blue = '#7b9ff9'
light_blue = '#baceff'
lighter_blue = '#cfdbf7'
orange = '#ee8467'

#################################
# Display function parameters
#################################
plotting_parameters_show = {
    "figsize_scaling": 1,
    "color": light_black,
    "x_fig_margin": 1,
    "y_fig_margin": 0.5,
    "C": {
        "gap": 0.2,
        "height": 0.25,
        "lw": 6
    },
    "J": {
        "width": 0.22,
        "lw": 6
    },
    "L": {
        "width": 0.7,
        "height": 0.25,
        "N_points": 150,
        "N_turns": 5,
        "lw": 2
    },
    "R": {
        "width": 0.6,
        "height": 0.25,
        "N_points": 150,
        "N_ridges": 4,
        "lw": 2
    },
    "P": {
        "side_wire_width": 0.25
    },
    "node": {
        "diameter": 12
    },
    "W": {
        "lw": 1
    },
    "label": {
        "fontsize": 10,
        "text_position_horizontal": [0.,-0.22],
        "text_position_vertical": [0.22,0.]
    }
}

#################################
# Normal mode function parameters
#################################
pp = deepcopy(plotting_parameters_show)
pp["y_fig_margin"] = 0.7

scale = 1.5
pp["figsize_scaling"] = scale
pp["C"]["gap"] /= scale
pp["C"]["height"] /= scale
pp["J"]["width"] /= scale
pp["L"]["width"] /= scale
pp["L"]["height"] /= scale
pp["R"]["width"] /= scale
pp["R"]["height"] /= scale
pp["label"] = {
    "fontsize": 10,
    "text_position_horizontal": [0., -pp["C"]["height"] / 2 - 0.07],
    "text_position_vertical": [pp["C"]["height"] / 2 + 0.05, -0.05]
}
pp["normal_mode_label"] = {
    "fontsize": 10,
    "color": blue,
    "y_arrow": pp["C"]["height"] / 2 + 0.08,
    "text_position_horizontal": [0., pp["C"]["height"] / 2 + 0.25],
    "text_position_vertical": [-pp["C"]["height"] / 2 - 0.15, +0.07]
}
pp["normal_mode_arrow"] = {
    "min_width": 0.1,
    "max_width": 0.4,
    "min_lw": 1,
    "max_lw": 3,
    "min_head": 0.05,
    "max_head": 0.071,
    "color": blue
}
plotting_parameters_normal_modes = pp

#######################################
# GUI component plotting parameters
#######################################
plotting_parameters_GUI = {
    "hover_increment": 1.5,
    "rect_args": [(0.1, -0.22), 0.8, 0.44],
    "rect_kwargs": {'linewidth': 2, 'facecolor': 'none'},
    "element_width": 1.,
    "element_height": 1.,
    "margin": 0.,
    "figsize_scaling": 1,
    "color": [0.15, 0.15, 0.15],
    "x_fig_margin": 0.,
    "y_fig_margin": 0.25,
    "C": {
        "gap": 0.2,
        "height": 0.25,
        "lw": 6
    },
    "J": {
        "width": 0.25,
        "lw": 6
    },
    "L": {
        "width": 0.7,
        "height": 0.25,
        "N_points": 150,
        "N_turns": 5,
        "lw": 2
    },
    "R": {
        "width": 0.6,
        "height": 0.25,
        "N_points": 150,
        "N_ridges": 4,
        "lw": 2
    },
    "P": {
        "side_wire_width": 0.25
    },
    "W": {
        "lw": 2
    }
}