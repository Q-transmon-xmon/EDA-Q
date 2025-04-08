############################################################################################
# File Name: control_line_circle.py
# Description: This file primarily contains the construction code for the ControlLineCircle.
############################################################################################
import gdspy
import math
import numpy as np
from addict import Dict
import toolbox
from base.library_base import LibraryBase

class ControlLineCircle(LibraryBase):
    """
    ControlLineCircle class for creating circular control line structures.

    Attributes:
        default_options: Dict, containing default parameters for the circular control line.
    """
    default_options = Dict(
        # Framework
        name="charge_line0",
        type="ControlLineCircle",
        chip="chip0",
        pos=[[0, 0],[0, 100]],
        # Geometric parameters
        width=15,
        gap=5,
        radius=60,
        pad_width=15,
        pad_height=25,
        distance=50,
        corner_radius=20
    )

    def __init__(self, options: Dict=None):
        """
        Initializes the ControlLineCircle class.

        Input:
            options: Dict, user-defined parameters for the circular control line.

        Output:
            None.
        """
        super().__init__(options)
        return

    def calc_general_ops(self):
        """
        Calculates general operations.

        Output:
            None.
        """
        return

    def draw_gds(self):
        """
        Draws the geometric shape of the ControlLineCircle and adds it to the GDS cell.

        Output:
            None.
        """
        self.lib = gdspy.GdsLibrary()
        gdspy.library.use_current_library = False

        corner_radius = self.corner_radius

        self.cell_extract = self.lib.new_cell(self.name + "_extract")
        self.cell_subtract = self.lib.new_cell(self.name + "_subtract")

        control_L_out = gdspy.FlexPath(self.pos, self.width + self.gap * 2,
                                      corners="circular bend", bend_radius=corner_radius).to_polygonset()
        circle = gdspy.Round(self.pos[-1], self.radius + self.gap, tolerance=0.01)
        self.cell_extract.add(control_L_out)
        self.cell_extract.add(circle)

        control_L_inner = gdspy.FlexPath(self.pos, self.width,
                                         corners="circular bend", bend_radius=corner_radius).to_polygonset()
        circle = gdspy.Round(self.pos[-1], self.radius, tolerance=0.01)
        self.cell_subtract.add(control_L_inner)
        self.cell_subtract.add(circle)

        pad = gdspy.boolean(self.cell_extract, self.cell_subtract, "not")
        self.cell = self.lib.new_cell(self.name + "_cell")
        self.cell.add(pad)

        return