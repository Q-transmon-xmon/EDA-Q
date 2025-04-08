############################################################################################
# File Name: finger.py
# Description: This file primarily contains the code for constructing readout cavities.
############################################################################################

import gdspy
import copy
import math
import numpy as np
from addict import Dict
import toolbox
from base.library_base import LibraryBase


class Finger(LibraryBase):
    default_options = Dict(
        # Framework
        name="finger0",
        type="Finger",
        chip="chip0",
        start_pos=(0, 0),
        length=300,
        orientation=0,
        corner_angle=90,
        corner_radius=90,
        width=10,
        gap=6
    )

    def __init__(self, options: Dict = None):
        """
        Initializes an instance of the Finger class.

        Input:
            options: Dict, containing custom option parameters.
        """
        super().__init__(options)
        return

    def calc_general_ops(self):
        """
        Placeholder function for calculating general operations.
        """
        return

    def draw_gds(self):
        """
        Draws the geometric shape of the ReadoutLine and adds it to the GDS cell.
        """
        self.lib = gdspy.GdsLibrary()
        gdspy.library.use_current_library = False
        self.cell = self.lib.new_cell(self.name + "_cell")

        # Interface
        corner_angle = self.corner_angle
        corner_radius = self.corner_radius
        length = self.length
        width = self.width
        gap = self.gap
        orientation = self.orientation
        start_pos = self.start_pos

        # Base shape, starting at (0, 0)
        pos = []
        pos.append((0, 0))
        min_length = self.corner_min_length(corner_angle, corner_radius)
        now_p = (length + min_length, 0)
        pos.append(now_p)
        now_p = (now_p[0] + min_length * math.cos(math.radians(corner_angle)),
                 now_p[1] + min_length * math.sin(math.radians(corner_angle)))
        pos.append(now_p)

        # Drawing
        finger = gdspy.FlexPath(pos, width + gap * 2, corners="circular bend",
                                bend_radius=corner_radius).to_polygonset()
        sub_finger = gdspy.FlexPath(pos, width, corners="circular bend", bend_radius=corner_radius).to_polygonset()
        finger = gdspy.boolean(finger, sub_finger, "not")

        # Translate and rotate
        finger.rotate(math.radians(orientation), (0, 0))
        finger.translate(start_pos[0], start_pos[1])

        # Add to cell
        self.cell.add(finger)

        return

    def corner_min_length(self, corner_angle, corner_radius):
        """
        Calculates the minimum corner length for a given angle and radius.

        Input:
            corner_angle: Float, the angle of the corner.
            corner_radius: Float, the radius of the corner.

        Output:
            Float, the minimum corner length.
        """
        corner_angle = math.radians(corner_angle)
        return abs(corner_radius * math.tan(corner_angle / 2))