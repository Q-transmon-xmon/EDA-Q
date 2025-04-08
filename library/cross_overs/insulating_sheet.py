############################################################################################
# File Name: insulating_sheet.py
# Description: This file defines the InsulatingSheet class for generating the geometric shape
#              of an insulating sheet.
############################################################################################
import gdspy
import math
import numpy as np
from addict import Dict
from base.library_base import LibraryBase


class InsulatingSheet(LibraryBase):
    default_options = Dict(
        # Framework
        name="insulating_sheet0",
        type="InsulatingSheet",
        chip="chip0",
        pos=(0, 0),
        outline=[],
        # Geometric parameters
        height=50,
        width=30,
        orientation=0
    )

    def __init__(self, options: Dict = None):
        """
        Initializes an instance of the InsulatingSheet class.

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
        Generates the polygon representing the insulating sheet and adds it to the GDS cell.

        Returns:
            None: This method directly adds the polygon to the GDS cell.
        """
        self.lib = gdspy.GdsLibrary()
        gdspy.library.use_current_library = False
        self.cell = self.lib.new_cell(self.name)
        x = self.pos[0]
        y = self.pos[1]

        sheet = gdspy.Rectangle((-self.width / 2 + x, self.height / 2 + y),
                                (self.width / 2 + x, -self.height / 2 + y))
        sheet.rotate(math.radians(self.options.orientation), self.options.pos)

        self.cell.add(sheet)

        return