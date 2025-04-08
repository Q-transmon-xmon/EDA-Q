############################################################################################
# File Name: readout_line_finger.py
# Description: This file primarily contains the code for constructing a readout cavity.
#              The ReadoutLineFinger class is defined to draw the geometric shape of the readout line.
############################################################################################

import gdspy
import copy
import math
import numpy as np
from addict import Dict
import toolbox
from base.library_base import LibraryBase

class ReadoutLineFinger(LibraryBase):
    default_options = Dict(
        # Framework
        name = "rdl0",  # Readout line name
        type = "ReadoutLine",  # Type
        chip = "chip0",  # Chip name
        start_pos = (0, 0),  # Start position
        end_pos = (0, 1000),  # End position
        coupling_length = 300,  # Coupling length
        orientation = 90,  # Orientation
        outline = [],  # Outline
        # Geometric parameters
        length = 3000,  # Total length
        cpw_width = 10,  # CPW width
        start_r = 100,  # Starting corner radius
        r = 100,  # Corner radius
        couple_length = 275,  # Coupling length
        space = 26.5,  # Space
        gap = 5,  # Gap
    )

    def __init__(self, options: Dict = None):
        """
        Initialize the ReadoutLineFinger class.
        
        Input:
            options: Dictionary containing the parameters for the readout line.
        """
        super().__init__(options)
        return

    def calc_general_ops(self):
        """
        Calculate general operations, currently not implemented with specific functionality.
        """
        return

    def draw_gds(self):
        """
        Draw the geometric shape of the ReadoutLine and add it to the GDS cell.
        """
        # Interfaces
        name = self.name
        start_pos = copy.deepcopy(self.start_pos)
        end_pos = copy.deepcopy(self.end_pos)
        length = self.length
        cpw_width = self.cpw_width
        start_r = self.start_r
        r = self.r
        couple_length = self.couple_length
        space = self.space
        gap = self.gap

        # Calculate the direction angle
        orientation = toolbox.calculate_direction_angle(start_pos, end_pos)

        # Calculate the straight-line distance
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        dist = math.sqrt(dx**2 + dy**2)
        end_pos = [start_pos[0] + dist, start_pos[1]]

        self.lib = gdspy.GdsLibrary()
        gdspy.library.use_current_library = False
        self.cell = self.lib.new_cell(name + "_cell")
        self.cell_subtract = self.lib.new_cell(name, "_sub_cell")

        # Draw the finger structure
        finger = gdspy.Path(initial_point=start_pos, width=cpw_width + 2 * gap)  # External path
        finger.segment(0, "+x")  # Draw horizontal segment
        finger.turn(start_r, "l")  # Turn
        finger.segment(0, "+y")  # Draw vertical segment

        finger_sub = gdspy.Path(initial_point=start_pos, width=cpw_width)  # Internal path
        finger_sub.segment(0, "+x")  # Draw horizontal segment
        finger_sub.turn(start_r, "l")  # Turn
        finger_sub.segment(0, "+y")  # Draw vertical segment

        finger = gdspy.boolean(finger, finger_sub, "not")  # Calculate the difference

        # Draw the CPW
        options = Dict(
            start_pos=[
                start_pos[0] + start_r, 
                start_pos[1] + start_r
            ],
            end_pos=[
                end_pos[0],
                end_pos[1] + start_r
            ],
            length=length,
            cpw_width=cpw_width,
            start_straight=50,  # Starting straight length
            r=r,  # Corner radius
            start_r=start_r,  # Starting corner radius
            couple_length=couple_length,
            space=space,  # Space
            gap=gap,  # Gap
        )

        # Calculate the distance and angle between start_pos and end_pos
        dx = options.end_pos[0] - options.start_pos[0]
        dy = options.end_pos[1] - options.start_pos[1]
        distance = math.sqrt(dx**2 + dy**2)  # Calculate straight-line distance
        angle = math.atan2(dy, dx) + math.pi / 2  # Calculate angle, rotate 90 degrees counterclockwise
        
        if options.length <= distance:
            raise ValueError("Parameter setting error, the length of the readout line is less than or equal to the distance between the qubit and the transmission line.")
        
        # Create a gdspy path with width cpw_width
        readout_l = gdspy.Path(options.cpw_width, (options.start_pos[0], options.start_pos[1]), number_of_paths=1)
        readout_l.segment(options.start_straight, '+x')  # Draw starting segment

        # Calculate the number of segments and their lengths
        num = round((distance - options.start_r * 2 - options.space) // (options.r * 2))
        if num <= 0:
            raise ValueError("Parameter setting error, the distance between the qubit and the transmission line is too short.")
        last_straight = distance - num * options.r * 2 - options.start_r * 2 - options.space

        segment = round((options.length - options.start_straight - options.start_r * math.pi - num * math.pi * options.r) / (num + 1))
        last_segment = options.length - segment * num - options.start_straight - options.start_r * math.pi - num * math.pi * options.r

        # Add segments and turns
        readout_l.turn(options.start_r, 'rr')  # Turn
        readout_l.segment(segment, '-x')  # Draw segment

        for i in range(num - 1):
            if i == num - 2:
                readout_l.turn(options.r, 'll' if i % 2 == 0 else 'rr')  # Adjust turn direction
                readout_l.segment(last_segment, '+x' if i % 2 == 0 else '-x')  # Draw last segment
            else:
                readout_l.turn(options.r, 'll' if i % 2 == 0 else 'rr')
                readout_l.segment(segment, '+x' if i % 2 == 0 else '-x')  # Draw middle segment

        readout_l.turn(options.r, 'l' if (num - 1) % 2 == 0 else 'r')  # Adjust turn direction
        readout_l.segment(last_straight, '-y')  # Draw final straight segment
        readout_l.turn(options.r, 'l' if (num - 1) % 2 == 0 else 'r')  # Determine final turn direction

        readout_l.segment(options.couple_length, '+x' if (num - 1) % 2 == 0 else '-x')  # Draw coupling segment

        # Rotate the entire shape based on the calculated angle
        readout_l.rotate(0.5 * math.pi, options.start_pos)

        self.cell_subtract.add(readout_l)  # Add to subtract cell

        # Create extract cell
        self.cell_extract = self.lib.new_cell(options.name + "_extract")

        # Recalculate distance and angle
        dx = options.end_pos[0] - options.start_pos[0]
        dy = options.end_pos[1] - options.start_pos[1]
        distance = math.sqrt(dx**2 + dy**2)
        angle = math.atan2(dy, dx) + math.pi / 2  

        # Create another path
        readout_l = gdspy.Path(options.cpw_width + options.gap * 2, (options.start_pos[0], options.start_pos[1]), number_of_paths=1)
        readout_l.segment(options.start_straight, '+x')  # Draw starting segment

        num = round((distance - options.start_r * 2 - options.space) // (options.r * 2))  # Calculate number of segments
        last_straight = distance - num * options.r * 2 - options.start_r * 2 - options.space  # Calculate final straight segment

        segment = round((options.length - options.start_straight - options.start_r * math.pi - num * math.pi * options.r) / (num + 1))  # Calculate segment length
        last_segment = options.length - segment * num - options.start_straight - options.start_r * math.pi - num * math.pi * options.r  # Calculate final segment length

        # Add segments and turns
        readout_l.turn(options.start_r, 'rr')  # Turn
        readout_l.segment(segment, '-x')  # Draw segment

        for i in range(num - 1):
            if i == num - 2:
                readout_l.turn(options.r, 'll' if i % 2 == 0 else 'rr')
                readout_l.segment(last_segment, '+x' if i % 2 == 0 else '-x')  # Draw last segment
            else:
                readout_l.turn(options.r, 'll' if i % 2 == 0 else 'rr')
                readout_l.segment(segment, '+x' if i % 2 == 0 else '-x')  # Draw middle segment

        readout_l.turn(options.r, 'l' if (num - 1) % 2 == 0 else 'r')  # Determine final turn direction
        readout_l.segment(last_straight, '-y')  # Draw final straight segment
        readout_l.turn(options.r, 'l' if (num - 1) % 2 == 0 else 'r');  # Determine final turn direction

        readout_l.segment(options.couple_length, '+x' if (num - 1) % 2 == 0 else '-x')  # Draw coupling segment
        readout_l.rotate(0.5 * math.pi, options.start_pos)  # Rotate shape based on calculated angle

        self.cell_extract.add(readout_l)  # Add to extract cell

        # Generate the final shape using boolean operations
        sub_poly = gdspy.boolean(self.cell_extract, self.cell_subtract, "not")
        all_shape = gdspy.boolean(sub_poly, finger, "or")  # Merge paths

        all_shape.rotate(orientation, start_pos)  # Rotate final shape
        self.cell.add(all_shape)  # Add to main cell

        return