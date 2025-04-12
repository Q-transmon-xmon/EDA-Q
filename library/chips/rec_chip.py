############################################################################################
# File Name: rec_chip.py
# Description: This file primarily contains the construction code for the RecChip (single rectangular chip).
############################################################################################
from addict import Dict
import gdspy, copy
from base.library_base import LibraryBase
import toolbox

class RecChip(LibraryBase):
    """
    RecChip class for creating a single rectangular chip structure.

    Attributes:
        default_options: Dict, containing default parameters for a single rectangular chip.
    """
    default_options = Dict(
        # Framework
        name="chip0",
        type="RecChip",
        # Geometric parameters
        start_pos=(0, 0),
        end_pos=(500, 500)
    )

    def __init__(self, options: Dict=None):
        """
        Initializes the RecChip class.

        Input:
            options: Dict, user-defined parameters for a single rectangular chip.

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
        Draws the geometric shape of the RecChip and adds it to the GDS cell.

        Output:
            None.
        """
        gdspy.library.use_current_library = False
        self.lib = gdspy.GdsLibrary()
        self.cell = self.lib.new_cell(self.name)
        # Create four segments to form a rectangle
        path = gdspy.Path(1, self.start_pos)
        path.segment(self.end_pos[0] - self.start_pos[0], "+x")
        path.segment(self.end_pos[1] - self.start_pos[1], "+y")
        path.segment(self.end_pos[0] - self.start_pos[0], "-x")
        path.segment(self.end_pos[1] - self.start_pos[1], "-y")

        self.cell.add(path)
        return