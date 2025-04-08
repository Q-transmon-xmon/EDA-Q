############################################################################################
# File Name: charge_line.py
# Description: This file primarily contains the construction code for the ChargeLine.
############################################################################################
import gdspy
import math
from base.library_base import LibraryBase
from addict import Dict

class ChargeLine(LibraryBase):
    """
    ChargeLine class for creating charge line structures.

    Attributes:
        default_options: Dict, containing default parameters for the charge line.
    """
    default_options = Dict(
        # Framework
        name="charge_line0",
        type="ChargeLine",
        chip="chip0",
        outline=[],
        # Geometric parameters
        pos=[[0, 0],[0, 100]],
        width=15,
        gap=5,
        pad_width=15,
        pad_height=25,
        distance=50,
        corner_radius=20
    )

    def __init__(self, options: Dict=None):
        """
        Initializes the ChargeLine class.

        Input:
            options: Dict, user-defined parameters for the charge line.

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
        # self.outline = [...]
        return

    def draw_gds(self):
        """
        Draws the geometric shape of the ChargeLine and adds it to the GDS cell.

        Output:
            None.
        """
        self.lib = gdspy.GdsLibrary()
        gdspy.library.use_current_library = False
        corner_radius = self.corner_radius

        self.cell_extract = self.lib.new_cell(self.name + "_extract")
        self.cell_subtract = self.lib.new_cell(self.name + "_subtract")

        control_L_out = gdspy.FlexPath(self.pos, self.width + self.gap * 2, corners="circular bend", bend_radius=corner_radius).to_polygonset()
        self.cell_extract.add(control_L_out)

        d = math.sqrt((self.pos[-1][1] - self.pos[-2][1])**2 + (self.pos[-1][0] - self.pos[-2][0])**2)
        self.pos[-1] = (self.pos[-1][0] - (self.pad_height / d) * (self.pos[-1][0] - self.pos[-2][0]), self.pos[-1][1] - (self.pad_height / d) * (self.pos[-1][1] - self.pos[-2][1]))

        control_L_inner = gdspy.FlexPath(self.pos, self.width, corners="circular bend", bend_radius=corner_radius).to_polygonset()
        self.cell_subtract.add(control_L_inner)

        pad = gdspy.boolean(self.cell_extract, self.cell_subtract, "not")
        self.cell = self.lib.new_cell(self.name + "_cell")
        self.cell.add(pad)

        return