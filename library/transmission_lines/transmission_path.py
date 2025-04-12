############################################################################################
# File Name: transmission_path.py
# Description: This file primarily contains the code for constructing transmission lines.
#              Defines the TransmissionPath class, responsible for drawing the geometric shape
#              of transmission lines and setting basic parameters.
############################################################################################

import gdspy
import math, copy
import numpy as np
from addict import Dict
from base.library_base import LibraryBase


class TransmissionPath(LibraryBase):
    # Default option settings
    default_options = Dict(
        # Framework
        name="transmission1",  # Transmission line name
        type="TransmissionPath",  # Transmission line type
        chip="chip0",  # Associated chip
        outline=[],  # Outline
        # Geometric parameters
        pos=[(0, 0), (500, 0)],  # Coordinates of the transmission line positions
        width=10,  # Transmission line width
        gap=6,  # Transmission line gap
        corner_radius=20  # Corner radius
    )

    def __init__(self, options: Dict = None):
        """
        Initializes the TransmissionPath class.

        Input:
            options: Optional dictionary of parameters to override default options.
        """
        super().__init__(options)  # Call the parent class constructor
        return

    def calc_general_ops(self):
        """
        Calculates general operations for the transmission line.
        Currently, this method is empty and can be extended in the future to implement specific functionality.
        """
        return

    def draw_gds(self):
        """
        Draws the geometric shape of the TransmissionLine and adds it to the GDS cell.
        """
        name = self.name
        type = self.type
        chip = self.chip
        outline = copy.deepcopy(self.outline)  # Deep copy the outline
        pos = copy.deepcopy(self.pos)  # Deep copy the position
        width = self.width  # Transmission line width
        gap = self.gap  # Transmission line gap
        corner_radius = self.corner_radius  # Corner radius

        self.lib = gdspy.GdsLibrary()  # Create a GDS library
        gdspy.library.use_current_library = False  # Do not use the current library
        self.cell_subtract = self.lib.new_cell(self.name + "_subtract")  # Create a subtraction cell

        # Create the inner transmission line
        transmission_L_inner = gdspy.FlexPath(pos, width, corners="circular bend",
                                              bend_radius=corner_radius).to_polygonset()
        self.cell_subtract.add(transmission_L_inner)  # Add the inner transmission line to the subtraction cell

        # Create the outer control line
        self.cell_extract = self.lib.new_cell(name + "_extract")
        control_L_out = gdspy.FlexPath(pos, width + gap * 2, corners="circular bend",
                                       bend_radius=corner_radius).to_polygonset()
        self.cell_extract.add(control_L_out)  # Add the outer control line to the extraction cell

        # Calculate the final pattern
        pad = gdspy.boolean(self.cell_extract, self.cell_subtract, "not")
        self.cell = self.lib.new_cell(name + "_cell")  # Create the final cell
        self.cell.add(pad)  # Add the final pattern to the final cell
        return