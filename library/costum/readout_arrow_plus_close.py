############################################################################################
# File Name: readout_arrow_plus_close.py
# Description: This file primarily contains the construction code for the ReadoutArrowPlusClose.
############################################################################################

import gdspy
import copy
import math
import numpy as np
from addict import Dict
import toolbox
from base.library_base import LibraryBase
from library.readout_lines.readout_cavity_plus import ReadoutCavityPlus


class ReadoutArrowPlusClose(LibraryBase):
    """
    ReadoutArrowPlusClose class for creating readout cavity structures.

    Attributes:
        default_options: Dict, containing default parameters for the readout cavity.
    """
    default_options = Dict(
        # Framework
        name="readout1",
        type="ReadoutArrowPlusClose",
        chip="chip0",
        start_pos=(0, 0),
        coupling_length=200,
        coupling_dist=26.5,
        width=10,
        gap=6,
        outline=[],
        # Geometric parameters
        height=800,
        finger_length=300,
        finger_orientation=-45,
        start_dir="bot",
        start_length=150,
        length=3000,
        space_dist=100,
        radius=50,
        cpw_orientation=0,
        arrow_length=150,
        arrow_orientation=135,
    )

    def __init__(self, options: Dict = None):
        """
        Initializes the ReadoutArrowPlusClose class.

        Input:
            options: Dict, user-defined parameters for the readout cavity.

        Output:
            None.
        """
        super().__init__(options)
        return

    def calc_general_ops(self):
        """
        Calculates general operations.

        Output:
            None.
        """
        return

    def draw_gds(self):
        """
        Draws the geometric shape of the ReadoutArrowPlusClose and adds it to the GDS cell.

        Output:
            None.
        """
        self.lib = gdspy.GdsLibrary()
        gdspy.library.use_current_library = False
        self.cell = self.lib.new_cell(self.name + "_cell")

        # Draw the initial shape of the cavity, starting at (0, 0), direction to the right
        # Interface
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
            raise ValueError(
                "The corner angle between the finger and the cavity is too large. Please adjust the parameters!")

        options = Dict(
            start_pos=(0, 0),
            finger_length=finger_length,
            finger_orientation=finger_orientation,
            corner_angle=corner_angle,
            corner_radius=radius,
            width=width,
            gap=gap,
            arrow_length=arrow_length,
            arrow_orientation=arrow_orientation,
        )
        arrow_finger = ArrowFinger(options)
        arrow_finger.draw_gds()

        # Draw the cavity
        min_corner_length = arrow_finger.corner_min_length(corner_angle, radius)
        start_pos = (finger_length + min_corner_length, 0)
        start_pos = (start_pos[0] + min_corner_length * math.cos(math.radians(corner_angle)),
                     start_pos[1] + min_corner_length * math.sin(math.radians(corner_angle)))
        start_pos = toolbox.rotate_point(start_pos, (0, 0), finger_orientation)

        corner_length = math.radians(corner_angle) * radius
        length = length - finger_length - corner_length
        options = Dict(
            start_pos=start_pos,
            coupling_length=coupling_length,
            coupling_dist=coupling_dist,
            width=width,
            gap=gap,
            start_dir=start_dir,
            height=height,
            length=length,
            start_length=start_length,
            space_dist=space_dist,
            radius=radius,
            orientation=cpw_orientation
        )
        rd = ReadoutCavityPlus(options)
        rd.draw_gds()

        # Merge and translate
        start_pos = self.start_pos
        pattern = gdspy.boolean(arrow_finger.cell, rd.cell, "or")
        pattern.translate(start_pos[0], start_pos[1])
        self.cell.add(pattern)

        return


class ArrowFinger(LibraryBase):
    """
    ArrowFinger class for creating arrow finger structures.

    Attributes:
        default_options: Dict, containing default parameters for the arrow finger.
    """
    default_options = Dict(
        # Framework
        name="finger0",
        type="Finger",
        chip="chip0",
        start_pos=(0, 0),
        finger_length=300,
        finger_orientation=0,
        corner_angle=90,
        corner_radius=90,
        width=10,
        gap=6,
        arrow_length=150,
        arrow_orientation=0,
    )

    def __init__(self, options: Dict = None):
        """
        Initializes the ArrowFinger class.

        Input:
            options: Dict, user-defined parameters for the arrow finger.

        Output:
            None.
        """
        super().__init__(options)
        return

    def calc_general_ops(self):
        """
        Calculates general operations.

        Output:
            None.
        """
        return

    def draw_gds(self):
        """
        Draws the geometric shape of the ArrowFinger and adds it to the GDS cell.

        Output:
            None.
        """
        self.lib = gdspy.GdsLibrary()
        gdspy.library.use_current_library = False
        self.cell = self.lib.new_cell(self.name + "_cell")

        # Interface
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
        min_length = self.corner_min_length(corner_angle, corner_radius)
        now_p = (finger_length + min_length, 0)
        pos.append(now_p)
        now_p = (now_p[0] + min_length * math.cos(math.radians(corner_angle)),
                 now_p[1] + min_length * math.sin(math.radians(corner_angle)))
        pos.append(now_p)

        # Draw finger
        finger = gdspy.FlexPath(pos, width + gap * 2, corners="circular bend",
                                bend_radius=corner_radius).to_polygonset()
        sub_finger = gdspy.FlexPath(pos, width, corners="circular bend", bend_radius=corner_radius).to_polygonset()

        # Rotate finger
        finger.rotate(math.radians(finger_orientation), (0, 0))
        sub_finger.rotate(math.radians(finger_orientation), (0, 0))

        # Arrow base position, starting at (0, 0), direction to the right
        angle1 = arrow_orientation + 135
        angle2 = angle1 + 90
        arrow_pos = []
        arrow_pos1 = []

        now_p = (arrow_length * math.cos(math.radians(angle1)), arrow_length * math.sin(math.radians(angle1)))
        arrow_pos.append(now_p)
        now_p = (0, 0)
        arrow_pos.append(now_p)
        now_p = (arrow_length * math.cos(math.radians(angle2)), arrow_length * math.sin(math.radians(angle2)))
        arrow_pos.append(now_p)

        now_p1 = (
        (arrow_length - gap) * math.cos(math.radians(angle1)), (arrow_length - gap) * math.sin(math.radians(angle1)))
        arrow_pos1.append(now_p1)
        now_p1 = (0, 0)
        arrow_pos1.append(now_p1)
        now_p1 = (
        (arrow_length - gap) * math.cos(math.radians(angle2)), (arrow_length - gap) * math.sin(math.radians(angle2)))
        arrow_pos1.append(now_p1)

        # Draw arrow
        arrow = gdspy.FlexPath(arrow_pos, width + gap * 2, corners="natural").to_polygonset()
        sub_arrow = gdspy.FlexPath(arrow_pos1, width, corners="natural").to_polygonset()

        # Get the total shape
        arrow_finger = gdspy.boolean(finger, arrow, "or")
        sub_arrow_finger = gdspy.boolean(sub_finger, sub_arrow, "or")
        arrow_finger = gdspy.boolean(arrow_finger, sub_arrow_finger, "not")

        # Translate
        arrow_finger.translate(start_pos[0], start_pos[1])

        # Add to cell
        self.cell.add(arrow_finger)

        return

    def corner_min_length(self, corner_angle, corner_radius):
        """
        Calculates the minimum corner length.
        Input:
            corner_angle: Angle, the size of the corner.
            corner_radius: Radius, the radius of the corner.

        Output:
            Minimum corner length.
        """
        corner_angle = math.radians(corner_angle)
        return abs(corner_radius * math.tan(corner_angle / 2))