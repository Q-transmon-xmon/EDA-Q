############################################################################################
# File Name: transmission_single_pad.py
# Description: This file primarily contains the code for constructing transmission lines.
#              Defines the TransmissionSinglePad class, responsible for drawing the geometric shape
#              of transmission lines and setting basic parameters.
############################################################################################

import gdspy
import math, copy
import numpy as np
from addict import Dict
from base.library_base import LibraryBase


class TransmissionSinglePad(LibraryBase):
    # Default option settings
    default_options = Dict(
        # Framework
        name="transmission1",  # Transmission line name
        type="TransmissionPath",  # Transmission line type
        chip="chip0",  # Associated chip
        outline=[],  # Outline
        # Geometric parameters
        pos=[],  # Transmission line position
        width=15,  # Transmission line width
        gap=5,  # Transmission line gap
        pad_width=30,  # Pad width
        pad_height=50,  # Pad height
        pad_gap=5  # Pad gap
    )

    def __init__(self, options: Dict = None):
        """
        Initializes the TransmissionSinglePad class.

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
        self.lib = gdspy.GdsLibrary()  # Create a GDS library
        gdspy.library.use_current_library = False  # Do not use the current library
        self.cell = self.lib.new_cell(self.name + "_cell")  # Create a new cell

        # Add drawing code
        # Example code:
        # If you need to draw a rectangular pad, you can use the following code
        if self.pos:  # Ensure the position is defined
            x, y = self.pos[0]  # Take the first position
            pad = gdspy.Rectangle((x, y), (x + self.pad_width, y + self.pad_height))  # Create a rectangle
            self.cell.add(pad)  # Add the rectangle to the cell

        # Assign the pattern to the cell
        # self.cell.add(pattern)  # Example: Add the drawn pattern to the cell
        return