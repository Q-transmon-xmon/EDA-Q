#########################################################################
# File Name: transmon_interdigitated.py
# Description: Defines the TransmonInterdigitated class, which is used to draw the geometric structure of a superconducting qubit and generate elements in a GDS design database.
#              Includes qubit parameter settings, pin calculations, and geometric shape drawing functions.
#########################################################################
from addict import Dict
from base.library_base import LibraryBase
import toolbox
import copy, gdspy

class TransmonInterdigitated(LibraryBase):
    default_options = Dict(
        # Framework
        name = "q0",
        type = "Transmon",
        gds_pos = (0, 0),
        topo_pos = (0, 0),
        chip = "chip0",
        readout_pins = [],
        control_pins = [],
        coupling_pins = [],
        outline = [],
        # Dimension parameters
        pad_width=1000,
        pad_height=300,
        finger_width=50,
        finger_height=100,
        finger_space=50,
        comb_width=50,
        comb_space_vert=50,
        comb_space_hor=50,
        jj_width=20,
        cc_space=50,
        cc_width=100,
        cc_height=100,
        cpw_width = 10
    )
    
    def __init__(self, options):
        """
        Initializes the TransmonInterdigitated class.
        
        Input:
            options: Dictionary containing component parameter options.
        """
        super().__init__(options)
        return
    
    def calc_general_ops(self):
        """
        Calculates and generates the coordinates for coupling pins, readout pins, and control pins.
        """
        """
        Generate coupling_pins, readout_pins, control_pins
        self.default_options.coupling_pins.top = ...
        self.default_options.coupling_pins.bot = ...
        self.default_options.coupling_pins.left = ...
        self.default_options.coupling_pins.right = ...
        self.default_options.readout_pins.append(...)    # append contains a coordinate, represented as a list, e.g., [0, 0]
        self.default_options.control_pins.append(...)
        """
        gds_pos = self.default_options.gds_pos
        pad_width=self.default_options.pad_width
        pad_height=self.default_options.pad_height
        finger_width=self.default_options.finger_width
        finger_height=self.default_options.finger_height
        finger_space=self.default_options.finger_space
        comb_width=self.default_options.comb_width
        comb_space_vert=self.default_options.comb_space_vert
        comb_space_hor=self.default_options.comb_space_hor
        jj_width=self.default_options.jj_width
        cc_space=self.default_options.cc_space
        cc_width=self.default_options.cc_width
        cc_height=self.default_options.cc_height
        cpw_width = self.default_options.cpw_width
        width = 1.5*pad_width
        height = 5*pad_height

        self.default_options.readout_pins.append([gds_pos[0]+(width-pad_width)/2+(cc_width)/2,gds_pos[1]+height])    # append contains a coordinate, represented as a list, e.g., [0, 0]
        self.default_options.control_pins.append([gds_pos[0]+(width-pad_width)/2+pad_width-cc_width+(cc_width)/2,gds_pos[1]+height])
        self.default_options.coupling_pins.top = [gds_pos[0]+(width-cc_width)/2+(cc_width)/2,gds_pos[1]+height]
        self.default_options.coupling_pins.bot = [gds_pos[0]+(width-cc_width)/2+(cc_width)/2,gds_pos[1]]
        self.default_options.coupling_pins.left = [gds_pos[0]+(width-pad_width)/2+(cc_width)/2,gds_pos[1]]
        self.default_options.coupling_pins.right = [gds_pos[0]+(width-pad_width)/2+pad_width-cc_width+(cc_width)/2,gds_pos[1]]
        self.default_options.outline = [(gds_pos[0],gds_pos[1]),(gds_pos[0]+width,gds_pos[1]),(gds_pos[0]+width,gds_pos[1]+height),(gds_pos[0],gds_pos[1]+height),(gds_pos[0],gds_pos[1])]
        return

    def draw_gds(self):
        """
        Draws the geometric shapes of the qubit and adds them to the GDS cell.
        """
        # Interface
        gds_pos = self.default_options.gds_pos
        pad_width=self.default_options.pad_width
        pad_height=self.default_options.pad_height
        finger_width=self.default_options.finger_width
        finger_height=self.default_options.finger_height
        finger_space=self.default_options.finger_space
        comb_width=self.default_options.comb_width
        comb_space_vert=self.default_options.comb_space_vert
        comb_space_hor=self.default_options.comb_space_hor
        jj_width=self.default_options.jj_width
        cc_space=self.default_options.cc_space
        cc_width=self.default_options.cc_width
        cc_height=self.default_options.cc_height
        cpw_width = self.default_options.cpw_width
        width = 1.5*pad_width
        height = 5*pad_height
        # Drawing
        self.lib = gdspy.GdsLibrary()
        gdspy.library.use_current_library = False
        self.cell = self.lib.new_cell(self.name)
        # Draw bounding box
        rect = gdspy.Rectangle((gds_pos[0],gds_pos[1]),(gds_pos[0]+width,gds_pos[1]+height))
        all_pad_height = cc_height*2+cc_space*2+pad_height*2+finger_height*2+finger_space
        # Lower large pad coordinates
        left_pad_lower = (gds_pos[0]+(width-pad_width)/2,gds_pos[1]+(height-all_pad_height)/2+cc_height+cc_space)
        right_pad_lower = (gds_pos[0]+(width-pad_width)/2+pad_width,gds_pos[1]+(height-all_pad_height)/2+pad_height+cc_height+cc_space)

        # Upper large pad coordinates
        left_pad_upper = (gds_pos[0]+(width-pad_width)/2,gds_pos[1]+(height-all_pad_height)/2+pad_height+finger_height*2+finger_space+cc_height+cc_space)
        right_pad_upper = (gds_pos[0]+(width-pad_width)/2+pad_width,gds_pos[1]+(height-all_pad_height)/2+pad_height*2+finger_height*2+finger_space+cc_height+cc_space)

        # Comb height
        comb_height = finger_height*2+finger_space-comb_space_vert
        # Distance between the leftmost comb and the edge
        comb_dis = (pad_width-comb_width*9-comb_space_hor*8)/2
        # Lower comb coordinates
        left_comb_lower_1 = (gds_pos[0]+(width-pad_width)/2+comb_dis,gds_pos[1]+(height-all_pad_height)/2+pad_height+cc_height+cc_space)
        right_comb_lower_1 = (gds_pos[0]+(width-pad_width)/2+comb_dis+comb_width,gds_pos[1]+(height-all_pad_height)/2+pad_height+cc_height+cc_space+comb_height)
        left_comb_lower_2 = (gds_pos[0]+(width-pad_width)/2+comb_dis+comb_space_hor*2+comb_width*2,gds_pos[1]+(height-all_pad_height)/2+pad_height+cc_height+cc_space)
        right_comb_lower_2 = (gds_pos[0]+(width-pad_width)/2+comb_dis+comb_space_hor*2+comb_width*3,gds_pos[1]+(height-all_pad_height)/2+pad_height+cc_height+cc_space+comb_height)
        left_comb_lower_3 = (gds_pos[0]+(width-pad_width)/2+comb_dis+comb_space_hor*5+comb_width*5,gds_pos[1]+(height-all_pad_height)/2+pad_height+cc_height+cc_space)
        right_comb_lower_3 = (gds_pos[0]+(width-pad_width)/2+comb_dis+comb_space_hor*5+comb_width*6,gds_pos[1]+(height-all_pad_height)/2+pad_height+cc_height+cc_space+comb_height)
        left_comb_lower_4 = (gds_pos[0]+(width-pad_width)/2+comb_dis+comb_space_hor*7+comb_width*7,gds_pos[1]+(height-all_pad_height)/2+pad_height+cc_height+cc_space)
        right_comb_lower_4 = (gds_pos[0]+(width-pad_width)/2+comb_dis+comb_space_hor*7+comb_width*8,gds_pos[1]+(height-all_pad_height)/2+pad_height+cc_height+cc_space+comb_height)

        # Upper comb coordinates
        left_comb_upper_1 = (gds_pos[0]+(width-pad_width)/2+comb_dis+comb_space_hor+comb_width,gds_pos[1]+(height-all_pad_height)/2+pad_height+cc_height+cc_space+comb_space_vert)
        right_comb_upper_1 = (gds_pos[0]+(width-pad_width)/2+comb_dis+comb_space_hor+comb_width*2,gds_pos[1]+(height-all_pad_height)/2+pad_height+finger_height*2+finger_space+cc_height+cc_space)
        left_comb_upper_2 = (gds_pos[0]+(width-pad_width)/2+comb_dis+comb_space_hor*3+comb_width*3,gds_pos[1]+(height-all_pad_height)/2+pad_height+cc_height+cc_space+comb_space_vert)
        right_comb_upper_2 = (gds_pos[0]+(width-pad_width)/2+comb_dis+comb_space_hor*3+comb_width*4,gds_pos[1]+(height-all_pad_height)/2+pad_height+finger_height*2+finger_space+cc_height+cc_space)
        left_comb_upper_3 = (gds_pos[0]+(width-pad_width)/2+comb_dis+comb_space_hor*6+comb_width*6,gds_pos[1]+(height-all_pad_height)/2+pad_height+cc_height+cc_space+comb_space_vert)
        right_comb_upper_3 = (gds_pos[0]+(width-pad_width)/2+comb_dis+comb_space_hor*6+comb_width*7,gds_pos[1]+(height-all_pad_height)/2+pad_height+finger_height*2+finger_space+cc_height+cc_space)
        left_comb_upper_4 = (gds_pos[0]+(width-pad_width)/2+comb_dis+comb_space_hor*8+comb_width*8,gds_pos[1]+(height-all_pad_height)/2+pad_height+cc_height+cc_space+comb_space_vert)
        right_comb_upper_4 = (gds_pos[0]+(width-pad_width)/2+comb_dis+comb_space_hor*8+comb_width*9,gds_pos[1]+(height-all_pad_height)/2+pad_height+finger_height*2+finger_space+cc_height+cc_space)

        # Comb coordinates for the junction
        left_comb_lower_j = (gds_pos[0]+(width-pad_width)/2+comb_dis+comb_width*4+comb_space_hor*4,gds_pos[1]+(height-all_pad_height)/2+pad_height+cc_height+cc_space)
        right_comb_lower_j = (gds_pos[0]+(width-pad_width)/2+comb_dis+comb_width*4+comb_space_hor*4+finger_width,gds_pos[1]+(height-all_pad_height)/2+pad_height+cc_height+cc_space+finger_height)

        left_comb_upper_j = (gds_pos[0]+(width-pad_width)/2+comb_dis+comb_width*4+comb_space_hor*4,gds_pos[1]+(height-all_pad_height)/2+pad_height+cc_height+cc_space+finger_height+finger_space)
        right_comb_upper_j = (gds_pos[0]+(width-pad_width)/2+comb_dis+comb_width*4+comb_space_hor*4+finger_width,gds_pos[1]+(height-all_pad_height)/2+pad_height+cc_height+cc_space+finger_height*2+finger_space)

        # Lower left small pad coordinates
        left_lpad_lower_left = (gds_pos[0]+(width-pad_width)/2,gds_pos[1]+(height-all_pad_height)/2)
        right_lpad_lower_left = (gds_pos[0]+(width-pad_width)/2+cc_width,gds_pos[1]+(height-all_pad_height)/2+cc_height)
        # Lower left cpw coordinates
        left_cpw_lower_left = (gds_pos[0]+(width-pad_width)/2+(cc_width-cpw_width)/2,gds_pos[1]+(height-all_pad_height)/2)
        right_cpw_lower_left = (gds_pos[0]+(width-pad_width)/2+(cc_width-cpw_width)/2+cpw_width,gds_pos[1])

        # Lower right small pad coordinates
        left_lpad_lower_right = (gds_pos[0]+(width-pad_width)/2+pad_width-cc_width,gds_pos[1]+(height-all_pad_height)/2)
        right_lpad_lower_right = (gds_pos[0]+(width-pad_width)/2+pad_width,gds_pos[1]+(height-all_pad_height)/2+cc_height)
        # Lower right cpw coordinates
        left_cpw_lower_right = (gds_pos[0]+(width-pad_width)/2+pad_width-cc_width+(cc_width-cpw_width)/2,gds_pos[1]+(height-all_pad_height)/2)
        right_cpw_lower_right = (gds_pos[0]+(width-pad_width)/2+pad_width-cc_width+(cc_width-cpw_width)/2+cpw_width,gds_pos[1])

        # Lower center small pad coordinates
        left_lpad_lower_center = (gds_pos[0]+(width-cc_width)/2,gds_pos[1]+(height-all_pad_height)/2)
        right_lpad_lower_center = (gds_pos[0]+(width-cc_width)/2+cc_width,gds_pos[1]+(height-all_pad_height)/2+cc_height)
        # Lower center cpw coordinates
        left_cpw_lower_center = (gds_pos[0]+(width-cc_width)/2+(cc_width-cpw_width)/2,gds_pos[1]+(height-all_pad_height)/2)
        right_cpw_lower_center = (gds_pos[0]+(width-cc_width)/2+(cc_width-cpw_width)/2+cpw_width,gds_pos[1])

        # Upper left small pad coordinates
        left_lpad_upper_left = (gds_pos[0]+(width-pad_width)/2,gds_pos[1]+(height-all_pad_height)/2+pad_height*2+finger_height*2+finger_space+cc_height+cc_space*2)
        right_lpad_upper_left = (gds_pos[0]+(width-pad_width)/2+cc_width,gds_pos[1]+(height-all_pad_height)/2+pad_height*2+finger_height*2+finger_space+cc_height*2+cc_space*2)
        # Upper left cpw coordinates
        left_cpw_upper_left = (gds_pos[0]+(width-pad_width)/2+(cc_width-cpw_width)/2,gds_pos[1]+(height-all_pad_height)/2+pad_height*2+finger_height*2+finger_space+cc_height*2+cc_space*2)
        right_cpw_upper_left = (gds_pos[0]+(width-pad_width)/2+(cc_width-cpw_width)/2+cpw_width,gds_pos[1]+height)

        # Upper right small pad coordinates
        left_lpad_upper_right = (gds_pos[0]+(width-pad_width)/2+pad_width-cc_width,gds_pos[1]+(height-all_pad_height)/2+pad_height*2+finger_height*2+finger_space+cc_height+cc_space*2)
        right_lpad_upper_right = (gds_pos[0]+(width-pad_width)/2+pad_width,gds_pos[1]+(height-all_pad_height)/2+pad_height*2+finger_height*2+finger_space+cc_height*2+cc_space*2)
        # Upper right cpw coordinates
        left_cpw_upper_right = (gds_pos[0]+(width-pad_width)/2+pad_width-cc_width+(cc_width-cpw_width)/2,gds_pos[1]+(height-all_pad_height)/2+pad_height*2+finger_height*2+finger_space+cc_height*2+cc_space*2)
        right_cpw_upper_right = (gds_pos[0]+(width-pad_width)/2+pad_width-cc_width+(cc_width-cpw_width)/2+cpw_width,gds_pos[1]+height)

        # Upper center small pad coordinates
        left_lpad_upper_center = (gds_pos[0]+(width-cc_width)/2,gds_pos[1]+(height-all_pad_height)/2+pad_height*2+finger_height*2+finger_space+cc_height+cc_space*2)
        right_lpad_upper_center = (gds_pos[0]+(width-cc_width)/2+cc_width,gds_pos[1]+(height-all_pad_height)/2+pad_height*2+finger_height*2+finger_space+cc_height*2+cc_space*2)
        # Upper center cpw coordinates
        left_cpw_upper_center = (gds_pos[0]+(width-cc_width)/2+(cc_width-cpw_width)/2,gds_pos[1]+(height-all_pad_height)/2+pad_height*2+finger_height*2+finger_space+cc_height*2+cc_space*2)
        right_cpw_upper_center = (gds_pos[0]+(width-cc_width)/2+(cc_width-cpw_width)/2+cpw_width,gds_pos[1]+height)
        # Draw lower large pad
        lower_pad = gdspy.Rectangle(left_pad_lower,
                                    right_pad_lower)

        # Draw upper large pad
        upper_pad = gdspy.Rectangle(left_pad_upper,
                                    right_pad_upper)

        # Draw lower combs
        lower_comb_1 = gdspy.Rectangle(left_comb_lower_1,
                                    right_comb_lower_1)
        lower_comb_2 = gdspy.Rectangle(left_comb_lower_2,
                                    right_comb_lower_2)
        lower_comb_3 = gdspy.Rectangle(left_comb_lower_3,
                                    right_comb_lower_3)
        lower_comb_4 = gdspy.Rectangle(left_comb_lower_4,
                                    right_comb_lower_4)
        # Draw upper combs
        upper_comb_1 = gdspy.Rectangle(left_comb_upper_1,
                                    right_comb_upper_1)
        upper_comb_2 = gdspy.Rectangle(left_comb_upper_2,
                                    right_comb_upper_2)
        upper_comb_3 = gdspy.Rectangle(left_comb_upper_3,
                                    right_comb_upper_3)
        upper_comb_4 = gdspy.Rectangle(left_comb_upper_4,
                                    right_comb_upper_4)

        # Draw lower junction combs
        lower_comb_j = gdspy.Rectangle(left_comb_lower_j,
                                    right_comb_lower_j)
        # Draw upper junction combs
        upper_comb_j = gdspy.Rectangle(left_comb_upper_j,
                                    right_comb_upper_j)

        # Combine lower pad
        lower_pad = gdspy.boolean(lower_pad,lower_comb_1,'or')
        lower_pad = gdspy.boolean(lower_pad,lower_comb_2,'or')
        lower_pad = gdspy.boolean(lower_pad,lower_comb_3,'or')
        lower_pad = gdspy.boolean(lower_pad,lower_comb_4,'or')
        lower_pad = gdspy.boolean(lower_pad,lower_comb_j,'or')

        # Combine upper pad
        upper_pad = gdspy.boolean(upper_pad,upper_comb_1,'or')
        upper_pad = gdspy.boolean(upper_pad,upper_comb_2,'or')
        upper_pad = gdspy.boolean(upper_pad,upper_comb_3,'or')
        upper_pad = gdspy.boolean(upper_pad,upper_comb_4,'or')
        upper_pad = gdspy.boolean(upper_pad,upper_comb_j,'or')

        # Draw lower coupling pads
        lower_lpad_center = gdspy.Rectangle(left_lpad_lower_center,
                                    right_lpad_lower_center)
        lower_lpad_left = gdspy.Rectangle(left_lpad_lower_left,
                                    right_lpad_lower_left)
        lower_lpad_right = gdspy.Rectangle(left_lpad_lower_right,
                                    right_lpad_lower_right)
        # Draw lower coupling cpw
        lower_cpw_center = gdspy.Rectangle(left_cpw_lower_center,
                                    right_cpw_lower_center)
        lower_cpw_left = gdspy.Rectangle(left_cpw_lower_left,
                                        right_cpw_lower_left)
        lower_cpw_right = gdspy.Rectangle(left_cpw_lower_right,
                                        right_cpw_lower_right)
        # Combine lower coupling pads
        lower_lpad_center = gdspy.boolean(lower_lpad_center,lower_cpw_center,'or')
        lower_lpad_left = gdspy.boolean(lower_lpad_left,lower_cpw_left,'or')
        lower_lpad_right = gdspy.boolean(lower_lpad_right,lower_cpw_right,'or')

        # Draw upper coupling pads
        upper_lpad_left = gdspy.Rectangle(left_lpad_upper_left,
                                        right_lpad_upper_left)
        upper_lpad_right = gdspy.Rectangle(left_lpad_upper_right,
                                        right_lpad_upper_right)
        upper_lpad_center = gdspy.Rectangle(left_lpad_upper_center,
                                            right_lpad_upper_center)
        # Draw upper coupling cpw
        upper_cpw_left = gdspy.Rectangle(left_cpw_upper_left,
                                        right_cpw_upper_left)
        upper_cpw_right = gdspy.Rectangle(left_cpw_upper_right,
                                        right_cpw_upper_right)
        upper_cpw_center = gdspy.Rectangle(left_cpw_upper_center,
                                        right_cpw_upper_center)
        # Combine upper coupling pads
        upper_lpad_left = gdspy.boolean(upper_lpad_left,upper_cpw_left,'or')
        upper_lpad_right = gdspy.boolean(upper_lpad_right,upper_cpw_right,'or')
        upper_lpad_center = gdspy.boolean(upper_lpad_center,upper_cpw_center,'or')

        rect = gdspy.boolean(rect,lower_pad,'not')
        rect = gdspy.boolean(rect,upper_pad,'not')
        rect = gdspy.boolean(rect,lower_lpad_center,'not')
        rect = gdspy.boolean(rect,lower_lpad_left,'not')
        rect = gdspy.boolean(rect,lower_lpad_right,'not')
        rect = gdspy.boolean(rect,upper_lpad_left,'not')
        rect = gdspy.boolean(rect,upper_lpad_right,'not')
        rect = gdspy.boolean(rect,upper_lpad_center,'not')
        self.cell.add(rect)
        return