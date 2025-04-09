#########################################################################
# File Name: xmon_nju.py
# Description: Defines the XmonNju class, which is used to draw the geometric structure of superconducting qubits 
#              and generate elements in the GDS design database.
#              Includes qubit parameter settings, pin calculations, and geometric shape drawing functions.
#########################################################################
from addict import Dict
from base.library_base import LibraryBase
import toolbox
import copy, gdspy, numpy as np

class XmonNju(LibraryBase):
    default_options = Dict(
        # Framework
        name = "q0",
        type = "XmonJJ",
        gds_pos = (0, 0),
        topo_pos = (0, 0),
        chip = "chip0",
        readout_pins = [],
        control_pins = [],
        coupling_pins = [],
        outline = [],
        orientation = 0,
        # Cross out
        cross_out_row_width=72,
        cross_out_row_length=328,
        cross_out_col_width=72,
        cross_out_col_length=383,

        # Cross in
        cross_in_row_width=24,
        cross_in_row_length=336,
        cross_in_col_width=24,
        cross_in_col_length=343,

        ## Pad
        pad_options = [1,1,1,1], # Corresponds to top, bottom, left, right respectively
        pad_out_height = [249, 249, 80, 80],
        pad_out_width = [350, 350, 38, 38],
        pad_in_height = [201, 201, 32, 32],
        pad_in_width = [260, 260, 24, 24],
        # pad_top_width = 18, # Width of the top connection
        # pad_bottom_width = 15, # Width of the bottom metal surface


        ## Claw
        claw_options=[1,1,1,1],
        claw_width = 143,
        claw_height = 133,
        claw_small_width = 85,
        claw_small_height = 118,
        claw_gap = 5,
        claw_dist = 4,
        claw_connection = 10,
        
        ## JJ
        jj_chip = "Josephson Junction",

        # Pad offset is the distance relative to the cross in boundary
        jj_pad0_offset = 1,
        jj_pad0_width = 6,
        jj_pad0_height = 7,
        jj_connection0_width = 3.7,
        jj_connection0_height = 0.6,
        jj_stick0_width = 3.55,
        jj_stick0_height = 0.18,
        jj_stick0_offset = 6, # Distance from the connection to the stick alignment relative to the pad top

        jj_pad1_offset = 9, 
        jj_pad1_width = 6,
        jj_pad1_height = 7,
        jj_connection1_width= 0.6,
        jj_connection1_height = 2, 
        jj_stick1_width = 0.18,
        jj_stick1_height = 3.6,
        jj_stick1_offset = 3.3, # Distance from the connection to the stick alignment relative to the pad left

        jj_pad2_offset = 9, 
        jj_pad2_width = 6,
        jj_pad2_height = 7,
        jj_connection2_width = 0.6,
        jj_connection2_height = 2,
        jj_stick2_width = 0.18,
        jj_stick2_height = 3.6,
        jj_stick2_offset = 3.3, # Distance from the connection to the stick alignment relative to the pad right

        ## Hole
        hole0_width0 = 2,
        hole0_height0 = 4,
        hole0_width1 = 6,
        hole0_height1 = 2,

        hole1_width0 = 5,
        hole1_height0 = 2,
        hole1_width1 = 2,
        hole1_height1 = 4,

        hole2_width0 = 5,
        hole2_height0 = 2,
        hole2_width1 = 2,
        hole2_height1 = 4,
    )
    
    def __init__(self, options = Dict()):
        """
        Initializes the XmonNju class.
        
        Input:
            options: Dictionary containing component parameter options.
        """
        super().__init__(options)
        return
    
    def calc_general_ops(self):
        """
        Need to calculate the following parameters:
        readout_pins
        control_pins
        coupling_pins
        outline
        """
        return

    def draw_gds(self):
        """
        Draws the geometric shapes of the qubit and adds them to the GDS cell.
        """
        ################################ gdspy variables ################################
        # Do not modify this section of code
        gdspy.library.use_current_library = False
        self.lib = gdspy.GdsLibrary()
        self.cell = self.lib.new_cell(self.name)
        self.jj_cell = self.lib.new_cell(self.name+"_jj")
        ################################ Interface ################################
        # The purpose of the interface is to facilitate subsequent user parameter updates. 
        # Users can update the interface only, and the code below the interface does not need to be modified.
        # Framework
        name = self.name
        gds_pos = self.gds_pos
        orientation = self.orientation
        # Cross out
        cross_out_row_width = self.cross_out_row_width
        cross_out_row_length = self.cross_out_row_length
        cross_out_col_width = self.cross_out_col_width
        cross_out_col_length = self.cross_out_col_length
        # Cross in
        cross_in_row_width = self.cross_in_row_width
        cross_in_row_length = self.cross_in_row_length
        cross_in_col_width = self.cross_in_col_width
        cross_in_col_length = self.cross_in_col_length
        # Pad 
        pad_options = self.pad_options
        pad_out_height = self.pad_out_height
        pad_out_width = self.pad_out_width
        pad_in_height = self.pad_in_height
        pad_in_width = self.pad_in_width
        # Claw
        claw_options = self.claw_options
        claw_width = self.claw_width
        claw_height = self.claw_height
        claw_small_width = self.claw_small_width
        claw_small_height = self.claw_small_height
        claw_gap = self.claw_gap
        claw_connection = self.claw_connection
        claw_dist = self.claw_dist

        ## JJ
        jj_pad0_offset = self.jj_pad0_offset
        jj_pad0_width = self.jj_pad0_width
        jj_pad0_height = self.jj_pad0_height
        jj_connection0_width = self.jj_connection0_width
        jj_connection0_height = self.jj_connection0_height
        jj_stick0_width = self.jj_stick0_width
        jj_stick0_height = self.jj_stick0_height
        jj_stick0_offset = self.jj_stick0_offset

        jj_pad1_offset = self.jj_pad1_offset
        jj_pad1_width = self.jj_pad1_width
        jj_pad1_height = self.jj_pad1_height
        jj_connection1_width = self.jj_connection1_width
        jj_connection1_height = self.jj_connection1_height
        jj_stick1_width = self.jj_stick1_width
        jj_stick1_height = self.jj_stick1_height
        jj_stick1_offset = self.jj_stick1_offset

        jj_pad2_offset = self.jj_pad2_offset
        jj_pad2_width = self.jj_pad2_width
        jj_pad2_height = self.jj_pad2_height
        jj_connection2_width = self.jj_connection2_width
        jj_connection2_height = self.jj_connection2_height
        jj_stick2_width = self.jj_stick2_width
        jj_stick2_height = self.jj_stick2_height
        jj_stick2_offset = self.jj_stick2_offset

        ## Hole
        hole0_width0 = self.hole0_width0
        hole0_height0 = self.hole0_height0
        hole0_width1 = self.hole0_width1
        hole0_height1 = self.hole0_height1

        hole1_width0 = self.hole1_width0
        hole1_height0 = self.hole1_height0
        hole1_width1 = self.hole1_width1
        hole1_height1 = self.hole1_height1

        hole2_width0 = self.hole2_width0
        hole2_height0 = self.hole2_height0
        hole2_width1 = self.hole2_width1
        hole2_height1 = self.hole2_height1
        ################################ Parameter Conversion ################################
        # This module exists to reconcile the contradiction between user convenience and developer convenience.
        # It can convert a set of user-friendly parameters into a set of parameters that are convenient for drawing.
        # For example:
        # claw_width0 = self.claw_width
        # claw_height0 = self.claw_height
        # claw_width1 = self.claw_width - 2*self.claw_small_width
        # claw_height1 = self.claw_height - self.claw_small_height
        claw_pos_options = [(gds_pos[0], gds_pos[1] + cross_out_col_length/2 + 0.5 * claw_gap + claw_dist + claw_height - claw_small_height),
                    (gds_pos[0], gds_pos[1] - cross_out_col_length/2 - 0.5 * claw_gap - claw_dist - claw_height + claw_small_height),
                    (gds_pos[0] - cross_out_row_length/2 - 0.5 * claw_gap - claw_dist - claw_width + claw_small_width, gds_pos[1]),
                    (gds_pos[0] + cross_out_row_length/2 + 0.5 * claw_gap + claw_dist + claw_width - claw_small_width, gds_pos[1])]
        # Then, in the drawing section, draw two rectangles and subtract the two shapes to get the claw prototype (excluding gap)
        ################################ Drawing ##################################
        # Add your code here

        # Draw cross structure
        row_out = gdspy.Rectangle(
            (gds_pos[0] - cross_out_row_length / 2, gds_pos[1] - cross_out_row_width / 2 ),
            (gds_pos[0] + cross_out_row_length / 2, gds_pos[1] + cross_out_row_width / 2)
        )
        col_out = gdspy.Rectangle(
            (gds_pos[0] - cross_out_col_width / 2, gds_pos[1] - cross_out_col_length / 2),
            (gds_pos[0] + cross_out_col_width / 2, gds_pos[1] + cross_out_col_length / 2)
        )
        if(pad_options[2] == 1):
            pad_left = gdspy.Rectangle(
                (gds_pos[0] - cross_out_row_length / 2 - pad_out_width[2], gds_pos[1]  - pad_out_height[2] / 2),
                (gds_pos[0] - cross_out_row_length / 2, gds_pos[1] + pad_out_height[2] / 2)
            )
        if(pad_options[3] == 1):
            pad_right = gdspy.Rectangle(
                (gds_pos[0] + cross_out_row_length / 2, gds_pos[1] - pad_out_height[3] / 2),
                (gds_pos[0] + cross_out_row_length / 2 + pad_out_width[3], gds_pos[1] + pad_out_height[3] / 2)
            )
        cross_out = gdspy.boolean(row_out, col_out, 'or')
        pad_row_out = gdspy.boolean(pad_left, pad_right, 'or')
        cross_pad_out = gdspy.boolean(cross_out, pad_row_out, 'or')

        row_in = gdspy.Rectangle(
            (gds_pos[0] - cross_in_row_length / 2, gds_pos[1] - cross_in_row_width / 2),
            (gds_pos[0] + cross_in_row_length / 2, gds_pos[1] + cross_in_row_width / 2)
        )
        col_in = gdspy.Rectangle(
            (gds_pos[0] - cross_in_col_width / 2, gds_pos[1] - cross_in_col_length / 2),
            (gds_pos[0] + cross_in_col_width / 2, gds_pos[1] + cross_in_col_length / 2)
        )
        if(pad_options[2] == 1):
            pad_left = gdspy.Rectangle(
                (gds_pos[0] - cross_in_row_length / 2 - pad_in_width[2], gds_pos[1]  - pad_in_height[2] / 2),
                (gds_pos[0] - cross_in_row_length / 2, gds_pos[1] + pad_in_height[2] / 2)
            )
        if(pad_options[3] == 1):
            pad_right = gdspy.Rectangle(
                (gds_pos[0] + cross_in_row_length / 2, gds_pos[1] - pad_in_height[3] / 2),
                (gds_pos[0] + cross_in_row_length / 2 + pad_in_width[3], gds_pos[1] + pad_in_height[3] / 2)
            )
        cross_in = gdspy.boolean(row_in, col_in, 'or')
        pad_row_in = gdspy.boolean(pad_left, pad_right, 'or')
        cross_pad_in = gdspy.boolean(cross_in, pad_row_in, 'or')

        cross_pad = gdspy.boolean(cross_pad_out, cross_pad_in, 'not')
        self.cell.add(cross_pad)

        # Draw hole structure
        hole0_top = gdspy.Rectangle(
            (gds_pos[0] - hole0_width0 / 2, gds_pos[1] - cross_in_col_length / 2),
            (gds_pos[0] + hole0_width0 / 2, gds_pos[1] - cross_in_col_length / 2 - hole0_height0))
        hole0_bottom = gdspy.Rectangle(
            (gds_pos[0] - hole0_width1 / 2, gds_pos[1] - cross_in_col_length / 2 - hole0_height0),
            (gds_pos[0] + hole0_width1 / 2, gds_pos[1] - cross_in_col_length / 2 - hole0_height0 - hole0_height1))
        hole0 = gdspy.boolean(hole0_top, hole0_bottom, 'or')

        hole1_top = gdspy.Rectangle(
            (gds_pos[0] - cross_in_col_width / 2, gds_pos[1] - cross_out_col_length / 2 + hole1_height0 + hole1_height1),
            (gds_pos[0] - cross_in_col_width / 2 + hole1_width0, gds_pos[1] - cross_out_col_length / 2 + hole1_height1))
        hole1_bottom = gdspy.Rectangle(
            (gds_pos[0] - cross_in_col_width / 2 + hole1_width0 - hole1_width1, gds_pos[1] - cross_out_col_length / 2 + hole1_height1),
            (gds_pos[0] - cross_in_col_width / 2 + hole1_width0, gds_pos[1] - cross_out_col_length / 2))
        hole1 = gdspy.boolean(hole1_top, hole1_bottom, 'or')

        hole2_top = gdspy.Rectangle(
            (gds_pos[0] + cross_in_col_width / 2, gds_pos[1] - cross_out_col_length / 2 + hole2_height0 + hole2_height1),
            (gds_pos[0] + cross_in_col_width / 2 - hole2_width0, gds_pos[1] - cross_out_col_length / 2 + hole2_height1))
        hole2_bottom = gdspy.Rectangle(
            (gds_pos[0] + cross_in_col_width / 2 - hole2_width0 + hole2_width1, gds_pos[1] - cross_out_col_length / 2 + hole2_height1),
            (gds_pos[0] + cross_in_col_width / 2 - hole2_width0, gds_pos[1] - cross_out_col_length / 2))
        hole2 = gdspy.boolean(hole2_top, hole2_bottom, 'or')

        cross_pad = gdspy.boolean(cross_pad, hole0, 'not')
        cross_pad = gdspy.boolean(cross_pad, hole1, 'not')
        cross_pad = gdspy.boolean(cross_pad, hole2, 'not')

        self.cell.add(cross_pad)

        # Draw claw structure
        claw_pos = claw_pos_options[0]
        claw_top = gdspy.FlexPath([(claw_pos[0] - claw_connection / 2 - claw_gap / 2, claw_pos[1]),
                                    (claw_pos[0] - claw_width / 2, claw_pos[1]),
                                    (claw_pos[0] - claw_width / 2, claw_pos[1] - claw_height),
                                    (claw_pos[0] - claw_small_width / 2, claw_pos[1] - claw_height),
                                    (claw_pos[0] - claw_small_width / 2, claw_pos[1] - 0.5 * claw_gap - claw_height + claw_small_height + claw_dist),
                                    (claw_pos[0] + claw_small_width / 2, claw_pos[1] - 0.5 * claw_gap - claw_height + claw_small_height + claw_dist),
                                    (claw_pos[0] + claw_small_width / 2, claw_pos[1] - claw_height),
                                    (claw_pos[0] + claw_width / 2, claw_pos[1] - claw_height),
                                    (claw_pos[0] + claw_width / 2, claw_pos[1]),
                                    (claw_pos[0] + claw_connection / 2 + claw_gap / 2, claw_pos[1])],claw_gap, layer=1).to_polygonset()
        self.cell.add(claw_top)

        # Draw JJ structure
        JJ_pos0 = (gds_pos[0], gds_pos[1] - cross_in_col_length / 2 + jj_pad0_offset)
        JJ_pad0 = gdspy.Rectangle((JJ_pos0[0] - jj_pad0_width / 2, JJ_pos0[1]), 
                                  (JJ_pos0[0] + jj_pad0_width / 2, JJ_pos0[1] - jj_pad0_height))
        JJ_connection0_left = gdspy.Rectangle((JJ_pos0[0] - jj_pad0_width / 2 - jj_connection0_width, JJ_pos0[1] - jj_stick0_offset + jj_connection0_height), 
                                          (JJ_pos0[0] - jj_pad0_width / 2, JJ_pos0[1] - jj_stick0_offset))
        JJ_stick0_left = gdspy.Rectangle((JJ_pos0[0] - jj_pad0_width / 2 - jj_connection0_width - jj_stick0_width, JJ_pos0[1] - jj_stick0_offset), 
                                     (JJ_pos0[0] - jj_pad0_width / 2 - jj_connection0_width, JJ_pos0[1] - jj_stick0_offset + jj_stick0_height))
        JJ_connection0_right = gdspy.Rectangle((JJ_pos0[0] + jj_pad0_width / 2, JJ_pos0[1] - jj_stick0_offset + jj_connection0_height), 
                                           (JJ_pos0[0] + jj_pad0_width / 2 + jj_connection0_width, JJ_pos0[1] - jj_stick0_offset))
        JJ_stick0_right = gdspy.Rectangle((JJ_pos0[0] + jj_pad0_width / 2 + jj_connection0_width, JJ_pos0[1] - jj_stick0_offset), 
                                      (JJ_pos0[0] + jj_pad0_width / 2 + jj_connection0_width + jj_stick0_width, JJ_pos0[1] - jj_stick0_offset + jj_stick0_height))
        JJ_connection0 = gdspy.boolean(JJ_connection0_left, JJ_connection0_right, 'or')
        JJ_stick0 = gdspy.boolean(JJ_stick0_left, JJ_stick0_right, 'or')
        JJ_connection0_stick0 = gdspy.boolean(JJ_stick0, JJ_connection0, 'or')
        JJ0 = gdspy.boolean(JJ_pad0, JJ_connection0_stick0, 'or')

        JJ_pos1 = (gds_pos[0] - cross_in_col_width / 2 + jj_pad1_width / 2, gds_pos[1] - cross_in_col_length / 2 - jj_pad1_offset)
        JJ_pad1 = gdspy.Rectangle((JJ_pos1[0] - jj_pad1_width / 2, JJ_pos1[1] - jj_pad1_height), 
                                  (JJ_pos1[0] + jj_pad1_width / 2, JJ_pos1[1]))
        JJ_connection1 = gdspy.Rectangle((JJ_pos1[0] - jj_pad1_width / 2 + jj_stick1_offset , JJ_pos1[1]), 
                                       (JJ_pos1[0] - jj_pad1_width / 2 + jj_stick1_offset - jj_connection1_width, JJ_pos1[1] + jj_connection1_height))
        JJ_stick1 = gdspy.Rectangle((JJ_pos1[0] - jj_pad1_width / 2 + jj_stick1_offset, JJ_pos1[1]), 
                                    (JJ_pos1[0] - jj_pad1_width / 2 + jj_stick1_offset - jj_stick1_width, JJ_pos1[1] + jj_connection1_height + jj_stick1_height))
        JJ1 = gdspy.boolean(JJ_pad1, JJ_connection1, 'or')
        JJ1 = gdspy.boolean(JJ1, JJ_stick1, 'or')

        JJ_pos2 = (gds_pos[0] + cross_in_col_width / 2 - jj_pad2_width / 2, gds_pos[1] - cross_in_col_length / 2 - jj_pad2_offset)
        JJ_pad2 = gdspy.Rectangle((JJ_pos2[0] - jj_pad2_width / 2, JJ_pos2[1] - jj_pad2_height), 
                                  (JJ_pos2[0] + jj_pad2_width / 2, JJ_pos2[1]))
        JJ_connection2 = gdspy.Rectangle((JJ_pos2[0] + jj_pad2_width / 2 - jj_stick2_offset, JJ_pos2[1]), 
                                       (JJ_pos2[0] + jj_pad2_width / 2 - jj_stick2_offset + jj_connection2_width, JJ_pos2[1] + jj_connection2_height))
        JJ_stick2 = gdspy.Rectangle((JJ_pos2[0] + jj_pad2_width / 2 - jj_stick2_offset, JJ_pos2[1]), 
                                    (JJ_pos2[0] + jj_pad2_width / 2 - jj_stick2_offset + jj_stick2_width , JJ_pos2[1] + jj_connection2_height + jj_stick2_height))
        JJ2 = gdspy.boolean(JJ_pad2, JJ_connection2, 'or')
        JJ2 = gdspy.boolean(JJ2, JJ_stick2, 'or')

        JJ = gdspy.boolean(JJ0, JJ1, 'or')
        JJ = gdspy.boolean(JJ, JJ2, 'or')

        self.jj_cell.add(JJ)

        ########################################################################
        return