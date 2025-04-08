#########################################################################
# File Name: coupler_base.py
# Description: Defines the CouplerBase class for creating base structures of couplers.
#              Includes functionality for initializing parameters, calculating general operations,
#              and drawing GDSII files.
#########################################################################

import gdspy
import math, copy
import numpy as np
from addict import Dict
from base.library_base import LibraryBase


class CouplerBase(LibraryBase):
    """
    CouplerBase class for creating base structures of couplers.

    Attributes:
        default_options: Dict, containing default coupler parameters.
    """
    default_options = Dict(
        # Framework
        name="CouplerBase0",
        type="CouplerBase",
        chip="chip0",
        pos=[0, 0],  # Center of the two rectangles
        width=180,  # Outer width
        metal_width=30,  # Metal width
        upper_height=200,
        lower_height=80,
        gap=10,
        claw_height=15,
        claw_width=100,
        rotate=0,
        start_pos=[0, 500],
        end_pos=[0, 0],
        # Interface
    )

    def __init__(self, options=Dict()):
        """
        Initializes the CouplerBase class.

        Input:
            options: Dict, user-defined coupler parameters.

        Output:
            None.
        """
        super().__init__(options)
        return

    def calc_general_ops(self):
        """
        Calculates general operations.

        Requires calculating the following parameters:
        readout_pins
        control_pins
        coupling_pins
        outline

        Output:
            None.
        """
        return

    def draw_gds(self):
        """
        Draws the GDSII file.

        Output:
            None.
        """
        ################################ gdspy Variables #################################
        self.lib = gdspy.GdsLibrary()
        gdspy.library.use_current_library = False
        self.cell = self.lib.new_cell(self.name + "_cell")

        ################################ Interface #################################
        # The purpose of the interface is to facilitate subsequent user parameter updates.
        # Users can update the interface only, and the code below the interface remains unchanged.

        # Framework
        pos = self.options.pos
        width = self.options.width
        upper_height = self.options.upper_height
        lower_height = self.options.lower_height
        gap = self.options.gap
        claw_height = self.options.claw_height
        claw_width = self.options.claw_width
        metal_width = self.options.metal_width
        rotate = self.options.rotate
        start_pos = self.options.start_pos
        end_pos = self.options.end_pos

        ################################ Parameter Conversion #################################
        # This module exists to reconcile the contradiction between user convenience and developer convenience.
        # It converts user-friendly parameter sets into parameter sets convenient for drawing.
        if abs(start_pos[0] - end_pos[0]) < width and abs(start_pos[1] - end_pos[1]) < width:
            raise ValueError("Start_pos and end_pos should be at least Couplerwidth apart")

        claw_width = (max(abs(start_pos[0] - end_pos[0]), abs(start_pos[1] - end_pos[1])) - width) / 2
        pos = [(start_pos[0] + end_pos[0]) / 2, (start_pos[1] + end_pos[1]) / 2]
        if start_pos[0] == end_pos[0]:
            rotate = math.pi / 2 if start_pos[1] > end_pos[1] else -math.pi / 2
        else:
            rotate = 0

        upper_rec_out = gdspy.Rectangle((pos[0] - width / 2, pos[1] + upper_height + gap / 2),
                                        (pos[0] + width / 2, pos[1] + gap / 2))
        upper_rec_in = gdspy.Rectangle(
            (pos[0] - width / 2 + metal_width, pos[1] + upper_height - metal_width + gap / 2),
            (pos[0] + width / 2 - metal_width, pos[1] + gap / 2))
        upper_rec = gdspy.boolean(upper_rec_out, upper_rec_in, "not")

        lower_rec_out = gdspy.Rectangle((pos[0] - width / 2, pos[1] - gap / 2),
                                        (pos[0] + width / 2, pos[1] - lower_height - gap / 2))
        lower_rec_in = gdspy.Rectangle((pos[0] - width / 2 + metal_width, pos[1] - gap / 2), (
        pos[0] + width / 2 - metal_width, pos[1] - lower_height + metal_width - gap / 2))
        lower_rec = gdspy.boolean(lower_rec_out, lower_rec_in, "not")

        rec = gdspy.boolean(upper_rec, lower_rec, "or")

        claw1 = gdspy.Rectangle((pos[0] - width / 2 - claw_width, pos[1] + gap / 2 + claw_height),
                                (pos[0] - width / 2, pos[1] + gap / 2))
        claw2 = gdspy.Rectangle((pos[0] - width / 2 - claw_width, pos[1] - claw_height - gap / 2),
                                (pos[0] - width / 2, pos[1] - gap / 2))
        claw_left = gdspy.boolean(claw1, claw2, "or")

        claw3 = gdspy.Rectangle((pos[0] + width / 2, pos[1] + gap / 2 + claw_height),
                                (pos[0] + width / 2 + claw_width, pos[1] + gap / 2))
        claw4 = gdspy.Rectangle((pos[0] + width / 2, pos[1] - claw_height - gap / 2),
                                (pos[0] + width / 2 + claw_width, pos[1] - gap / 2))
        claw_right = gdspy.boolean(claw3, claw4, "or")
        claw = gdspy.boolean(claw_left, claw_right, "or")

        coupler = gdspy.boolean(rec, claw, "or")
        coupler.rotate(rotate, center=pos)

        self.cell.add(coupler)

        return