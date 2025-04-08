#########################################################################
# File Name: circlemon.py
# Description: Defines the Circlemon class, which simulates the geometric shape of a superconducting qubit.
#              Includes functionality to draw the Transmon structure, including finger structures and readout lines.
#########################################################################

from addict import Dict
from base.library_base import LibraryBase
import toolbox
import copy
import gdspy
import math
import numpy as np

class Circlemon(LibraryBase):
    default_options = Dict(
        # Component framework
        name = "q0",  # Component name
        type = "Transmon",  # Component type
        gds_pos = (0, 0),  # GDS position
        topo_pos = (0, 0),  # Topological position
        chip = "chip0",  # Chip name
        readout_pins = [],  # Readout pins
        control_pins = [],  # Control pins
        coupling_pins = [],  # Coupling pins
        outline = [],  # Outline
        # Geometric parameters
        r1 = 100,  # Radius of the first circle
        r2 = 150,  # Radius of the second circle
        r3 = 250,  # Radius of the third circle
        r4 = 300,  # Radius of the fourth circle
        r5 = 325,  # Radius of the fifth circle
        r6 = 370,  # Radius of the sixth circle
        pad_angle = 90,  # Pad angle
        pad_orientation = 0,  # Pad orientation
        finger_length = 200,  # Finger length
        finger_width = 10,  # Finger width
        finger_gap = 6,  # Finger gap
        finger_orientation = 180,  # Finger orientation
        finger_pad_width = 20,  # Finger pad width
        finger_pad_height = 20,  # Finger pad height
        finger_pad_gap = 6,  # Finger pad gap
        readout_width = 6  # Readout line width
    )

    def __init__(self, options):
        """
        Initialize the Circlemon class.
        
        Input:
            options: Dictionary containing the component's parameter options.
        """
        super().__init__(options)
        return

    def calc_general_ops(self):
        """
        Calculate general operations for the component, including pin positions and outline.
        """
        gds_pos = self.gds_pos
        circle6_rad = self.r6
        pad_orientation = self.pad_orientation
        r3 = self.r3
        finger_length = self.finger_length
        finger_orientation = self.finger_orientation
        finger_pad_width = self.finger_pad_width

        # Calculate readout pin positions
        self.readout_pins = [
            (gds_pos[0] + circle6_rad * np.cos(np.pi / 180 * pad_orientation),
             gds_pos[1] + circle6_rad * np.sin(np.pi / 180 * pad_orientation))
        ]
        self.control_pins = []  # Control pins are empty

        # Calculate coupling pin positions
        length = r3 + finger_length + finger_pad_width / 2
        p = (length * math.cos(finger_orientation / 180 * math.pi),
             length * math.sin(finger_orientation / 180 * math.pi))
        p = (p[0] + gds_pos[0], p[1] + gds_pos[1])
        self.coupling_pins = [p]

        self.outline = []  # Outline is empty
        return

    def draw_gds(self):
        """
        Draw the geometric shape of the Circlemon and add it to the GDS cell.
        """
        # Interfaces
        gds_pos = self.gds_pos
        circle1_rad = self.r1
        circle2_rad = self.r2
        circle3_rad = self.r3
        circle4_rad = self.r4
        circle5_rad = self.r5
        circle6_rad = self.r6
        pad_angle = self.pad_angle
        pad_orientation = self.pad_orientation
        initial_angle = -pad_angle / 2  # Initial angle
        final_angle = pad_angle / 2  # Final angle
        finger_length = self.finger_length
        finger_width = self.finger_width
        finger_gap = self.finger_gap
        finger_orientation = self.finger_orientation
        finger_pad_width = self.finger_pad_width
        finger_pad_height = self.finger_pad_height
        finger_pad_gap = self.finger_pad_gap
        readout_width = self.readout_width

        # Calculate finger coordinates
        left_inner_finger = (gds_pos[0] + circle3_rad, gds_pos[1] - finger_width / 2)
        right_inner_finger = (gds_pos[0] + circle3_rad + finger_length, gds_pos[1] + finger_width / 2)

        left_outer_finger = (gds_pos[0] + circle6_rad, gds_pos[1] - finger_width / 2 - finger_gap)
        right_outer_finger = (gds_pos[0] + circle3_rad + finger_length - finger_pad_gap, gds_pos[1] + finger_width / 2 + finger_gap)

        # Calculate finger pad coordinates
        left_inner_finger_pad = (gds_pos[0] + circle3_rad + finger_length, gds_pos[1] - finger_pad_width / 2)
        right_inner_finger_pad = (gds_pos[0] + circle3_rad + finger_length + finger_pad_height, gds_pos[1] + finger_pad_width / 2)

        left_outer_finger_pad = (gds_pos[0] + circle3_rad + finger_length - finger_pad_gap, gds_pos[1] - finger_pad_width / 2 - finger_pad_gap)
        right_outer_finger_pad = (gds_pos[0] + circle3_rad + finger_length + finger_pad_height + finger_pad_gap, gds_pos[1] + finger_pad_width / 2 + finger_pad_gap)

        # Calculate readout line coordinates
        left_readout_line = (gds_pos[0] + circle5_rad, gds_pos[1] - readout_width / 2)
        right_readout_line = (gds_pos[0] + circle6_rad, gds_pos[1] + readout_width / 2)

        # Drawing
        gdspy.library.use_current_library = False
        self.lib = gdspy.GdsLibrary()
        self.cell = self.lib.new_cell(self.name)

        # Create circles and arcs
        circle1 = gdspy.Round((gds_pos[0], gds_pos[1]), circle1_rad, tolerance=0.01)
        circle2 = gdspy.Round((gds_pos[0], gds_pos[1]), circle2_rad, tolerance=0.01)
        circle3 = gdspy.Round((gds_pos[0], gds_pos[1]), circle3_rad, tolerance=0.01)
        circle6 = gdspy.Round((gds_pos[0], gds_pos[1]), circle6_rad, tolerance=0.01)
        circle_arc = gdspy.Round((gds_pos[0], gds_pos[1]), circle5_rad,
                                 inner_radius=circle4_rad,
                                 initial_angle=np.pi / 180 * initial_angle,
                                 final_angle=np.pi / 180 * final_angle,
                                 tolerance=0.01)

        # Create readout line and finger structures
        readout_line = gdspy.Rectangle(left_readout_line, right_readout_line)
        circle_arc = gdspy.boolean(circle_arc, readout_line, 'or').rotate(np.pi / 180 * pad_orientation, center=(gds_pos[0], gds_pos[1]))
        
        inner_finger = gdspy.Rectangle(left_inner_finger, right_inner_finger)
        inner_finger_pad = gdspy.Rectangle(left_inner_finger_pad, right_inner_finger_pad)
        inner_finger = gdspy.boolean(inner_finger, inner_finger_pad, 'or').rotate(np.pi / 180 * finger_orientation, center=(gds_pos[0], gds_pos[1]))
        
        outer_finger = gdspy.Rectangle(left_outer_finger, right_outer_finger)
        outer_finger_pad = gdspy.Rectangle(left_outer_finger_pad, right_outer_finger_pad)
        outer_finger = gdspy.boolean(outer_finger, outer_finger_pad, 'or').rotate(np.pi / 180 * finger_orientation, center=(gds_pos[0], gds_pos[1]))

        # Generate final shape
        circle_in = gdspy.boolean(circle2, circle1, 'not')
        circle_out = gdspy.boolean(circle6, circle3, 'not')
        circle_out = gdspy.boolean(circle_out, circle_arc, 'not')
        circle = gdspy.boolean(circle_in, circle_out, 'or')
        circle = gdspy.boolean(circle, outer_finger, 'or')
        circle = gdspy.boolean(circle, inner_finger, 'not')
        
        self.cell.add(circle)  # Add shape to the cell

        return