############################################################################################
# File Name: readout_arrow.py
# Description: This file primarily contains the construction code for the readout cavity.
#              Defines the ReadoutArrow class for drawing the geometric shapes of the readout line and arrow.
############################################################################################

import gdspy
import copy
import math
import numpy as np
from addict import Dict
import toolbox
from library.readout_lines.readout_line_finger import ReadoutLineFinger
from library.others.arrow import Arrow
from base.library_base import LibraryBase

class ReadoutArrow(LibraryBase):
    default_options = Dict(
        # Framework
        name = "readout1",  # Readout line name
        type = "ReadoutArrow",  # Type
        chip = "chip0",  # Chip name
        start_pos = (0, 0),  # Starting position
        end_pos = (0, 1000),  # Ending position
        outline = [],  # Outline
        # Geometric parameters
        start_length = 300,  # Starting length
        start_r = 90,  # Starting corner radius
        arrow_length = 200,  # Arrow length
        cpw_height = 800,  # CPW height
        cpw_length = 2000,  # CPW length
        cpw_r = 90,  # CPW corner radius
        couple_length = 275,  # Coupling length
        space = 26.5,  # Spacing
        gap = 6,  # Gap
        width = 10,  # Readout line width
        orientation = 0  # Orientation
    )

    def __init__(self, options: Dict = None):
        """
        Initializes the ReadoutArrow class.
        
        Input:
            options: Dictionary containing the parameters for the readout line.
        """
        super().__init__(options)
        return

    def calc_general_ops(self):
        """
        Calculates general operations, currently not implemented.
        """
        return

    def draw_gds(self):
        """
        Draws the geometric shapes of the ReadoutLine and adds them to the GDS cell.
        """
        self.lib = gdspy.GdsLibrary()
        gdspy.library.use_current_library = False
        self.cell = self.lib.new_cell(self.name + "_cell")

        # Retrieve parameters
        start_length = self.start_length
        start_r = self.start_r
        arrow_length = self.arrow_length
        cpw_height = self.cpw_height
        cpw_length = self.cpw_length
        cpw_r = self.cpw_r
        couple_length = self.couple_length
        space = self.space
        gap = self.gap
        width = self.width
        end_pos = self.end_pos
        start_pos = copy.deepcopy(self.start_pos)  # Deep copy the starting position
        orientation = self.orientation
        delta = copy.deepcopy(start_pos)

        # Draw the arrow
        options = Dict(
            start_pos = delta,  # Arrow starting position
            inclined_length = start_length,  # Inclined length
            gap = gap,  # Gap
            width = width,  # Width
            height = arrow_length,  # Height
            inclined_width = width,  # Inclined width
            orientation = 0  # Orientation
        )
        arrow = Arrow(options)  # Create an Arrow object
        arrow.draw_gds()  # Draw the arrow

        # Create the readout line finger object
        options = Dict(
            start_pos = arrow.end_pos,  # Finger starting position is the arrow's end position
            end_pos = [arrow.end_pos[0], arrow.end_pos[1] + cpw_height],  # Finger ending position
            length = cpw_length,  # Finger length
            cpw_width = width,  # CPW width
            start_r = start_r,  # Starting corner radius
            r = cpw_r,  # CPW corner radius
            couple_length = couple_length,  # Coupling length
            space = space,  # Spacing
            gap = gap  # Gap
        )
        finger = ReadoutLineFinger(options)  # Create a ReadoutLineFinger object
        finger.draw_gds()  # Draw the readout line finger
        self.end_pos = options.end_pos  # Update the ending position

        # Merge the arrow and finger shapes
        all_pattern = gdspy.boolean(arrow.cell, finger.cell, operation="or")  # Perform OR operation
        all_pattern.rotate(orientation, start_pos)  # Rotate the shape
        self.cell.add(all_pattern)  # Add to the cell

        return