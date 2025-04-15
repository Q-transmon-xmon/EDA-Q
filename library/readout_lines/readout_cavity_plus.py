############################################################################################
# File Name: readout_cavity_plus.py
# Description: This file primarily contains the construction code for the readout cavity.
#              Defines the ReadoutCavityPlus class for drawing the geometric shapes of the readout cavity.
############################################################################################

import gdspy
import copy
import math
import numpy as np
from addict import Dict
import toolbox
from base.library_base import LibraryBase

class ReadoutCavityPlus(LibraryBase):
    default_options = Dict(
        # Framework
        name = "readout1",  # Readout cavity name
        type = "ReadoutCavityPlus",  # Type
        chip = "chip0",  # Chip name
        start_pos = (0, 0),  # Starting position
        coupling_length = 300,  # Coupling length
        coupling_dist = 26.5,  # Coupling distance
        width = 10,  # Readout cavity width
        gap = 6,  # Gap
        outline = [],  # Outline
        # Geometric parameters
        start_dir = "up",  # Starting direction
        height = 700,  # Height
        length = 3000,  # Total length
        start_length = 300,  # Starting length
        space_dist = 200,  # Space distance
        radius = 90,  # Corner radius
        orientation = 90  # Orientation
    )

    def __init__(self, options: Dict = None):
        """
        Initializes the ReadoutCavityPlus class.
        
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
        self.cell = self.lib.new_cell(self.name + "_cell")

        # Retrieve parameters
        start_dir = self.start_dir
        orientation = self.orientation
        width = self.width
        gap = self.gap
        start_pos = self.start_pos
        coupling_length = self.coupling_length
        height = self.height
        length = self.length
        space_dist = self.space_dist
        radius = self.radius
        start_length = self.start_length

        # Number of turns
        space_num = self.calc_space_num(height, space_dist)

        # Convert to the length in the case of a straight line
        length, start_length, coupling_length = self.convert_length(length, coupling_length, start_length, corner_num=space_num*2, corner_radius=radius)
        # Calculate the lengths related to drawing
        end_length, one_mid_straight = self.calc_length(length=length, start_length=start_length, coupling_length=coupling_length,
                                                        space_dist=space_dist, height=height, space_num=space_num)
        # Get the drawing point set
        pos = self.get_pos(start_dir, start_length, space_num, space_dist, one_mid_straight, end_length, coupling_length)
        
        # Draw the cavity
        path = gdspy.FlexPath(pos, width + gap*2, corners="circular bend", bend_radius=radius).to_polygonset()
        sub_path = gdspy.FlexPath(pos, width, corners="circular bend", bend_radius=radius).to_polygonset()
        cavity = gdspy.boolean(path, sub_path, 'not')  # Perform boolean operation to generate the cavity

        # Rotate and translate
        cavity.rotate(math.radians(orientation), (0, 0))  # Rotate the cavity
        cavity.translate(dx=start_pos[0], dy=start_pos[1])  # Translate the cavity

        self.cell.add(cavity)  # Add to the cell
        return
    
    def calc_space_num(self, deltax, dist):
        """
        Calculates the number of turns that can fit between a given height and distance.
        
        Input:
            deltax: Height
            dist: Distance
        
        Returns:
            Number of turns
        """
        return math.floor(deltax / dist) - 1
    
    def calc_corner_diff(self, corner_angle, corner_radius):
        """
        Calculates the difference for a given corner angle and corner radius.
        
        Input:
            corner_angle: Corner angle (degrees)
            corner_radius: Corner radius
        
        Returns:
            Difference
        """
        diff = 2 * corner_radius * math.tan(math.radians(corner_angle) / 2) - math.radians(corner_angle) * corner_radius
        return diff
    
    def calc_length(self, length, start_length, coupling_length, space_dist, height, space_num):
        """
        Calculates the lengths of different parts.
        
        Input:
            length: Total length
            start_length: Starting length
            coupling_length: Coupling length
            space_dist: Space distance
            height: Height
            space_num: Number of turns
        
        Returns:
            End length and middle straight length
        """
        end_length = height - space_num * space_dist
        mid_length = length - start_length - coupling_length - end_length
        one_mid_length = mid_length / space_num
        one_mid_straight = one_mid_length - space_dist
        return end_length, one_mid_straight
    
    def convert_length(self, length, coupling_length, start_length, corner_num, corner_radius):
        """
        Converts to the length in the case of a straight line.
        
        Input:
            length: Total length
            coupling_length: Coupling length
            start_length: Starting length
            corner_num: Number of turns
            corner_radius: Corner radius
        
        Returns:
            Converted lengths
        """
        corner_diff = self.calc_corner_diff(90, corner_radius)
        length += (2 * corner_num + 2) * corner_diff
        coupling_length += corner_radius
        start_length += corner_radius
        return length, start_length, coupling_length
    
    def get_pos(self, start_dir, start_length, space_num, space_dist, one_mid_straight, end_length, coupling_length):
        """
        Calculates the positions of the points in the path based on the parameters.
        
        Input:
            start_dir: Starting direction
            start_length: Starting length
            space_num: Number of turns
            space_dist: Interval
            one_mid_straight: Middle straight length
            end_length: End length
            coupling_length: Coupling length
        
        Returns:
            List of calculated path point positions
        """
        pos = []
        now_p = (0, 0)
        pos.append(now_p)
        
        now_dir = start_dir
        if now_dir == "up":
            now_p = (0, start_length)
            pos.append(now_p)
            now_dir = "bot"
        else:
            now_p = (0, -start_length)
            pos.append(now_p)
            now_dir = "up"
        
        for i in range(space_num):
            now_p = (now_p[0] + space_dist, now_p[1])
            pos.append(now_p)
            if now_dir == "up":
                now_p = (now_p[0], now_p[1] + one_mid_straight)
                pos.append(now_p)
                now_dir = "bot"
            else:
                now_p = (now_p[0], now_p[1] - one_mid_straight)
                pos.append(now_p)
                now_dir = "up"

        now_p = (now_p[0] + end_length, now_p[1])
        pos.append(now_p)
        
        if now_dir == "up":
            now_p = (now_p[0], now_p[1] + coupling_length)
            pos.append(now_p)
        else:
            now_p = (now_p[0], now_p[1] - coupling_length)
            pos.append(now_p)
        
        return copy.deepcopy(pos)  # Return the path point positions