############################################################################################
# File Name: readout_line_finger_plus.py
# Description: This file primarily contains the code for constructing a readout cavity.
#              The ReadoutLineFingerPlus class and Finger class are defined to draw the geometric shapes
#              of the readout line and finger structures.
############################################################################################

import gdspy
import copy
import math
import numpy as np
from addict import Dict
import toolbox
from base.library_base import LibraryBase
from library.readout_lines.readout_cavity_plus import ReadoutCavityPlus

class ReadoutLineFingerPlus(LibraryBase):
    default_options = Dict(
        # Framework
        name = "readout1",  # Readout line name
        type = "ReadoutLineFinger2",  # Type
        chip = "chip0",  # Chip name
        start_pos = (0, 0),  # Start position
        coupling_length = 300,  # Coupling length
        coupling_dist = 26.5,  # Coupling distance
        width = 10,  # Readout line width
        gap = 6,  # Gap
        outline = [],  # Outline
        # Geometric parameters
        height = 1000,  # Height
        finger_length = 300,  # Finger length
        finger_orientation = 180,  # Finger orientation
        start_dir = "top",  # Start direction
        start_length = 300,  # Start length
        length = 3000,  # Total length
        space_dist = 200,  # Space distance
        radius = 90,  # Corner radius
        cpw_orientation = 180  # CPW orientation
    )

    def __init__(self, options: Dict = None):
        """
        Initialize the ReadoutLineFingerPlus class.
        
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
        self.lib = gdspy.GdsLibrary()
        gdspy.library.use_current_library = False
        self.cell = self.lib.new_cell(self.name + "_cell")

        # Get parameters
        height = self.height
        width = self.width
        gap = self.gap
        start_dir = self.start_dir
        start_length = self.start_length
        length = self.length
        radius = self.radius
        coupling_length = self.coupling_length
        coupling_dist = self.coupling_dist
        finger_length = self.finger_length
        finger_orientation = self.finger_orientation
        space_dist = self.space_dist
        cpw_orientation = self.cpw_orientation

        # Calculate the angle of the finger structure
        corner_angle = cpw_orientation - finger_orientation
        if start_dir == "up":
            corner_angle += 90
        else:
            corner_angle -= 90

        if abs(corner_angle) >= 180:
            raise ValueError("The corner angle between the finger and the cavity is too large. Please adjust the parameters!")

        # Create the finger structure
        options = Dict(
            start_pos = (0, 0),
            length = finger_length,
            orientation = finger_orientation,
            corner_angle = corner_angle,
            corner_radius = radius,
            width = width,
            gap = gap
        )
        finger = Finger(options)
        finger.draw_gds()

        # Draw the cavity
        min_corner_length = finger.corner_min_length(corner_angle, radius)
        start_pos = (finger_length + min_corner_length, 0)  # Calculate the start position
        start_pos = (start_pos[0] + min_corner_length * math.cos(math.radians(corner_angle)),
                     start_pos[1] + min_corner_length * math.sin(math.radians(corner_angle)))
        start_pos = toolbox.rotate_point(start_pos, (0, 0), finger_orientation)  # Rotate the start position
        
        corner_length = math.radians(corner_angle) * radius  # Calculate the corner length
        length = length - finger_length - corner_length  # Update the remaining length
        options = Dict(
            start_pos = start_pos,
            coupling_length = coupling_length,
            coupling_dist = coupling_dist,
            width = width,
            gap = gap,
            start_dir = start_dir,
            height = height,
            length = length,
            start_length = start_length,
            space_dist = space_dist,
            radius = radius,
            orientation = cpw_orientation
        )
        rd = ReadoutCavityPlus(options)
        rd.draw_gds()  # Draw the cavity

        # Merge the finger structure and the cavity, and translate to the start position
        start_pos = self.start_pos
        pattern = gdspy.boolean(finger.cell, rd.cell, "or")
        pattern.translate(start_pos[0], start_pos[1])
        self.cell.add(pattern)  # Add to the cell

        return
    
class Finger(LibraryBase):
    default_options = Dict(
        # Framework
        name = "finger0",  # Finger structure name
        type = "Finger",  # Type
        chip = "chip0",  # Chip name
        start_pos = (0, 0),  # Start position
        length = 300,  # Length
        orientation = 0,  # Orientation
        corner_angle = 90,  # Corner angle
        corner_radius = 90,  # Corner radius
        width = 10,  # Width
        gap = 6  # Gap
    )

    def __init__(self, options: Dict = None):
        """
        Initialize the Finger class.
        
        Input:
            options: Dictionary containing the parameters for the finger structure.
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
        Draw the geometric shape of the finger structure and add it to the GDS cell.
        """
        self.lib = gdspy.GdsLibrary()
        gdspy.library.use_current_library = False
        self.cell = self.lib.new_cell(self.name + "_cell")

        # Get parameters
        corner_angle = self.corner_angle
        corner_radius = self.corner_radius
        length = self.length
        width = self.width
        gap = self.gap
        orientation = self.orientation
        start_pos = self.start_pos

        # Calculate the point set for the base shape
        pos = []
        pos.append((0, 0))  # Starting point
        min_length = self.corner_min_length(corner_angle, corner_radius)  # Calculate the minimum corner length
        now_p = (length + min_length, 0)  # Calculate the next point
        pos.append(now_p)
        now_p = (now_p[0] + min_length * math.cos(math.radians(corner_angle)), 
                 now_p[1] + min_length * math.sin(math.radians(corner_angle)))
        pos.append(now_p)

        # Draw the finger structure
        finger = gdspy.FlexPath(pos, width + gap * 2, corners="circular bend", bend_radius=corner_radius).to_polygonset()
        sub_finger = gdspy.FlexPath(pos, width, corners="circular bend", bend_radius=corner_radius).to_polygonset()
        finger = gdspy.boolean(finger, sub_finger, "not")  # Calculate the difference
        
        # Translate and rotate
        finger.rotate(math.radians(orientation), (0, 0))
        finger.translate(start_pos[0], start_pos[1])

        # Add to the cell
        self.cell.add(finger)

        return
    
    def corner_min_length(self, corner_angle, corner_radius):
        """
        Calculate the minimum length for a given corner angle and corner radius.
        
        Input:
            corner_angle: Corner angle (degrees)
            corner_radius: Corner radius
        
        Returns:
            Minimum length
        """
        corner_angle = math.radians(corner_angle)
        return abs(corner_radius * math.tan(corner_angle / 2))  # Calculate the minimum length