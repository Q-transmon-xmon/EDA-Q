#########################################################################
# File Name: transmon_teeth.py
# Description: Defines the TransmonTeeth class, which is used to draw the geometric structure of a superconducting qubit and generate elements in a GDS design database.
#              Includes qubit parameter settings, pin calculations, and geometric shape drawing functions.
#########################################################################
from addict import Dict
from base.library_base import LibraryBase
import toolbox
import copy, gdspy

class TransmonTeeth(LibraryBase):
    default_options = Dict(
        # Framework
        name = "q0",
        type = "TransmonTeeth",
        gds_pos = (0, 0),
        topo_pos = (0, 0),
        chip = "chip0",
        readout_pins = [],
        control_pins = [],
        coupling_pins = [],
        outline = [],
        # Dimension parameters
        pad_gap=30,
        inductor_width=20,
        pad_width=400,
        pad_height=90,
        pocket_width=650,
        pocket_height=650,
        coupled_pad_height=150,
        coupled_pad_width=20,
        coupled_pad_gap=50,  # One can arrange the gap between the teeth.
        connect_pad_gap=15,
        connect_pad_width=20,
        connect_pad_height=150,
        cpw_width=10,
        cpw_gap=6,
        pad_options = [1,1,1,1,1,1]
    )
    
    def __init__(self, options):
        """
        Initializes the TransmonTeeth class.
        
        Input:
            options: Dictionary containing component parameter options.
        """
        super().__init__(options)
        return
    
    def calc_general_ops(self):
        """
        Calculates the pin coordinates and outline.
        """
        pad_gap=self.pad_gap
        inductor_width=self.inductor_width
        pad_width=self.pad_width
        pad_height=self.pad_height
        pocket_width=self.pocket_width
        pocket_height=self.pocket_height
        # coupled_pad belongs to the teeth part. Teeth will have same height/width and are symmetric.
        coupled_pad_height=self.coupled_pad_height
        coupled_pad_width=self.coupled_pad_width
        coupled_pad_gap=self.coupled_pad_gap  # One can arrange the gap between the teeth.
        connect_pad_gap=self.connect_pad_gap
        connect_pad_width=self.connect_pad_width
        connect_pad_height=self.connect_pad_height
        cpw_width=self.cpw_width
        cpw_gap=self.cpw_gap
        pad_options = self.pad_options
        gds_pos = self.gds_pos

        self.coupling_pins.top = [gds_pos[0]+pocket_width,gds_pos[1]+(pocket_height -pad_gap)/2+pad_height+pad_gap+connect_pad_gap+cpw_width/2]
        self.coupling_pins.bot = [gds_pos[0]+(pocket_width - coupled_pad_width*2 - coupled_pad_gap)/2+connect_pad_width+connect_pad_gap+1+cpw_gap+cpw_width/2,gds_pos[1]]
        self.coupling_pins.left = [gds_pos[0],gds_pos[1]+(pocket_height - pad_height*2-pad_gap)/2-connect_pad_gap-cpw_width/2]
        self.coupling_pins.right = [gds_pos[0]+pocket_width,gds_pos[1]+(pocket_height - pad_height*2-pad_gap)/2-connect_pad_gap-cpw_width/2]
        self.readout_pins.append([gds_pos[0],gds_pos[1]+(pocket_height -pad_gap)/2+pad_height+pad_gap+connect_pad_gap+cpw_width/2])    # append contains a coordinate, represented as a list, e.g., [0, 0]
        self.control_pins.append([gds_pos[0]+(pocket_width - coupled_pad_width*2 - coupled_pad_gap)/2+connect_pad_width+connect_pad_gap+1+cpw_gap+cpw_width/2,gds_pos[1]+pocket_height])
        self.outline = [[gds_pos[0], gds_pos[1]], [gds_pos[0]+pocket_width,gds_pos[1]],[gds_pos[0]+pocket_width, gds_pos[1]+pocket_height],[gds_pos[0],gds_pos[1]+pocket_height],[gds_pos[0],gds_pos[1]]]

        return

    def draw_gds(self):
        """
        Draws the geometric shapes of the qubit and adds them to the GDS cell.
        """
        pad_gap=self.pad_gap
        inductor_width=self.inductor_width
        pad_width=self.pad_width
        pad_height=self.pad_height
        pocket_width=self.pocket_width
        pocket_height=self.pocket_height
        # coupled_pad belongs to the teeth part. Teeth will have same height/width and are symmetric.
        coupled_pad_height=self.coupled_pad_height
        coupled_pad_width=self.coupled_pad_width
        coupled_pad_gap=self.coupled_pad_gap  # One can arrange the gap between the teeth.
        connect_pad_gap=self.connect_pad_gap
        connect_pad_width=self.connect_pad_width
        connect_pad_height=self.connect_pad_height
        cpw_width=self.cpw_width
        cpw_gap=self.cpw_gap
        pad_options = self.pad_options
        gds_pos = self.gds_pos

        gdspy.library.use_current_library = False
        self.cell = self.lib.new_cell(self.name)

        """
        Add your code here
        self.cell_subtract draws the metal part
        The remaining red area after subtraction is the substrate
        """
        # Calculate the coordinates of the four corners of the lower rectangle
        lower_rect_left = (gds_pos[0]+(pocket_width - pad_width)/2,gds_pos[1]+(pocket_height - pad_height*2-pad_gap)/2)
        lower_rect_right = (gds_pos[0]+(pocket_width - pad_width)/2+pad_width,gds_pos[1]+(pocket_height - pad_height*2-pad_gap)/2+pad_height)
        lower_rect_center = (gds_pos[0]+(pocket_width)/2,gds_pos[1]+(pocket_height - pad_height-pad_gap)/2)
        # Calculate the center coordinates of the left circle in the lower rectangle
        lower_circle_left = (gds_pos[0]+(pocket_width - pad_width)/2,gds_pos[1]+(pocket_height - pad_height-pad_gap)/2)

        # Calculate the center coordinates of the right circle in the lower rectangle
        lower_circle_right = (gds_pos[0]+(pocket_width - pad_width)/2+pad_width,gds_pos[1]+(pocket_height - pad_height-pad_gap)/2)

        # Calculate the coordinates of the four corners of the upper rectangle
        upper_rect_left = (gds_pos[0]+(pocket_width - pad_width)/2,gds_pos[1]+(pocket_height -pad_gap)/2+pad_gap)
        upper_rect_right = (gds_pos[0]+(pocket_width - pad_width)/2+pad_width,gds_pos[1]+(pocket_height -pad_gap)/2+pad_height+pad_gap)
        upper_rect_center = (gds_pos[0]+(pocket_width)/2,gds_pos[1]+(pocket_height-pad_gap+pad_height)/2+pad_gap)

        # Calculate the center coordinates of the left circle in the upper rectangle
        upper_circle_left = (gds_pos[0]+(pocket_width - pad_width)/2,gds_pos[1]+(pocket_height-pad_gap+pad_height)/2+pad_gap)

        # Calculate the center coordinates of the right circle in the upper rectangle
        upper_circle_right = (gds_pos[0]+(pocket_width - pad_width)/2+pad_width,gds_pos[1]+(pocket_height-pad_gap+pad_height)/2+pad_gap)

        # Calculate the coordinates of the left tooth in the upper part
        left_tooth_left = (gds_pos[0]+(pocket_width - coupled_pad_width*2 - coupled_pad_gap)/2,gds_pos[1]+(pocket_height -pad_gap)/2+pad_height+pad_gap)
        left_tooth_right = (gds_pos[0]+(pocket_width  - coupled_pad_gap)/2,gds_pos[1]+(pocket_height -pad_gap)/2+pad_height+pad_gap+coupled_pad_height)

        # Calculate the center coordinates of the left tooth in the upper part
        left_tooth_circle = (gds_pos[0]+(pocket_width - coupled_pad_width - coupled_pad_gap)/2,gds_pos[1]+(pocket_height -pad_gap)/2+pad_height+pad_gap+coupled_pad_height)

        # Calculate the coordinates of the right tooth in the upper part
        right_tooth_left = (gds_pos[0]+(pocket_width  + coupled_pad_gap)/2,gds_pos[1]+(pocket_height -pad_gap)/2+pad_height+pad_gap)
        right_tooth_right = (gds_pos[0]+(pocket_width  + coupled_pad_gap)/2+ coupled_pad_width,gds_pos[1]+(pocket_height -pad_gap)/2+pad_height+pad_gap+coupled_pad_height)

        # Calculate the center coordinates of the right tooth in the upper part
        right_tooth_circle = (gds_pos[0]+(pocket_width  + coupled_pad_width + coupled_pad_gap)/2,gds_pos[1]+(pocket_height -pad_gap)/2+pad_height+pad_gap+coupled_pad_height)

        # Calculate the coordinates of the small pad in the center of the upper part
        left_pad_upper_center = (gds_pos[0]+(pocket_width - coupled_pad_width*2 - coupled_pad_gap)/2+connect_pad_width+connect_pad_gap,gds_pos[1]+(pocket_height -pad_gap)/2+pad_height+pad_gap+connect_pad_gap)
        right_pad_upper_center = (gds_pos[0]+(pocket_width - coupled_pad_width*2 - coupled_pad_gap)/2+connect_pad_width*2+connect_pad_gap,gds_pos[1]+(pocket_height -pad_gap)/2+pad_height+pad_gap+connect_pad_gap+connect_pad_height)

        # Upper center cpw coordinates
        left_cpw_upper_center = (gds_pos[0]+(pocket_width - coupled_pad_width*2 - coupled_pad_gap)/2+connect_pad_width+connect_pad_gap-1+cpw_gap,gds_pos[1]+(pocket_height -pad_gap)/2+pad_height+pad_gap+connect_pad_gap+connect_pad_height)
        right_cpw_upper_center = (gds_pos[0]+(pocket_width - coupled_pad_width*2 - coupled_pad_gap)/2+connect_pad_width+connect_pad_gap+1+cpw_gap+cpw_width,gds_pos[1]+pocket_height)

        # Calculate the coordinates of the small pad on the left of the upper part
        left_pad_upper_left = (gds_pos[0]+(pocket_width - pad_width)/2,gds_pos[1]+(pocket_height -pad_gap)/2+pad_height+pad_gap+connect_pad_gap)
        right_pad_upper_left = (gds_pos[0]+(pocket_width - pad_width)/2+connect_pad_width,gds_pos[1]+(pocket_height -pad_gap)/2+pad_height+pad_gap+connect_pad_gap+connect_pad_height)
        # Upper left cpw coordinates
        left_cpw_upper_left = (gds_pos[0],gds_pos[1]+(pocket_height -pad_gap)/2+pad_height+pad_gap+connect_pad_gap)
        right_cpw_upper_left = (gds_pos[0]+(pocket_width - pad_width)/2,gds_pos[1]+(pocket_height -pad_gap)/2+pad_height+pad_gap+connect_pad_gap+cpw_width)

        # Calculate the coordinates of the small pad on the right of the upper part
        left_pad_upper_right = (gds_pos[0]+(pocket_width - pad_width)/2+pad_width-connect_pad_width,gds_pos[1]+(pocket_height -pad_gap)/2+pad_height+pad_gap+connect_pad_gap)
        right_pad_upper_right = (gds_pos[0]+(pocket_width - pad_width)/2+pad_width,gds_pos[1]+(pocket_height -pad_gap)/2+pad_height+pad_gap+connect_pad_gap+connect_pad_height)
        # Upper right cpw coordinates
        left_cpw_upper_right = (gds_pos[0]+(pocket_width - pad_width)/2+pad_width,gds_pos[1]+(pocket_height -pad_gap)/2+pad_height+pad_gap+connect_pad_gap)
        right_cpw_upper_right = (gds_pos[0]+pocket_width,gds_pos[1]+(pocket_height -pad_gap)/2+pad_height+pad_gap+connect_pad_gap+cpw_width)

        # Calculate the coordinates of the small pad in the center of the lower part
        left_pad_lower_center = (gds_pos[0]+(pocket_width - coupled_pad_width*2 - coupled_pad_gap)/2+connect_pad_width+connect_pad_gap,gds_pos[1]+(pocket_height - pad_height*2-pad_gap)/2-connect_pad_gap)
        right_pad_lower_center = (gds_pos[0]+(pocket_width - coupled_pad_width*2 - coupled_pad_gap)/2+connect_pad_width*2+connect_pad_gap,gds_pos[1]+(pocket_height - pad_height*2-pad_gap)/2-connect_pad_gap-connect_pad_height)
        # Lower center cpw coordinates
        left_cpw_lower_center = (gds_pos[0]+(pocket_width - coupled_pad_width*2 - coupled_pad_gap)/2+connect_pad_width+connect_pad_gap-1+cpw_gap,gds_pos[1]+(pocket_height - pad_height*2-pad_gap)/2-connect_pad_gap-connect_pad_height)
        right_cpw_lower_center = (gds_pos[0]+(pocket_width - coupled_pad_width*2 - coupled_pad_gap)/2+connect_pad_width+connect_pad_gap+1+cpw_gap+cpw_width,gds_pos[1])

        # Calculate the coordinates of the small pad on the left of the lower part
        left_pad_lower_left = (gds_pos[0]+(pocket_width - pad_width)/2,gds_pos[1]+(pocket_height - pad_height*2-pad_gap)/2-connect_pad_gap)
        right_pad_lower_left = (gds_pos[0]+(pocket_width - pad_width)/2+connect_pad_width,gds_pos[1]+(pocket_height - pad_height*2-pad_gap)/2-connect_pad_gap-connect_pad_height)
        # Lower left cpw coordinates
        left_cpw_lower_left = (gds_pos[0]+(pocket_width - pad_width)/2,gds_pos[1]+(pocket_height - pad_height*2-pad_gap)/2-connect_pad_gap)
        right_cpw_lower_left = (gds_pos[0],gds_pos[1]+(pocket_height - pad_height*2-pad_gap)/2-connect_pad_gap-cpw_width)

        # Calculate the coordinates of the small pad on the right of the lower part
        left_pad_lower_right = (gds_pos[0]+(pocket_width - pad_width)/2+pad_width-connect_pad_width,gds_pos[1]+(pocket_height - pad_height*2-pad_gap)/2-connect_pad_gap)
        right_pad_lower_right = (gds_pos[0]+(pocket_width - pad_width)/2+pad_width,gds_pos[1]+(pocket_height - pad_height*2-pad_gap)/2-connect_pad_gap-connect_pad_height)
        # Lower right cpw coordinates
        left_cpw_lower_right = (gds_pos[0]+(pocket_width - pad_width)/2+pad_width-connect_pad_width,gds_pos[1]+(pocket_height - pad_height*2-pad_gap)/2-connect_pad_gap)
        right_cpw_lower_right = (gds_pos[0]+pocket_width,gds_pos[1]+(pocket_height - pad_height*2-pad_gap)/2-connect_pad_gap-cpw_width)
        
        # Create the geometry (a single rectangle) and add it to the cell.
        rect = gdspy.Rectangle((gds_pos[0], gds_pos[1]), (gds_pos[0]+pocket_width, gds_pos[1]+pocket_height))
        # Create the lower rectangle shape
        rect_lower = gdspy.Rectangle(
            lower_rect_left,
            lower_rect_right
        )
        # Create the left circle in the lower rectangle
        circle_left_lower = gdspy.Round(lower_circle_left,
                                        pad_height/2,tolerance=0.01)

        # Create the right circle in the lower rectangle
        circle_right_lower = gdspy.Round(lower_circle_right,
                                        pad_height/2,tolerance=0.01)

        # Combine the lower pad
        lower_comb = gdspy.boolean(rect_lower,circle_left_lower,'or')
        lower_comb = gdspy.boolean(lower_comb,circle_right_lower,'or')
                
        # Create the upper rectangle shape
        rect_upper = gdspy.Rectangle(
            upper_rect_left,
            upper_rect_right
        )
        # Create the left circle in the upper rectangle
        circle_left_upper = gdspy.Round(upper_circle_left,
                                        pad_height/2,tolerance=0.01)
        # Create the right circle in the upper rectangle
        circle_right_upper = gdspy.Round(upper_circle_right,
                                        pad_height/2,tolerance=0.01)
        # Create the left tooth in the upper part
        rect_tooth_left = gdspy.Rectangle(left_tooth_left,
                                        left_tooth_right)
        # Create the left tooth circle
        circle_tooth_left = gdspy.Round(left_tooth_circle,
                                        coupled_pad_width/2,tolerance=0.01)
        # Combine the left tooth
        tooth_left = gdspy.boolean(rect_tooth_left,circle_tooth_left,'or')

        # Create the right tooth in the upper part
        rect_tooth_right = gdspy.Rectangle(right_tooth_left,
                                        right_tooth_right)
        # Create the right tooth circle
        circle_tooth_right = gdspy.Round(right_tooth_circle,
                                        coupled_pad_width/2,tolerance=0.01)
        # Combine the right tooth
        tooth_right = gdspy.boolean(rect_tooth_right,circle_tooth_right,'or')

        # Combine the upper pad
        upper_comb = gdspy.boolean(rect_upper,circle_left_upper,'or')
        upper_comb = gdspy.boolean(upper_comb,circle_right_upper,'or')
        upper_comb = gdspy.boolean(upper_comb,tooth_left,'or')
        upper_comb = gdspy.boolean(upper_comb,tooth_right,'or')

        # Create the small pad in the center of the upper part
        upper_pad_loc_center = gdspy.Rectangle(left_pad_upper_center,
                                        right_pad_upper_center)
        # Create the upper center cpw
        upper_cpw_in_center = gdspy.Rectangle(left_cpw_upper_center,
                                    right_cpw_upper_center)
        # Combine the upper center small pad and cpw 
        upper_pad_loc_center = gdspy.boolean(upper_pad_loc_center,upper_cpw_in_center,'or')

        # Create the small pad on the left of the upper part
        upper_pad_loc_left = gdspy.Rectangle(left_pad_upper_left,
                                        right_pad_upper_left)
        # Create the upper left cpw
        upper_cpw_in_left = gdspy.Rectangle(left_cpw_upper_left,
                                    right_cpw_upper_left)
        # Combine the upper left small pad and cpw 
        upper_pad_loc_left = gdspy.boolean(upper_pad_loc_left,upper_cpw_in_left,'or')

        # Create the small pad on the right of the upper part
        upper_pad_loc_right = gdspy.Rectangle(left_pad_upper_right,
                                        right_pad_upper_right)
        # Create the upper right cpw
        upper_cpw_in_right = gdspy.Rectangle(left_cpw_upper_right,
                                    right_cpw_upper_right)
        # Combine the upper right small pad and cpw 
        upper_pad_loc_right = gdspy.boolean(upper_pad_loc_right,upper_cpw_in_right,'or')

        # Create the small pad in the center of the lower part
        lower_pad_loc_center = gdspy.Rectangle(left_pad_lower_center,
                                        right_pad_lower_center)
        # Create the lower center cpw
        lower_cpw_in_center = gdspy.Rectangle(left_cpw_lower_center,
                                    right_cpw_lower_center)
        # Combine the lower center small pad and cpw 
        lower_pad_loc_center = gdspy.boolean(lower_pad_loc_center,lower_cpw_in_center,'or')

        # Create the small pad on the left of the lower part
        lower_pad_loc_left = gdspy.Rectangle(left_pad_lower_left,
                                        right_pad_lower_left)
        # Create the lower left cpw
        lower_cpw_in_left = gdspy.Rectangle(left_cpw_lower_left,
                                        right_cpw_lower_left)
        # Combine the lower left small pad and cpw 
        lower_pad_loc_left = gdspy.boolean(lower_pad_loc_left,lower_cpw_in_left,'or')

        # Create the small pad on the right of the lower part
        lower_pad_loc_right = gdspy.Rectangle(left_pad_lower_right,
                                        right_pad_lower_right)
        # Create the lower right cpw
        lower_cpw_in_right = gdspy.Rectangle(left_cpw_lower_right,
                                        right_cpw_lower_right)
        # Combine the lower right small pad and cpw 
        lower_pad_loc_right = gdspy.boolean(lower_pad_loc_right,lower_cpw_in_right,'or')

        pad_loc = [upper_pad_loc_center,upper_pad_loc_left,upper_pad_loc_right,lower_pad_loc_center,lower_pad_loc_left,lower_pad_loc_right]
        rect = gdspy.boolean(rect,lower_comb,'not')
        rect = gdspy.boolean(rect,upper_comb,'not')
        for i in range(6):
            if pad_options[i] == 1:
                rect = gdspy.boolean(rect,pad_loc[i],'not')
        self.cell.add(rect)
        return