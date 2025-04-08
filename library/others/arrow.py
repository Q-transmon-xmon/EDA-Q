############################################################################################
# File Name: arrow.py
# Description: This file defines the construction and drawing functionality for arrow shapes,
#              generating GDS-format geometric shapes.
############################################################################################

import gdspy, copy
from addict import Dict
import math as mt
from base.library_base import LibraryBase


class Arrow(LibraryBase):
    default_options = Dict(
        # Framework
        name="readout1",
        type="Arrow",
        start_pos=[0, 0],
        inclined_length=500,
        outline=[],
        # Geometric parameters
        gap=5,
        width=10,
        height=150,
        inclined_width=10,
        orientation=0
    )

    def __init__(self, options: Dict = None):
        super().__init__(options)
        return

    def calc_general_ops(self):
        return

    def draw_gds(self):
        # Interface
        height = self.height
        width = self.gap
        gap = self.width
        inclined_gap = self.inclined_width
        start_pos = copy.deepcopy(self.start_pos)
        l1 = self.inclined_length
        orientation = self.orientation

        # Drawing
        self.lib = gdspy.GdsLibrary()
        gdspy.library.use_current_library = False
        self.cell = self.lib.new_cell(self.name + "_cell")

        outer_left_rec_right = [start_pos[0] + gap + width * 2, start_pos[1] + height + width * 2]
        inner_left_rec_right = [start_pos[0] + gap + width, start_pos[1] + height + width]
        inner_left_rec_left = [start_pos[0] + width, start_pos[1] + width]

        left_outer_rec = gdspy.Rectangle(start_pos, outer_left_rec_right)
        left_inner_rec = gdspy.Rectangle(inner_left_rec_left, inner_left_rec_right)

        outer_bottom_rec_right = [start_pos[0] + height + width * 2, start_pos[1] + gap + width * 2]
        inner_bottom_rec_left = [start_pos[0] + width, start_pos[1] + width]
        inner_bottom_rec_right = [start_pos[0] + height + width, start_pos[1] + gap + width]

        bottom_outer_rec = gdspy.Rectangle(start_pos, outer_bottom_rec_right)
        bottom_inner_rec = gdspy.Rectangle(inner_bottom_rec_left, inner_bottom_rec_right)

        inner_rec = gdspy.boolean(left_inner_rec, bottom_inner_rec, 'or')
        outer_rec = gdspy.boolean(left_outer_rec, bottom_outer_rec, 'or')

        inner_points = [
            (start_pos[0] + gap + width - inclined_gap * mt.cos(mt.pi / 180 * 45) / 2,
             start_pos[1] + gap + width + inclined_gap * mt.sin(mt.pi / 180 * 45) / 2),
            (start_pos[0] + gap + width - inclined_gap * mt.cos(mt.pi / 180 * 45) / 2 + l1 * mt.cos(mt.pi / 180 * 45),
             start_pos[1] + gap + width + inclined_gap * mt.sin(mt.pi / 180 * 45) / 2 + l1 * mt.sin(mt.pi / 180 * 45)),
            (start_pos[0] + gap + width + inclined_gap * mt.cos(mt.pi / 180 * 45) / 2 + l1 * mt.cos(mt.pi / 180 * 45),
             start_pos[1] + gap + width - inclined_gap * mt.sin(mt.pi / 180 * 45) / 2 + l1 * mt.sin(mt.pi / 180 * 45)),
            (start_pos[0] + gap + width + inclined_gap * mt.cos(mt.pi / 180 * 45) / 2,
             start_pos[1] + gap + width - inclined_gap * mt.sin(mt.pi / 180 * 45) / 2)
        ]

        inner_inclined_rec = gdspy.Polygon(inner_points)

        outer_points = [
            (start_pos[0] + gap + width * 2 - (inclined_gap + width * 2) * mt.cos(mt.pi / 180 * 45) / 2,
             start_pos[1] + gap + width * 2 + (inclined_gap + width * 2) * mt.sin(mt.pi / 180 * 45) / 2),
            (start_pos[0] + gap + width - inclined_gap * mt.cos(mt.pi / 180 * 45) / 2 + l1 * mt.cos(
                mt.pi / 180 * 45) - width * mt.cos(mt.pi / 180 * 45),
             start_pos[1] + gap + width + inclined_gap * mt.sin(mt.pi / 180 * 45) / 2 + l1 * mt.sin(
                 mt.pi / 180 * 45) + width * mt.sin(mt.pi / 180 * 45)),
            (start_pos[0] + gap + width + inclined_gap * mt.cos(mt.pi / 180 * 45) / 2 + l1 * mt.cos(
                mt.pi / 180 * 45) + width * mt.cos(mt.pi / 180 * 45),
             start_pos[1] + gap + width - inclined_gap * mt.sin(mt.pi / 180 * 45) / 2 + l1 * mt.sin(
                 mt.pi / 180 * 45) - width * mt.sin(mt.pi / 180 * 45)),
            (start_pos[0] + gap + width * 2 + (inclined_gap + width * 2) * mt.cos(mt.pi / 180 * 45) / 2,
             start_pos[1] + gap + width * 2 - (inclined_gap + width * 2) * mt.sin(mt.pi / 180 * 45) / 2)
        ]

        outer_inclined_rec = gdspy.Polygon(outer_points)

        inner_rec = gdspy.boolean(inner_rec, inner_inclined_rec, 'or')
        outer_rec = gdspy.boolean(outer_rec, outer_inclined_rec, 'or')
        rec = gdspy.boolean(outer_rec, inner_rec, 'not')

        path = gdspy.Path(width, (start_pos[0] + gap + width + l1 * mt.cos(mt.pi / 180 * 45),
                                  start_pos[1] + gap + width + l1 * mt.sin(mt.pi / 180 * 45)), 2, gap + width)
        path.segment(0, mt.pi / 180 * (45))
        path.turn(50, mt.pi / 180 * 45)

        rec = gdspy.boolean(rec, path, 'or')

        self.end_pos = (
            start_pos[0] + gap + width + l1 * mt.cos(mt.pi / 180 * 45) + 50 - 50 * mt.cos(45 / 180 * mt.pi),
            start_pos[1] + gap + width + l1 * mt.sin(mt.pi / 180 * 45) + 50 * mt.sin(45 / 180 * mt.pi)
        )

        rec.rotate(orientation, start_pos)
        self.cell.add(rec)