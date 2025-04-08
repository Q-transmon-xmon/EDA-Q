############################################################################################
# File Name: zline_nju.py
# Description: This file primarily contains the code for constructing Z-line NJU structures.
############################################################################################

import gdspy
import math, copy
import numpy as np
from addict import Dict
from base.library_base import LibraryBase


class ZlineNju(LibraryBase):
    default_options = Dict(
        # Framework
        name="ZlineNJU0",
        type="ZlineNJU",
        chip="chip0",
        line_init_pos=[(0, 0), (500, 0), (500, -1000), (1000, -1000), (1000, 0)],
        line_end_pos=[(1000, 800), (1200, 1000), (1200, 1200)],
        width=[15, 10],
        gap=[5, 4],
        short_width=12,
        short_height=4,
        long_short_gap=4,
        long_width_left=24,
        long_width_right=12,
        long_height=2,
        buffer_length=100,
        corner_radius=[20, 200],
        mirror=False,
    )

    def __init__(self, options=Dict()):
        """
        Initializes an instance of the ZlineNju class.

        Input:
            options: Dict, containing custom option parameters.
        """
        super().__init__(options)
        return

    def calc_general_ops(self):
        """
        Requires calculating the following parameters:
        - readout_pins
        - control_pins
        - coupling_pins
        - outline
        """
        return

    def draw_gds(self):
        """
        Draws the geometric shape of the Z-line NJU and adds it to the GDS cell.
        """
        ################################ gdspy Variables ################################
        self.lib = gdspy.GdsLibrary()
        gdspy.library.use_current_library = False
        self.cell = self.lib.new_cell(self.name + "_cell")

        ################################ Interface ################################
        # The purpose of the interface is to facilitate subsequent user parameter updates.
        # Users can update the interface only, and the code below the interface remains unchanged.
        # Framework

        line_init_pos = self.options.line_init_pos
        line_end_pos = self.options.line_end_pos
        width = self.options.width
        gap = self.options.gap
        short_width = self.options.short_width
        short_height = self.options.short_height
        long_short_gap = self.options.long_short_gap
        long_width_left = self.options.long_width_left
        long_width_right = self.options.long_width_right
        long_height = self.options.long_height
        buffer_length = self.options.buffer_length
        corner_radius = self.options.corner_radius
        mirror = self.options.mirror

        ################################ Parameter Conversion ################################
        # This module exists to reconcile the contradiction between user convenience and developer convenience.
        # It converts user-friendly parameter sets into parameter sets convenient for drawing.
        if line_init_pos[-1][0] == line_end_pos[0][0]:
            buffer_end_pos = (line_init_pos[-1][0], line_init_pos[-1][1] + buffer_length)
        else:
            buffer_end_pos = (line_init_pos[-1][0] + buffer_length, line_init_pos[-1][1])

        line_end_pos.insert(0, buffer_end_pos)

        line_init_out = gdspy.FlexPath(line_init_pos, width=width[0] + gap[0] * 2, corners="circular bend",
                                       bend_radius=corner_radius[0]).to_polygonset()
        line_init_in = gdspy.FlexPath(line_init_pos, width=width[0], corners="circular bend",
                                      bend_radius=corner_radius[0]).to_polygonset()
        line_init = gdspy.boolean(line_init_out, line_init_in, "not")

        buffer_out = gdspy.Path(width[0] + gap[0] * 2, line_init_pos[-1])
        buffer_out.segment(buffer_length, direction=np.arctan2(line_end_pos[0][1] - line_init_pos[-1][1],
                                                               line_end_pos[0][0] - line_init_pos[-1][0]),
                           final_width=(width[1] + gap[1] * 2))

        buffer_in = gdspy.Path(width[0], line_init_pos[-1])
        buffer_in.segment(buffer_length, direction=np.arctan2(line_end_pos[0][1] - line_init_pos[-1][1],
                                                              line_end_pos[0][0] - line_init_pos[-1][0]),
                          final_width=width[1])

        line_buffer = gdspy.boolean(buffer_out, buffer_in, "not")

        line_end_out = gdspy.FlexPath(line_end_pos, width=width[1] + gap[1] * 2, corners="circular bend",
                                      bend_radius=corner_radius[1])
        line_end_in = gdspy.FlexPath(line_end_pos, width=width[1], corners="circular bend",
                                     bend_radius=corner_radius[1])
        line_end = gdspy.boolean(line_end_out, line_end_in, "not")

        line = gdspy.boolean(line_init, line_buffer, "or")
        line = gdspy.boolean(line, line_end, "or")

        ################################ Drawing ################################
        end_pos = line_end_pos[-1]
        offset = (width[1] + gap[1]) / 2
        if not mirror:
            short_rec = gdspy.Rectangle((end_pos[0] - offset - short_width / 2, end_pos[1]),
                                        (end_pos[0] - offset + short_width / 2, end_pos[1] + short_height))
            connection_rec = gdspy.Rectangle((end_pos[0] + width[1] / 2, end_pos[1]), (
            end_pos[0] + width[1] / 2 + gap[1], end_pos[1] + short_height + long_short_gap))
            long_rec = gdspy.Rectangle(
                (end_pos[0] + offset - long_width_left, end_pos[1] + short_height + long_short_gap),
                (end_pos[0] + offset + long_width_right, end_pos[1] + short_height + long_short_gap + long_height))
        else:
            short_rec = gdspy.Rectangle((end_pos[0] + offset - short_width / 2, end_pos[1]),
                                        (end_pos[0] + offset + short_width / 2, end_pos[1] + short_height))
            connection_rec = gdspy.Rectangle((end_pos[0] - width[1] / 2, end_pos[1]), (
            end_pos[0] - width[1] / 2 - gap[1], end_pos[1] + short_height + long_short_gap))
            long_rec = gdspy.Rectangle(
                (end_pos[0] - offset - long_width_right, end_pos[1] + short_height + long_short_gap),
                (end_pos[0] - offset + long_width_left, end_pos[1] + short_height + long_short_gap + long_height))

        rec = gdspy.boolean(short_rec, connection_rec, "or")
        rec = gdspy.boolean(rec, long_rec, "or")
        zline_nju = gdspy.boolean(line, rec, "or")

        self.cell.add(zline_nju)

        return