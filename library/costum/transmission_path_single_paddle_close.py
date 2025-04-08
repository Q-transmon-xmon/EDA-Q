############################################################################################
# File Name: transmission_path_single_paddle_close.py
# Description: This file primarily contains the code for constructing transmission lines
#              with a single paddle.
############################################################################################
import gdspy
import math, copy
import numpy as np
from addict import Dict
from base.library_base import LibraryBase

class TransmissionPathSinglePaddleClose(LibraryBase):
    """
    TransmissionPathSinglePaddleClose class for creating transmission line structures
    with a single paddle.

    Attributes:
        default_options: Dict, containing default single paddle transmission line parameters.
    """
    default_options = Dict(
        # Framework
        name="transmission1",
        type="TransmissionPathSinglePaddleClose",
        chip="chip0",
        outline=[],
        # Geometric parameters
        pos=[],
        width=15,
        gap=5,
        pad_width=30,
        pad_height=30,
        pad_gap=5,
        corner_radius=20
    )

    def __init__(self, options: Dict=None):
        """
        Initializes the TransmissionPathSinglePaddleClose class.

        Input:
            options: Dict, user-defined single paddle transmission line parameters.

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
        Draws the geometric shape of TransmissionPathSinglePaddleClose and adds it to the GDS cell.

        Output:
            None.
        """
        name = self.name
        type = self.type
        chip = self.chip
        outline = copy.deepcopy(self.outline)
        pos = copy.deepcopy(self.pos)
        width = self.width
        gap = self.gap
        pad_width = self.pad_width
        pad_height = self.pad_height
        pad_gap = self.pad_gap
        corner_radius = self.corner_radius
        if pos[0][0] > pos[1][0]:
            pos_inner = [(pos[0][0], pos[0][1]), (pos[1][0] + gap, pos[1][1])]
        else:
            pos_inner = [(pos[0][0], pos[0][1]), (pos[1][0] - gap, pos[1][1])]

        self.lib = gdspy.GdsLibrary()
        gdspy.library.use_current_library = False

        self.cell_subtract = self.lib.new_cell(self.name + "_subtract")
        transmission_L_inner = gdspy.FlexPath(pos_inner, width, corners="circular bend", bend_radius=corner_radius).to_polygonset()
        self.cell_subtract.add(transmission_L_inner)

        self.cell_extract = self.lib.new_cell(name + "_extract")
        control_L_out = gdspy.FlexPath(pos, width + gap * 2, corners="circular bend", bend_radius=corner_radius).to_polygonset()
        self.cell_extract.add(control_L_out)

        """
        Draws the geometric shape of the Paddle and adds it to the GDS cell.
        """
        # External rectangle
        rect1 = gdspy.Rectangle((pos[0][0] - (pad_height / 2 + gap), pos[0][1] - (pad_width / 2 + gap)), (pos[0][0] + pad_height / 2 + gap, pos[0][1] + pad_width / 2 + gap))
        self.cell_extract.add(rect1)

        # Internal rectangle
        rect2 = gdspy.Rectangle((pos[0][0] - (pad_height / 2), pos[0][1] - (pad_width / 2)), (pos[0][0] + pad_height / 2, pos[0][1] + pad_width / 2))
        self.cell_subtract.add(rect2)

        # Perform boolean operations to construct the desired component
        paddle = gdspy.boolean(self.cell_extract, self.cell_subtract, "not")

        self.cell = self.lib.new_cell(name + "_cell")
        self.cell.add(paddle)
        return