############################################################################################
# File Name: readout_cavity_flipchip.py
# Description: This file primarily contains the construction code for the readout cavity.
#              Defines the ReadoutCavityFlipchip class for drawing the geometric shapes of the flip-chip readout cavity.
############################################################################################

import gdspy
import copy
import math
import numpy as np
from addict import Dict
import toolbox
from base.library_base import LibraryBase

class ReadoutCavityFlipchip(LibraryBase):
    default_options = Dict(
        # Framework
        name = "readout1",  # Readout cavity name
        type = "ReadoutCavityFlipchip",  # Type
        chip = "chip0",  # Chip name
        start_pos = (0, 0),  # Starting position
        coupling_length = 300,  # Coupling length
        coupling_dist = 26.5,  # Coupling distance
        width = 10,  # Readout cavity width
        gap = 6,  # Gap
        outline = [],  # Outline
        # Geometric parameters
        start_dir = "up",  # Starting direction
        height = 400,  # Height
        length = 1000,  # Total length
        start_length = 300,  # Starting length
        space_dist = 30,  # Space distance
        radius = 90,  # Corner radius
        orientation = 90,  # Orientation
        smallpad_width = 125,  # Small pad width
        smallpad_height = 30,  # Small pad height
        flip_length_outer = 5,  # Outer flip length
        flip_derection = -135,  # Flip direction
        flip_length_sideling = 93,  # Side flip length
        flip_length_inner = 25  # Inner flip length
    )

    def __init__(self, options: Dict = None):
        """
        Initializes the ReadoutCavityFlipchip class.
        
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

        # Draw the initial shape of the cavity, starting at (0, 0), direction right
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
        smallpad_width = self.smallpad_width
        smallpad_height = self.smallpad_height
        flip_length_outer = self.flip_length_outer
        flip_derection = self.flip_derection
        flip_length_sideling = self.flip_length_sideling
        flip_length_inner = self.flip_length_inner

        # Number of turns
        space_num = self.calc_space_num(height, space_dist)

        # Convert to the length in the case of a straight line
        length, start_length, coupling_length = self.convert_length(length, coupling_length, start_length, corner_num=space_num*2, corner_radius=radius)
        # Calculate the lengths related to drawing
        end_length, one_mid_straight = self.calc_length(length=length, start_length=start_length, coupling_length=coupling_length,
                                                        space_dist=space_dist, height=height, space_num=space_num)
        # Get the drawing point set
        pos = self.get_pos(start_dir, start_length, space_num, space_dist, one_mid_straight, end_length, coupling_length)

        # Calculate the flip path
        flip_outer = (0, -flip_length_outer)
        flip_sideling = (flip_outer[0] + flip_length_sideling * math.cos(math.radians(flip_derection)), 
                         flip_outer[1] - flip_length_sideling * math.sin(math.radians(flip_derection)))
        flip_inner = (flip_sideling[0], flip_sideling[1] - flip_length_inner)
        flip_pos = [flip_inner, flip_sideling, flip_outer]
        pos = flip_pos + pos  # Merge the flip path and other paths

        # Draw the cavity
        path = gdspy.FlexPath(pos, width + gap * 2, corners="circular bend", bend_radius=radius).to_polygonset()
        sub_path = gdspy.FlexPath(pos, width, corners="circular bend", bend_radius=radius).to_polygonset()

        # Draw the small pad
        sub_small_pad = gdspy.Rectangle((flip_inner[0] - smallpad_height / 2, flip_inner[1]),
                                         (flip_inner[0] + smallpad_height / 2, flip_inner[1] - smallpad_width))
        small_pad = gdspy.Rectangle((flip_inner[0] - smallpad_height / 2 - gap, flip_inner[1] + gap),
                                     (flip_inner[0] + smallpad_height / 2 + gap, flip_inner[1] - smallpad_width - gap))

        # Perform boolean operations to generate the cavity
        cavity = gdspy.boolean(path, sub_path, 'not')  # Subtract operation
        small_pad = gdspy.boolean(small_pad, sub_small_pad, 'not')  # Subtract operation
        connect = gdspy.boolean(sub_path, small_pad, 'and')  # Intersection operation

        cavity = gdspy.boolean(cavity, small_pad, 'or')  # Union operation
        cavity = gdspy.boolean(cavity, connect, 'not')  # Subtract operation
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