############################################################################################
# File Name: transmission_path_close.py
# Description: This file primarily contains the code for constructing transmission lines.
############################################################################################
import gdspy
import math, copy
import numpy as np
from addict import Dict
from base.library_base import LibraryBase

class TransmissionPathClose(LibraryBase):
    """
    TransmissionPathClose class for creating transmission line structures.

    Attributes:
        default_options: Dict, containing default transmission line parameters.
    """
    default_options = Dict(
        # Framework
        name="transmission1",
        type="TransmissionPathClose",
        chip="chip0",
        outline=[],
        # Geometric parameters
        pos=[(0, 0), (500, 0)],
        width=15,
        gap=5,
        corner_radius=20
    )

    def __init__(self, options: Dict=None):
        """
        Initializes the TransmissionPathClose class.

        Input:
            options: Dict, user-defined transmission line parameters.

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
        Draws the geometric shape of TransmissionPathClose and adds it to the GDS cell.

        Output:
            None.
        """
        name = self.name
        type = self.type
        chip = self.chip
        outline = copy.deepcopy(self.outline)
        pos = copy.deepcopy(self.pos)
        width = self.width
        gap = self.gap
        corner_radius = self.corner_radius
        # Coordinates are filled in from small to large
        pos_inner = [(pos[0][0], pos[0][1] + gap), (pos[1][0], pos[1][1] - gap)]

        self.lib = gdspy.GdsLibrary()
        gdspy.library.use_current_library = False
        self.cell_subtract = self.lib.new_cell(self.name + "_subtract")

        transmission_L_inner = gdspy.FlexPath(pos_inner, width, corners="circular bend", bend_radius=corner_radius).to_polygonset()
        self.cell_subtract.add(transmission_L_inner)

        self.cell_extract = self.lib.new_cell(name + "_extract")
        control_L_out = gdspy.FlexPath(pos, width + gap * 2, corners="circular bend", bend_radius=corner_radius).to_polygonset()
        self.cell_extract.add(control_L_out)

        pad = gdspy.boolean(self.cell_extract, self.cell_subtract, "not")
        self.cell = self.lib.new_cell(name + "_cell")
        self.cell.add(pad)
        return