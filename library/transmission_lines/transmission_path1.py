############################################################################################
# File Name: transmission_path1.py
# Description: This file primarily contains the code for constructing transmission lines.
#              Defines the TransmissionPath1 class, responsible for drawing the geometric shape
#              of transmission lines and setting basic parameters.
############################################################################################

import gdspy
import math, copy
import numpy as np
from addict import Dict
from base.library_base import LibraryBase


class TransmissionPath1(LibraryBase):
    # Default option settings
    default_options = Dict(
        # Framework
        name="transmission1",  # Transmission line name
        type="TransmissionPath1",  # Transmission line type
        chip="chip0",  # Associated chip
        outline=[],  # Outline
        # Geometric parameters
        pos=[(0, 0), (500, 0), (1000, 0), (1500, 0)],  # Coordinates of the transmission line positions
        width=[10, 15, 10],  # List of transmission line widths
        gap=[6, 9, 6],  # List of transmission line gaps
        buffer_length=[100, 50],  # List of buffer lengths
        corner_radius=20  # Corner radius
    )

    def __init__(self, options=Dict()):
        """
        Initializes the TransmissionPath1 class.

        Input:
            options: Optional dictionary of parameters to override default options.
        """
        super().__init__(options)  # Call the parent class constructor
        return

    def calc_general_ops(self):
        """
        Requires calculating the following parameters:
        - readout_pins
        - control_pins
        - coupling_pins
        - outline
        """
        return

    def draw_gds(self):
        """
        Draws the geometric shape of the quantum bit and adds it to the GDS cell.
        """
        ################################ gdspy Variables ################################
        # Do not modify this part of the code
        gdspy.library.use_current_library = False  # Do not use the current library
        self.lib = gdspy.GdsLibrary()  # Create a GDS library
        self.cell = self.lib.new_cell(self.name)  # Create a new cell
        ################################ Interface ################################
        # The purpose of the interface is to facilitate subsequent user parameter updates.
        # Users can update the interface only, and the code below the interface remains unchanged.
        ################################ Parameter Conversion ################################
        # This module exists to reconcile the contradiction between user convenience and developer convenience.
        # It converts user-friendly parameter sets into parameter sets convenient for drawing.
        # Example code:
        # claw_width0 = self.claw_width
        # claw_height0 = self.claw_height
        # claw_width1 = self.claw_width - 2 * self.claw_small_width
        # claw_height1 = self.claw_height - self.claw_small_height
        # Then, draw two rectangles in the following drawing part and subtract the two shapes to get the claw prototype (excluding gap)
        ################################ Drawing ################################
        # Add your code here
        # Example drawing logic:
        # pattern = gdspy.Rectangle((x1, y1), (x2, y2))  # Create a rectangle
        # gdspy.rotate(pattern, orientation)               # Rotate the shape
        # gdspy.translate(pattern, (gds_pos[0], gds_pos[1]))  # Translate the shape
        # self.cell.add(pattern)                           # Add the shape to the cell

        ########################################################################
        return