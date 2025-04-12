###############################################################################################
# File Name: control_line_width_diff1.py
# Description: This file primarily contains the construction code for the ControlLineWidthDiff1.
############################################################################################

import gdspy
import math
import copy
import numpy as np
from addict import Dict
from base.library_base import LibraryBase


class ControlLineWidthDiff1(LibraryBase):
    """
    ControlLineWidthDiff1 class.

    Contains the construction and drawing functions for control lines with different widths.
    """
    default_options = Dict(
        # Framework
        name="ControlLineWidthDiff0",
        type="ControlLineWidthDiff",
        chip="chip0",
        outline=[],
        # Geometric parameters
        path=[(0, 0), (500, 0), (500, -1000), (1000, -1000), (1000, 0), (1000, 1000)],
        width=[15, 10],
        gap=[5, 4],
        buffer_length=100,
        corner_radius=20
    )

    def __init__(self, options=Dict()):
        """
        Initializes the ControlLineWidthDiff1 class.

        Input:
            options: Dictionary, containing parameters for constructing the control line with different widths.
        """
        super().__init__(options)
        return

    def calc_general_ops(self):
        """
        Calculates general operations.

        Needs to calculate the following parameters:
        readout_pins
        control_pins
        coupling_pins
        outline
        """
        return

    def draw_gds(self):
        """
        Draws the GDS file.

        Draws control lines with different widths and adds buffers.
        """
        ################################ gdspy variables ################################
        gdspy.library.use_current_library = False
        self.lib = gdspy.GdsLibrary()
        self.cell = self.lib.new_cell(self.name)

        ################################ Interface ################################
        # The purpose of the interface is to facilitate subsequent user parameter updates. 
        # Only the interface needs to be updated, and the code below the interface does not need to be changed.
        # Framework
        pos = self.options.path
        width = self.options.width
        gap = self.options.gap
        buffer_length = self.options.buffer_length
        corner_radius = self.options.corner_radius

        ################################ Parameter Conversion ################################
        # This module exists to reconcile the contradiction between user convenience and developer convenience.
        # It can convert user-friendly parameter sets into developer-friendly parameter sets.

        ################################ Drawing ##################################
        control_L_out = gdspy.FlexPath(pos[:-1], width[0] + gap[0] * 2, corners="circular bend",
                                       bend_radius=corner_radius).to_polygonset()
        buffer_L_out = gdspy.Path(width[0] + gap[0] * 2, pos[-2])
        buffer_L_out.segment(buffer_length, direction=np.arctan2(pos[-1][1] - pos[-2][1], pos[-1][0] - pos[-2][0]),
                             final_width=(width[1] + gap[1] * 2))
        buffer_L_out.segment(
            length=(math.sqrt((pos[-1][0] - pos[-2][0]) ** 2 + (pos[-1][1] - pos[-2][1]) ** 2) - buffer_length),
            direction=np.arctan2(pos[-1][1] - pos[-2][1], pos[-1][0] - pos[-2][0]))

        control_L_out = gdspy.boolean(control_L_out, buffer_L_out, 'or')

        control_L_in = gdspy.FlexPath(pos[:-1], width[0], corners="circular bend",
                                      bend_radius=corner_radius).to_polygonset()
        buffer_L_in = gdspy.Path(width[0], pos[-2])
        buffer_L_in.segment(buffer_length, direction=np.arctan2(pos[-1][1] - pos[-2][1], pos[-1][0] - pos[-2][0]),
                            final_width=width[1])
        buffer_L_in.segment(length=(
                    math.sqrt((pos[-1][0] - pos[-2][0]) ** 2 + (pos[-1][1] - pos[-2][1]) ** 2) - buffer_length - gap[
                1]), direction=np.arctan2(pos[-1][1] - pos[-2][1], pos[-1][0] - pos[-2][0]))

        control_L_in = gdspy.boolean(control_L_in, buffer_L_in, 'or')

        control_L = gdspy.boolean(control_L_out, control_L_in, 'not')

        # Add your code
        self.cell.add(control_L)
        return