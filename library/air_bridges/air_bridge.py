############################################################################################
# File Name: air_bridge.py
# Description: This file primarily contains the construction code for air bridges.
############################################################################################
import gdspy, copy
from addict import Dict
import math as mt
from base.library_base import LibraryBase


class AirBridge(LibraryBase):
    """
    AirBridge class for creating air bridge structures.

    Attributes:
        default_options: Dict, containing default air bridge parameters.
    """
    default_options = Dict(
        # Framework
        name="AirBridge0",
        type="AirBridge",
        chip="chip0",
        outline=[],
        # Geometric parameters
        center_pos=(0, 0),
        width=10,
        height=60,
        rotation=0
    )

    def __init__(self, options: Dict = None):
        """
        Initializes the AirBridge class.

        Input:
            options: Dict, user-defined air bridge parameters.

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
        Draws the geometric shape of the AirBridge and adds it to the GDS cell.

        Output:
            None.
        """
        # Interface
        name = self.name
        center_pos = copy.deepcopy(self.center_pos)
        rotation = self.rotation
        width = self.width
        height = self.height

        # Drawing
        self.lib = gdspy.GdsLibrary()
        gdspy.library.use_current_library = False
        self.cell = self.lib.new_cell(self.name + "_cell")

        air = gdspy.Rectangle((center_pos[0] - width / 2, center_pos[1] - height / 2),
                              (center_pos[0] + width / 2, center_pos[1] + height / 2), layer=1)
        air.rotate(rotation, center_pos)
        self.cell.add(air)
        return