############################################################################################
# File Name: readout_cavity.py
# Description: This file primarily contains the construction code for the readout cavity.
#              Defines the ReadoutCavity class for drawing the geometric shapes of the readout cavity.
############################################################################################

import gdspy
import math
import numpy as np
from addict import Dict
from base.library_base import LibraryBase

class ReadoutCavity(LibraryBase):
    default_options = Dict(
        # Framework
        name = "rdl0",  # Readout cavity name
        type = "ReadoutCavity",  # Type
        chip = "chip0",  # Chip name
        start_pos = [0, 0],  # Starting position
        end_pos = [0, 1000],  # Ending position
        coupling_length = 300,  # Coupling length
        orientation = 90,  # Orientation
        outline = [],  # Outline
        # Dimension parameters
        length = 3000,  # Total length
        cpw_width = 10,  # CPW width
        start_straight = 300,  # Starting straight length
        start_r = 100,  # Starting corner radius
        r = 100,  # Corner radius
        couple_length = 275,  # Coupling length
        space = 26.5,  # Spacing
        gap = 5  # Gap
    )

    def __init__(self, options: Dict = None):
        """
        Initializes the ReadoutCavity class.
        
        Input:
            options: Dictionary containing the parameters for the readout cavity.
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
        self.cell_subtract = self.lib.new_cell(self.name + "_subtract")

        # Calculate the distance and angle between the start_pos and end_pos
        dx = self.end_pos[0] - self.start_pos[0]
        dy = self.end_pos[1] - self.start_pos[1]
        distance = math.sqrt(dx**2 + dy**2)  # Calculate the distance
        angle = math.atan2(dy, dx) + math.pi / 2  # Calculate the angle, rotate 90 degrees counterclockwise
        
        if self.length <= distance:
            raise ValueError("Parameter error: The length of the readout line is less than or equal to the distance between the qubit and the transmission line.")
        
        # Create a gdspy path with a width of cpw_width
        readout_l = gdspy.Path(self.cpw_width, (self.start_pos[0], self.start_pos[1]), number_of_paths=1)
        readout_l.segment(self.start_straight, '+x')  # Draw the starting straight segment

        # Calculate the number of segments and their lengths
        num = round((distance - self.start_r * 2 - self.space) // (self.r * 2))
        if num <= 0:
            raise ValueError("Parameter error: The distance between the qubit and the transmission line is too short.")
        last_straight = distance - num * self.r * 2 - self.start_r * 2 - self.space

        segment = round((self.length - self.start_straight - self.start_r * math.pi - num * math.pi * self.r) / (num + 1))
        last_segment = self.length - segment * num - self.start_straight - self.start_r * math.pi - num * math.pi * self.r

        # Add segments and turns
        readout_l.turn(self.start_r, 'rr')  # Turn
        readout_l.segment(segment, '-x')  # Draw segment

        for i in range(num - 1):
            if i == num - 2:
                readout_l.turn(self.r, 'll' if i % 2 == 0 else 'rr')  # Adjust turn direction
                readout_l.segment(last_segment, '+x' if i % 2 == 0 else '-x')  # Draw the last segment
            else:
                readout_l.turn(self.r, 'll' if i % 2 == 0 else 'rr')
                readout_l.segment(segment, '+x' if i % 2 == 0 else '-x')  # Draw intermediate segments

        readout_l.turn(self.r, 'l' if (num - 1) % 2 == 0 else 'r')
        readout_l.segment(last_straight, '-y')  # Draw the last straight segment
        readout_l.turn(self.r, 'l' if (num - 1) % 2 == 0 else 'r')

        readout_l.segment(self.coupling_length, '+x' if (num - 1) % 2 == 0 else '-x')  # Draw the coupling segment

        # Rotate the entire shape based on the calculated angle
        readout_l.rotate(angle, self.start_pos)

        self.cell_subtract.add(readout_l)  # Add the path to the subtract cell


        # Create the extract cell
        self.cell_extract = self.lib.new_cell(self.name + "_extract")
        readout_l = gdspy.Path(self.cpw_width + self.gap * 2, (self.start_pos[0], self.start_pos[1]), number_of_paths=1)
        readout_l.segment(self.start_straight, '+x')  # Draw the starting straight segment

        num = round((distance - self.start_r * 2 - self.space) // (self.r * 2))
        last_straight = distance - num * self.r * 2 - self.start_r * 2 - self.space

        segment = round((self.length - self.start_straight - self.start_r * math.pi - num * math.pi * self.r) / (num + 1))
        last_segment = self.length - segment * num - self.start_straight - self.start_r * math.pi - num * math.pi * self.r

        readout_l.turn(self.start_r, 'rr')
        readout_l.segment(segment, '-x')

        for i in range(num - 1):
            if i == num - 2:
                readout_l.turn(self.r, 'll' if i % 2 == 0 else 'rr')
                readout_l.segment(last_segment, '+x' if i % 2 == 0 else '-x')
            else:
                readout_l.turn(self.r, 'll' if i % 2 == 0 else 'rr')
                readout_l.segment(segment, '+x' if i % 2 == 0 else '-x')

        readout_l.turn(self.r, 'l' if (num - 1) % 2 == 0 else 'r')
        readout_l.segment(last_straight, '-y')
        readout_l.turn(self.r, 'l' if (num - 1) % 2 == 0 else 'r')

        readout_l.segment(self.coupling_length, '+x' if (num - 1) % 2 == 0 else '-x')

        readout_l.rotate(angle, self.start_pos)

        self.cell_extract.add(readout_l)  # Add the path to the extract cell

        # Use boolean operations to generate the final shape
        sub_poly = gdspy.boolean(self.cell_extract, self.cell_subtract, "not")
        self.cell = self.lib.new_cell(self.name + "_cell")  # Create the final cell
        self.cell.add(sub_poly)  # Add the final shape

        return