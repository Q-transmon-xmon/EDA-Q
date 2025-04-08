###############################################################################################
# File Name: control_line_circle2408.py
# Description: This file primarily contains the construction code for the ControlLineCircle2408.
############################################################################################

import gdspy
import math
import numpy as np
from addict import Dict
from copy import deepcopy
import toolbox
from base.library_base import LibraryBase

import math


def add_points(pos):
    """
    Adds additional points to the curve.

    Input:
        pos: List, containing the coordinates of the curve points.

    Output:
        pos: Extended list, containing the new point coordinates.
    """
    # Get the last two points of the curve
    x1, y1 = pos[-2]
    x2, y2 = pos[-1]

    # Calculate the angle of the last segment
    angle = math.atan2(y2 - y1, x2 - x1)

    # Add t3 point, turning right 45 degrees, extending 45 units
    angle_t3 = angle - math.radians(45)
    x3 = x2 + 45 * math.cos(angle_t3)
    y3 = y2 + 45 * math.sin(angle_t3)
    t3 = (x3, y3)

    # Add t4 point, continuing to turn left 90 degrees, extending 45 units
    angle_t4 = angle_t3 + math.radians(90)
    x4 = x3 + 45 * math.cos(angle_t4)
    y4 = y3 + 45 * math.sin(angle_t4)
    t4 = (x4, y4)

    # Add t5 point, continuing to turn left 90 degrees, extending 45 units
    angle_t5 = angle_t4 + math.radians(90)
    x5 = x4 + 45 * math.cos(angle_t5)
    y5 = y4 + 45 * math.sin(angle_t5)
    t5 = (x5, y5)

    # Add t6 point, continuing to turn left 90 degrees, extending 30 units
    angle_t6 = angle_t5 + math.radians(90)
    x6 = x5 + 30 * math.cos(angle_t6)
    y6 = y5 + 30 * math.sin(angle_t6)
    t6 = (x6, y6)

    # Add t7 point, continuing to turn right 45 degrees, extending 20 units
    angle_t7 = angle_t6 - math.radians(45)
    x7 = x6 + 20 * math.cos(angle_t7)
    y7 = y6 + 20 * math.sin(angle_t7)
    t7 = (x7, y7)

    # Add t3 to t7 to the pos list
    pos.extend([t3, t4, t5, t6, t7])

    return pos


def calculate_intermediate_points(pos):
    """
    Calculates intermediate points.

    Input:
        pos: List, containing at least five point coordinates.

    Output:
        point1, point2: Calculated coordinates of the two intermediate points.
    """
    if len(pos) < 5:
        raise ValueError("pos must contain at least 5 elements")

        # Get pos[-5] and pos[-3]
    p1 = deepcopy(pos[-5])
    p2 = deepcopy(pos[-3])

    # Calculate the direction vector
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]

    # Calculate the unit vector
    mag = (dx ** 2 + dy ** 2) ** 0.5
    ux = dx / mag
    uy = dy / mag

    u = 4

    # Calculate the first point (along the direction from p1 to p2, 3 units away from p1)
    point1 = (p1[0] + ux * u, p1[1] + uy * u)

    # Calculate the second point (along the direction from p2 to p1, 3 units away from p2)
    point2 = (p2[0] - ux * u, p2[1] - uy * u)

    return point1, point2


class ControlLineCircle2408(LibraryBase):
    """
    ControlLineCircle2408 class.

    Contains the construction and drawing functions for the ControlLineCircle2408.
    """
    default_options = Dict(
        # Framework
        name="charge_line0",
        type="ControlLineCircle2408",
        chip="chip0",
        pos=[[0, 0], [500, 0]],
        # Geometric parameters
        width=4,
        gap=2,
        radius=20,
        distance=50,
        corner_radius=10
    )

    def __init__(self, options: Dict = None):
        """
        Initializes the ControlLineCircle2408 class.

        Input:
            options: Dictionary, containing parameters for constructing the ControlLineCircle2408.
        """
        super().__init__(options)
        return

    def calc_general_ops(self):
        """
        Calculates general operations.
        """
        return

    def draw_gds(self):
        """
        Draws the GDS file.
        """
        self.lib = gdspy.GdsLibrary()
        gdspy.library.use_current_library = False

        corner_radius = self.corner_radius
        pos = deepcopy(self.pos)
        self.cell_extract = self.lib.new_cell(self.name + "_extract")
        self.cell_subtract = self.lib.new_cell(self.name + "_subtract")

        pos = add_points(pos)
        control_L_out = gdspy.FlexPath(pos, self.width + self.gap * 2,
                                       corners="circular bend", bend_radius=corner_radius).to_polygonset()

        control_L_inner = gdspy.FlexPath(pos, self.width,
                                         corners="circular bend", bend_radius=corner_radius).to_polygonset()
        (x1, y1), (x2, y2) = calculate_intermediate_points(pos)
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2
        half_diagonal = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5 / 2

        # Calculate the direction vector of the diagonal
        dx = x2 - x1
        dy = y2 - y1

        # Rotate the vector 90 degrees: (-dy, dx)
        # Scale it to half the length of the square's side
        side_half_vector = (
        -dy / (dx ** 2 + dy ** 2) ** 0.5 * half_diagonal, dx / (dx ** 2 + dy ** 2) ** 0.5 * half_diagonal)

        # Find the other two corner points
        point3 = (cx - side_half_vector[0], cy - side_half_vector[1])
        point4 = (cx + side_half_vector[0], cy + side_half_vector[1])
        point1 = (x1, y1)
        point2 = (x2, y2)
        square = gdspy.Polygon([point1, point4, point2, point3])
        control_L_out = gdspy.boolean(control_L_out, square, "or")
        self.cell_extract.add(control_L_out)
        # self.cell_extract.add(circle)

        self.cell_subtract.add(control_L_inner)
        # self.cell_subtract.add(circle)

        pad = gdspy.boolean(self.cell_extract, self.cell_subtract, "not")
        # pad = gdspy.boolean(pad, square, "or")
        self.cell = self.lib.new_cell(self.name + "_cell")
        self.cell.add(pad)

        return