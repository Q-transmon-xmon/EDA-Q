############################################################################################
# File Name: rec_chip_two.py
# Description: This file primarily contains the construction code for the RecChipTwo (two rectangular chips).
############################################################################################
from addict import Dict
import gdspy, copy
from base.library_base import LibraryBase
import toolbox

class RecChipTwo(LibraryBase):
    """
    RecChipTwo class for creating two rectangular chip structures.

    Attributes:
        default_options: Dict, containing default parameters for two rectangular chips.
    """
    default_options = Dict(
        # Framework
        name="chip0",
        type="RecChipTwo",
        # Geometric parameters
        start_pos0=(0, 0),
        end_pos0=(500, 500),
        start_pos1=(1000, 0),
        end_pos1=(1500, 500)
    )

    def __init__(self, options: Dict=None):
        """
        Initializes the RecChipTwo class.

        Input:
            options: Dict, user-defined parameters for two rectangular chips.

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
        Draws the geometric shape of the RecChipTwo and adds it to the GDS cell.

        Output:
            None.
        """
        gdspy.library.use_current_library = False
        self.lib = gdspy.GdsLibrary()
        self.cell = self.lib.new_cell(self.name)

        # Interface
        start_pos0 = copy.deepcopy(self.start_pos0)
        end_pos0 = copy.deepcopy(self.end_pos0)
        start_pos1 = copy.deepcopy(self.start_pos1)
        end_pos1 = copy.deepcopy(self.end_pos1)
        # Create four segments to form a rectangle
        path0 = gdspy.Path(1, start_pos0)
        path0.segment(end_pos0[0] - start_pos0[0], "+x")
        path0.segment(end_pos0[1] - start_pos0[1], "+y")
        path0.segment(end_pos0[0] - start_pos0[0], "-x")
        path0.segment(end_pos0[1] - start_pos0[1], "-y")

        path1 = gdspy.Path(1, start_pos1)
        path1.segment(end_pos1[0] - start_pos1[0], "+x")
        path1.segment(end_pos1[1] - start_pos1[1], "+y")
        path1.segment(end_pos1[0] - start_pos1[0], "-x")
        path1.segment(end_pos1[1] - start_pos1[1], "-y")

        self.cell.add(path0)
        self.cell.add(path1)
        return