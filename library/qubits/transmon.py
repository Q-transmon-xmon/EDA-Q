#########################################################################
# File Name: transmon.py
# Description: Defines the Transmon class, which is used to draw the geometric structure of a superconducting qubit and generate elements in a GDS design database.
#              Includes qubit parameter settings, pin calculations, and geometric shape drawing functions.
#########################################################################
from addict import Dict
from base.library_base import LibraryBase
import gdspy, numpy as np

class Transmon(LibraryBase):
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
        # Geometric parameters
        cpw_width=[10]*6,
        cpw_extend=[100]*6,
        width=455,
        height=200,
        gap=30,
        pad_options=[1]*6,
        pad_gap=[15]*6,
        pad_width=[125]*6,
        pad_height=[30]*6,
        cpw_pos=[[0,0]]*6,
        control_distance=[10]*4,
        subtract_gap=20,
        subtract_width = 600,
        subtract_height = 600
    )

    def __init__(self, options):
        """
        Initializes the Transmon class.
        
        Input:
            options: Dictionary containing component parameter options.
        """
        super().__init__(options)
        return
    
    def calc_general_ops(self):
        """
        Calculates the pin coordinates and outline.
        """
        # Retrieve parameters from options
        width = self.width
        height = self.height
        cpw_width = self.cpw_width
        cpw_extend = self.cpw_extend
        gap = self.gap
        pad_options = self.pad_options
        pad_gap = self.pad_gap
        pad_height = self.pad_height
        pad_width = self.pad_width
        cpw_pos = self.cpw_pos
        gds_pos = self.gds_pos
        control_pins = self.control_pins
        control_distance = self.control_distance
        subtract_gap = self.subtract_gap
        subtract_width = self.subtract_width
        subtract_height = self.subtract_height

        # Generate coordinates for automatic routing
        self.readout_pins = []
        self.control_pins = []
        self.coupling_pins = []

        self.readout_pins.append((-width/2-cpw_extend[0]+gds_pos[0],gap/2+height+pad_gap[0]+pad_height[0]/2+gds_pos[1]))
        self.control_pins.append((gds_pos[0]-width/2-max(cpw_extend)-control_distance[0],gds_pos[1]+gap/2+height/2))
        self.control_pins.append((gds_pos[0]+width/2+max(cpw_extend)+control_distance[1],gds_pos[1]+gap/2+height/2))
        self.control_pins.append((gds_pos[0]-width/2-max(cpw_extend)-control_distance[2],gds_pos[1]-gap/2-height/2))
        self.control_pins.append((gds_pos[0]+width/2+max(cpw_extend)+control_distance[3],gds_pos[1]-gap/2-height/2))
        self.coupling_pins.append((gds_pos[0], gds_pos[1]+gap/2+height+pad_gap[1]+pad_height[1]/2+cpw_extend[1]))
        self.coupling_pins.append((gds_pos[0], gds_pos[1]-gap/2-height-pad_gap[4]-pad_height[4]/2-cpw_extend[4]))
        self.coupling_pins.append((gds_pos[0]-width/2-cpw_extend[2], gds_pos[1]-gap/2-height-pad_gap[2]-pad_height[2]/2))
        self.coupling_pins.append((gds_pos[0]+width/2+cpw_extend[5], gds_pos[1]-gap/2-height-pad_gap[5]-pad_height[5]/2))
        

        self.outline = [[gds_pos[0]-width/2-subtract_gap, gds_pos[1]+gap/2+height+subtract_gap],
                        [gds_pos[0]+width/2+subtract_gap, gds_pos[1]+gap/2+height+subtract_gap],
                        [gds_pos[0]+width/2+subtract_gap, gds_pos[1]-gap/2-height-subtract_gap],
                        [gds_pos[0]-width/2-subtract_gap, gds_pos[1]-gap/2-height-subtract_gap],
                        [gds_pos[0]-width/2-subtract_gap, gds_pos[1]+gap/2+height+subtract_gap]]
        
        return

    def draw_gds(self):
        """
        Draws the geometric shapes of the Transmon and adds them to the GDS cell.
        """
        # gdspy variables
        gdspy.library.use_current_library = False
        self.lib = gdspy.GdsLibrary()
        self.cell = self.lib.new_cell(self.name)
        self.cell_subtract = self.lib.new_cell(self.name + "_subtract")
        
        # Retrieve parameters from options
        width = self.width
        height = self.height
        cpw_width = self.cpw_width
        cpw_extend = self.cpw_extend
        gap = self.gap
        pad_options = self.pad_options
        pad_gap = self.pad_gap
        pad_height = self.pad_height
        pad_width = self.pad_width
        cpw_pos = self.cpw_pos
        gds_pos = self.gds_pos
        control_distance = self.control_distance
        subtract_gap = self.subtract_gap
        subtract_width = self.subtract_width
        subtract_height = self.subtract_height

        # Check if the main rectangle width is large enough to accommodate all pads
        total_pad_height_upper = sum([x * y for x, y in zip(pad_width[:3], pad_options[:3])])
        total_pad_height_lower = sum([x * y for x, y in zip(pad_width[-3:], pad_options[-3:])])
        if width < total_pad_height_upper and width < total_pad_height_lower:
            raise ValueError("The main rectangle width is too small to accommodate all pads.")

        # Calculate the main body center coordinates
        main_body_x = gds_pos[0]
        main_body_y = gds_pos[1]
        
        # Calculate the coordinates of the four corners of the upper rectangle
        upper_left = [main_body_x - width/2, main_body_y + gap/2 + height]
        upper_right = [main_body_x + width/2, main_body_y + gap/2 + height]
        upper_center = [main_body_x, main_body_y + gap/2 + height]
        
        # Calculate the coordinates of the four corners of the lower rectangle
        lower_left = [main_body_x - width/2, main_body_y - gap/2 - height]
        lower_right = [main_body_x + width/2, main_body_y - gap/2 - height]
        lower_center = [main_body_x, main_body_y - gap/2 - height]
        
        # Create the upper rectangle shape
        rect_upper = gdspy.Rectangle(
            (main_body_x - width/2, main_body_y + gap/2),
            (main_body_x + width/2, main_body_y + height + gap/2)
        )
        self.cell_subtract.add(rect_upper)
        
        # Create the lower rectangle shape
        rect_lower = gdspy.Rectangle(
            (main_body_x - width/2, main_body_y - height - gap/2),
            (main_body_x + width/2, main_body_y - gap/2)
        )
        self.cell_subtract.add(rect_lower)
        
        # Add connection pads
        cpw_positions = [upper_left, upper_center, upper_right, lower_left, lower_center, lower_right]
        for i in range(6):
            if pad_options[i] == 1:
                # Calculate the x-coordinate of the pad, ensuring it does not exceed the main rectangle boundaries
                pad_x = max(main_body_x - width / 2 + pad_width[i] / 2, min(main_body_x + width / 2 - pad_width[i] / 2, cpw_positions[i][0]))
                pad_y = cpw_positions[i][1] + (pad_gap[i] if i < 3 else -pad_gap[i])
                
                # Create the pad shape (rectangle)
                pad = gdspy.Rectangle(
                    (pad_x - pad_width[i]/2, pad_y),
                    (pad_x + pad_width[i]/2, pad_y + pad_height[i]) if i < 3 else (pad_x + pad_width[i]/2, pad_y - pad_height[i])
                )
                self.cell_subtract.add(pad)

                # Calculate the direction angle (convert to radians if needed)
                if i == 0 or i == 3:  # Left CPW, direction left
                    direction_degrees = 180
                elif i == 1 or i == 4:  # Middle CPW, direction up or down
                    direction_degrees = 90 if i == 1 else -90
                else:  # Right CPW, direction right
                    direction_degrees = 0
                    
                direction_radians = np.radians(direction_degrees)
                
                # Create the CPW line
                # Calculate the start coordinates
                if i == 0 or i == 3:  # Upper left and lower left, start at the left boundary of the pad
                    cpw_start = [pad_x - pad_width[i]/2, pad_y + pad_height[i]/2] if i == 0 else [pad_x - pad_width[i]/2, pad_y - pad_height[i]/2]
                elif i == 1 or i == 4:  # Middle two, upper and lower boundaries
                    cpw_start = [pad_x, pad_y + pad_height[i]] if i == 1 else [pad_x, pad_y - pad_height[i]]
                else:  # Upper right and lower right, start at the right boundary of the pad
                    cpw_start = [pad_x + pad_width[i]/2, pad_y + pad_height[i]/2] if i == 2 else [pad_x + pad_width[i]/2, pad_y - pad_height[i]/2]

                cpw = gdspy.Path(cpw_width[i], cpw_start)
                cpw.segment(cpw_extend[i], direction=direction_radians)
                self.cell_subtract.add(cpw)

        self.cell_extract = self.lib.new_cell(self.name + "extract")

        indices = [i for i, value in enumerate(pad_options) if value == 1]
        max_extend_value = max(cpw_extend[i] for i in indices)
        max_pad_gap = max(pad_gap[i] for i in indices)
        max_pad_height = max(pad_height[i] for i in indices) 
        if sum(pad_options) == 0 or max_extend_value < subtract_gap:
            subtract_square = gdspy.Rectangle((main_body_x - width/2 - subtract_gap, main_body_y + height + gap/2 + subtract_gap),
                                              (main_body_x + width/2 + subtract_gap, main_body_y - height - gap/2 - subtract_gap))
            self.pocket_pos = [[main_body_x - width/2 - subtract_gap, main_body_y + height + gap/2 + subtract_gap],
                               [main_body_x + width/2 + subtract_gap, main_body_y - height - gap/2 - subtract_gap]]
        else:
            subtract_square = gdspy.Rectangle((main_body_x - width/2 - max_extend_value, main_body_y + height + gap/2 + max_extend_value + max_pad_gap + max_pad_height),
                                              (main_body_x + width/2 + max_extend_value, main_body_y - height - gap/2 - max_extend_value - max_pad_height - max_pad_gap))
            self.pocket_pos = [[main_body_x - width/2 - max_extend_value, main_body_y + height + gap/2 + max_extend_value + max_pad_gap + max_pad_height],
                               [main_body_x + width/2 + max_extend_value, main_body_y - height - gap/2 - max_extend_value - max_pad_height - max_pad_gap]]
        
        self.cell_extract.add(subtract_square)

        sub_poly = gdspy.boolean(self.cell_extract, self.cell_subtract, "not")

        self.cell = self.lib.new_cell(self.name + "_cell")
        self.cell.add(sub_poly)
        return