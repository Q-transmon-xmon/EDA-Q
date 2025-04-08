#########################################################################
# File Name: air_bridge.py
# Description: Defines the AirBridge class for creating air bridge structures.
#              Includes functionality for initializing parameters, calculating general operations,
#              and drawing GDSII files.
#########################################################################

from addict import Dict
from base.library_base import LibraryBase
import toolbox
import copy, gdspy
import numpy as np

class AirBridge(LibraryBase):
    """
    AirBridge class for creating air bridge structures.

    Attributes:
        default_options: Dict, containing default air bridge parameters.
    """
    default_options = Dict(
        # Framework
        name="air_bridge",
        type="AirBridge",
        chips="main",
        qubit=["q0", "q1"],
        outline=[],
        # Geometric parameters
        start_pos=(0, 0),
        end_pos=(2000, 0),
        pad_width=20,
        pad_height=20,
        bridge_width=10
    )

    def __init__(self, options: Dict=None):
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
        Draws the GDSII file.

        Output:
            None.
        """
        self.__gds_library = gdspy.GdsLibrary()
        gdspy.library.use_current_library = False
        self.__cell = self.__gds_library.new_cell(self.default_options.name + "_cell")
        return