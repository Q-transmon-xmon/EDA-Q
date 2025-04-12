############################################################################################
# File Name: readout_arrow_plus.py
# Description: This file primarily contains the construction code for the readout cavity.
#              Defines the ReadoutArrowPlus and ArrowFinger classes for drawing the geometric shapes of the readout line.
############################################################################################

import gdspy
import copy
import math
import numpy as np
from addict import Dict
import toolbox
from base.library_base import LibraryBase
from library.readout_lines.readout_cavity_plus import ReadoutCavityPlus

class ReadoutArrowPlus(LibraryBase):
    default_options = Dict(
        # Framework
        name = "readout1",  # Readout line name
        type = "ReadoutArrowPlus",  # Type
        chip = "chip0",  # Chip name
        start_pos = (0, 0),  # Starting position
        coupling_length = 300,  # Coupling length
        coupling_dist = 26.5,  # Coupling distance
        width = 10,  # Readout line width
        gap = 6,  # Gap
        outline = [],  # Outline
        # Geometric parameters
        height = 1000,  # Height
        finger_length = 300,  # Finger length
        finger_orientation = 45,  # Finger orientation
        start_dir = "up",  # Starting direction
        start_length = 300,  # Starting length
        length = 3000,  # Total length
        space_dist = 200,  # Spacing distance
        radius = 90,  # Corner radius
        cpw_orientation = 45,  # CPW orientation
        arrow_length = 150,  # Arrow length
        arrow_orientation = 225,  # Arrow orientation
    )

    def __init__(self, options: Dict = None):
        """
        Initializes the ReadoutArrowPlus class.
        
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
        arrow_length = self.arrow_length
        arrow_orientation = self.arrow_orientation

        # Draw arrow_finger
        corner_angle = cpw_orientation - finger_orientation
        if start_dir == "up":
            corner_angle += 90
        else:
            corner_angle -= 90

        if abs(corner_angle) >= 180:
            raise ValueError("The corner angle between the finger and cavity is too large. Please adjust the parameters!")

        options = Dict(
            start_pos = (0, 0),
            finger_length = finger_length,
            finger_orientation = finger_orientation,
            corner_angle = corner_angle,
            corner_radius = radius,
            width = width,
            gap = gap,
            arrow_length = arrow_length,
            arrow_orientation = arrow_orientation,
        )
        arrow_finger = ArrowFinger(options)  # Create an ArrowFinger object
        arrow_finger.draw_gds()  # Draw the arrow finger

        # Draw cavity
        min_corner_length = arrow_finger.corner_min_length(corner_angle, radius)  # Calculate the minimum corner length
        start_pos = (finger_length + min_corner_length, 0)
        start_pos = (start_pos[0] + min_corner_length * math.cos(math.radians(corner_angle)),
                     start_pos[1] + min_corner_length * math.sin(math.radians(corner_angle)))
        start_pos = toolbox.rotate_point(start_pos, (0, 0), finger_orientation)  # Rotate the starting position
        
        corner_length = math.radians(corner_angle) * radius
        length = length - finger_length - corner_length
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
        rd = ReadoutCavityPlus(options)  # Create a ReadoutCavityPlus object
        rd.draw_gds()  # Draw the readout cavity

        # Merge and translate
        start_pos = self.start_pos
        pattern = gdspy.boolean(arrow_finger.cell, rd.cell, "or")  # Merge shapes
        pattern.translate(start_pos[0], start_pos[1])  # Translate to the starting position
        self.cell.add(pattern)  # Add to the cell

        return
    
class ArrowFinger(LibraryBase):
    default_options = Dict(
        # Framework
        name = "finger0",  # Finger name
        type = "Finger",  # Type
        chip = "chip0",  # Chip name
        start_pos = (0, 0),  # Starting position
        finger_length = 300,  # Finger length
        finger_orientation = 0,  # Finger orientation
        corner_angle = 90,  # Corner angle
        corner_radius = 90,  # Corner radius
        width = 10,  # Finger width
        gap = 6,  # Gap
        arrow_length = 150,  # Arrow length
        arrow_orientation = 0,  # Arrow orientation
    )

    def __init__(self, options: Dict = None):
        """
        Initializes the ArrowFinger class.
        
        Input:
            options: Dictionary containing the parameters for the finger.
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
        corner_angle = self.corner_angle
        corner_radius = self.corner_radius
        finger_length = self.finger_length
        width = self.width
        gap = self.gap
        finger_orientation = self.finger_orientation
        start_pos = self.start_pos
        arrow_length = self.arrow_length
        arrow_orientation = self.arrow_orientation

        # Finger base position, starting at (0, 0)
        pos = []
        pos.append((0, 0))
        min_length = self.corner_min_length(corner_angle, corner_radius)  # Calculate the minimum corner length
        now_p = (finger_length + min_length, 0)
        pos.append(now_p)
        now_p = (now_p[0] + min_length * math.cos(math.radians(corner_angle)), 
                 now_p[1] + min_length * math.sin(math.radians(corner_angle)))
        pos.append(now_p)

        # Draw finger
        finger = gdspy.FlexPath(pos, width + gap * 2, corners="circular bend", bend_radius=corner_radius).to_polygonset()
        sub_finger = gdspy.FlexPath(pos, width, corners="circular bend", bend_radius=corner_radius).to_polygonset()

        # Rotate finger
        finger.rotate(math.radians(finger_orientation), (0, 0))
        sub_finger.rotate(math.radians(finger_orientation), (0, 0))

        # Arrow base position, starting at (0, 0)
        angle1 = arrow_orientation + 135
        angle2 = angle1 + 90
        arrow_pos = []
        now_p = (arrow_length * math.cos(math.radians(angle1)), arrow_length * math.sin(math.radians(angle1)))
        arrow_pos.append(now_p)
        now_p = (0, 0)
        arrow_pos.append(now_p)
        now_p = (arrow_length * math.cos(math.radians(angle2)), arrow_length * math.sin(math.radians(angle2)))
        arrow_pos.append(now_p)

        angle1 = arrow_orientation + 135
        angle2 = angle1 + 90
        sub_arrow_pos = []
        now_p = ((arrow_length - gap) * math.cos(math.radians(angle1)), 
                  (arrow_length - gap) * math.sin(math.radians(angle1)))
        sub_arrow_pos.append(now_p)
        now_p = (0, 0)
        sub_arrow_pos.append(now_p)
        now_p = ((arrow_length - gap) * math.cos(math.radians(angle2)), 
                  (arrow_length - gap) * math.sin(math.radians(angle2)))
        sub_arrow_pos.append(now_p)

        # Draw arrow
        arrow = gdspy.FlexPath(arrow_pos, width + gap * 2, corners="natural").to_polygonset()
        sub_arrow = gdspy.FlexPath(sub_arrow_pos, width, corners="natural").to_polygonset()

        # Get the total shape
        arrow_finger = gdspy.boolean(finger, arrow, "or")  # Merge finger and arrow
        sub_arrow_finger = gdspy.boolean(sub_finger, sub_arrow, "or")  # Merge sub-finger and sub-arrow
        arrow_finger = gdspy.boolean(arrow_finger, sub_arrow_finger, "not")  # Subtract sub-arrow_finger
        
        # Translate
        arrow_finger.translate(start_pos[0], start_pos[1])  # Translate to the starting position

        # Add to cell
        self.cell.add(arrow_finger)

        return
    
    def corner_min_length(self, corner_angle, corner_radius):
        """
        Calculates the minimum length for a given corner angle and corner radius.
        
        Input:
            corner_angle: Corner angle (degrees)
            corner_radius: Corner radius
        
        Returns:
            Minimum length
        """
        corner_angle = math.radians(corner_angle)
        return abs(corner_radius * math.tan(corner_angle / 2))