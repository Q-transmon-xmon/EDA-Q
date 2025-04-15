############################################################################################
# File Name: zline.py
# Description: This file primarily contains the code for constructing Z-lines.
############################################################################################

import gdspy, copy
from addict import Dict
import math
from base.library_base import LibraryBase


class Zline(LibraryBase):
    default_options = Dict(
        # Framework
        name="zline0",
        type="Zline",
        pos=(0, 0),
        width=10,
        chip="chip0",
        gap=6,
        length=300,
        length1=50,
        length2=100,
        length3=100,
        orientation=90
    )

    def __init__(self, options: Dict = None):
        """
        Initializes an instance of the Zline class.

        Input:
            options: Dict, containing custom option parameters.
        """
        super().__init__(options)
        return

    def calc_general_ops(self):
        """
        Placeholder function for calculating general operations.
        """
        return

    def draw_gds(self):
        """
        Draws the geometric shape of the Z-line and adds it to the GDS cell.
        """
        # Drawing
        self.lib = gdspy.GdsLibrary()
        gdspy.library.use_current_library = False
        self.cell = self.lib.new_cell(self.name + "_cell")

        pos = self.pos
        width = self.gap
        gap = self.width
        length = self.length
        length1 = self.length1
        length2 = self.length2
        length3 = self.length3
        orientation = self.orientation - 90

        length4 = length + width + gap

        # Create rectangles
        rect1 = gdspy.Rectangle(
            [-(length2 - gap / 2) + pos[0], length4 + pos[1]],
            [gap / 2 + width + length3 + pos[0], length4 + width + pos[1]]
        )

        rect2 = gdspy.Rectangle(
            [gap / 2 + width + pos[0], length4 + width + pos[1]],
            [gap / 2 + pos[0], pos[1]]
        )

        rect_large = gdspy.boolean(rect1, rect2, 'or')

        rect3 = gdspy.Rectangle(
            [-(gap / 2 + length1) + pos[0], length + pos[1]],
            [-gap / 2 + pos[0], length + width + pos[1]]
        )

        rect4 = gdspy.Rectangle(
            [-(gap / 2 + width) + pos[0], pos[1]],
            [-gap / 2 + pos[0], length + width + pos[1]]
        )

        rect_little = gdspy.boolean(rect3, rect4, 'or')
        rect = gdspy.boolean(rect_large, rect_little, 'or')

        rect.rotate(math.pi * orientation / 180, pos)

        self.cell.add(rect)