############################################################################################
# File Name: indium_bump.py
# Description: This file primarily contains the code for constructing Indium Bump.
############################################################################################

import gdspy
import copy
from addict import Dict
import math as mt
from base.library_base import LibraryBase


class IndiumBump(LibraryBase):
    default_options = Dict(
        # Framework
        name="In0",
        type="IndiumBump",
        chip="chip0",
        outline=[],
        # Geometric parameters
        center_pos=(0, 0),
        radius=10
    )

    def __init__(self, options: Dict = None):
        """
        Initializes an instance of the IndiumBump class.

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
        Draws the geometric shape of the Indium Bump and adds it to the GDS cell.
        """
        # Interface
        name = self.name
        type = self.type
        center_pos = copy.deepcopy(self.center_pos)
        radius = self.radius

        # Drawing
        self.lib = gdspy.GdsLibrary()
        gdspy.library.use_current_library = False
        self.cell = self.lib.new_cell(self.name + "_cell")

        # Add the circle to the cell
        self.cell.add(gdspy.Round(center=center_pos, radius=radius))