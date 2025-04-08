############################################################################################
# File Name: control_line_circle1.py
# Description: This file primarily contains the construction code for the ControlLineCircle1.
############################################################################################
import gdspy
import math
import numpy as np
from addict import Dict
import toolbox
from base.library_base import LibraryBase

class ControlLineCircle1(LibraryBase):
    """
    ControlLineCircle1 class for creating circular control line 1 structures.

    Attributes:
        default_options: Dict, containing default parameters for the circular control line 1.
    """
    default_options = Dict(
        # Framework
        name="charge_line0",
        type="ControlLineCircle1",
        chip="chip0",
        path=[[0, 0],[0, 100]],
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
        Initializes the ControlLineCircle1 class.

        Input:
            options: Dict, user-defined parameters for the circular control line 1.

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
        Draws the geometric shape of the ControlLineCircle1 and adds it to the GDS cell.

        Output:
            None.
        """
        self.lib = gdspy.GdsLibrary()
        gdspy.library.use_current_library = False

        pos = self.path

        corner_radius = self.corner_radius

        self.cell_extract = self.lib.new_cell(self.name + "_extract")
        self.cell_subtract = self.lib.new_cell(self.name + "_subtract")

        control_L_out = gdspy.FlexPath(pos, self.width + self.gap * 2,
                                        corners="circular bend", bend_radius=corner_radius).to_polygonset()
        circle = gdspy.Round(pos[-1], self.radius + self.gap, tolerance=0.01)
        self.cell_extract.add(control_L_out)
        self.cell_extract.add(circle)

        control_L_inner = gdspy.FlexPath(pos, self.width,
                                         corners="circular bend", bend_radius=corner_radius).to_polygonset()
        circle = gdspy.Round(pos[-1], self.radius, tolerance=0.01)
        self.cell_subtract.add(control_L_inner)
        self.cell_subtract.add(circle)

        pad = gdspy.boolean(self.cell_extract, self.cell_subtract, "not")
        self.cell = self.lib.new_cell(self.name + "_cell")
        self.cell.add(pad)

        return