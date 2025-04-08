############################################################################################
# File Name: charge_line1.py
# Description: This file primarily contains the construction code for the ChargeLine1.
############################################################################################
import gdspy
import math
from base.library_base import LibraryBase
from addict import Dict

class ChargeLine1(LibraryBase):
    """
    ChargeLine1 class for creating charge line 1 structures.

    Attributes:
        default_options: Dict, containing default parameters for the charge line 1.
    """
    default_options = Dict(
        # Framework
        name="charge_line0",
        type="ChargeLine1",
        chip="chip0",
        outline=[],
        # Geometric parameters
        path=[[0, 0],[0, 100]],
        width=15,
        gap=5,
        pad_width=15,
        pad_height=25,
        distance=50,
        corner_radius=20
    )

    def __init__(self, options: Dict=None):
        """
        Initializes the ChargeLine1 class.

        Input:
            options: Dict, user-defined parameters for the charge line 1.

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
        Draws the geometric shape of the ChargeLine1 and adds it to the GDS cell.

        Output:
            None.
        """
        """
        Generate and return the polygons representing the readout line and pad.

        Returns:
            List[gdspy.Polygon]: List containing the polygons representing the readout line and pad.
        """
        self.lib = gdspy.GdsLibrary()
        gdspy.library.use_current_library = False
        corner_radius = self.corner_radius

        self.cell_extract = self.lib.new_cell(self.name + "_extract")
        self.cell_subtract = self.lib.new_cell(self.name + "_subtract")

        control_L_out = gdspy.FlexPath(self.path, self.width + self.gap * 2, corners="circular bend", bend_radius=corner_radius).to_polygonset()
        self.cell_extract.add(control_L_out)

        pad_height = self.pad_height
        pos = self.path
        width = self.width

        d = math.sqrt((pos[-1][1] - pos[-2][1])**2 + (pos[-1][0] - pos[-2][0])**2)
        pos[-1] = (pos[-1][0] - (pad_height / d) * (pos[-1][0] - pos[-2][0]), pos[-1][1] - (pad_height / d) * (pos[-1][1] - pos[-2][1]))

        control_L_inner = gdspy.FlexPath(pos, width, corners="circular bend", bend_radius=corner_radius).to_polygonset()
        self.cell_subtract.add(control_L_inner)

        pad = gdspy.boolean(self.cell_extract, self.cell_subtract, "not")
        self.cell = self.lib.new_cell(self.name + "_cell")
        self.cell.add(pad)

        return