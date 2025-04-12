#########################################################################
# File name: xmon.py
# Description: Defines the configuration and behavior of the Xmon qubit.
#              This class inherits from LibraryBase and is used to describe
#              the parameters and methods of the Xmon qubit.
#########################################################################
from addict import Dict
from base.library_base import LibraryBase
import toolbox
import copy, gdspy, numpy as np

class Xmon(LibraryBase):
    default_options = Dict(
        # Framework
        name = "q0",
        type = "Xmon",
        gds_pos = (0, 0),
        topo_pos = (0, 0),
        chip = "chip0",
        readout_pins = [],
        control_pins = [],
        coupling_pins = [],
        outline = [],
        # Dimension parameters
        cross_width=10,
        cross_height=300,
        cross_gap=20,
        connect_pad_options=[1,1,1,1], # Whether small pads are displayed
        claw_length = 30,
        ground_spacing = 5,
        claw_width = 10,
        claw_gap = 6
    )
    
    def __init__(self, options = Dict()):
        """
        Initializes the Xmon class.
        
        Input:
            options: Dictionary containing component parameter options.
        """
        super().__init__(options)
        return
    
    def calc_general_ops(self):
        """
        Generates coupling_pins, readout_pins, control_pins, and outline.
        """
        
        """
        Generate coupling_pins, readout_pins, control_pins
        self.coupling_pins.top = ...
        self.coupling_pins.bot = ...
        self.coupling_pins.left = ...
        self.coupling_pins.right = ...
        self.readout_pins.append(...)    # Append a coordinate, represented as a list, e.g., [0, 0]
        self.control_pins.append(...)
        self.outline = ...
        """
        
        x = self.gds_pos[0]
        y = self.gds_pos[1]
        gds_pos = (x, y)
        cross_height = self.cross_height
        pad_ops = self.connect_pad_options
        ground_spacing = self.ground_spacing
        claw_width = self.claw_width
        claw_gap = self.claw_gap
        claw_length = self.claw_length

        self.readout_pins = []
        self.control_pins = []
        self.coupling_pins = []
        self.outline = []

        self.coupling_pins.append((gds_pos[0], gds_pos[1] + cross_height + ground_spacing + claw_gap + claw_width + claw_length))
        self.coupling_pins.append((gds_pos[0], gds_pos[1] - cross_height - ground_spacing - claw_gap - claw_width - claw_length))
        self.coupling_pins.append((gds_pos[0] - cross_height - ground_spacing - claw_gap - claw_width - claw_length, gds_pos[1]))
        self.coupling_pins.append((gds_pos[0] + cross_height + ground_spacing + claw_gap + claw_width + claw_length, gds_pos[1]))
        self.readout_pins.append((gds_pos[0]+50, gds_pos[1]+50))
        self.control_pins.append(gds_pos)

        self.outline = [[gds_pos[0] - cross_height - ground_spacing - claw_gap - claw_width - claw_length,
                                   gds_pos[1] - cross_height - ground_spacing - claw_gap - claw_width - claw_length],
                                  [gds_pos[0] + cross_height + ground_spacing + claw_gap + claw_width + claw_length,
                                   gds_pos[1] - cross_height - ground_spacing - claw_gap - claw_width - claw_length],
                                  [gds_pos[0] + cross_height + ground_spacing + claw_gap + claw_width + claw_length,
                                   gds_pos[1] + cross_height + ground_spacing + claw_gap + claw_width + claw_length],
                                  [gds_pos[0] - cross_height - ground_spacing - claw_gap - claw_width - claw_length,
                                   gds_pos[1] + cross_height + ground_spacing + claw_gap + claw_width + claw_length],
                                  [gds_pos[0] - cross_height - ground_spacing - claw_gap - claw_width - claw_length,
                                   gds_pos[1] - cross_height - ground_spacing - claw_gap - claw_width - claw_length]]
        return

    def draw_gds(self):
        """
        Draws the geometric shapes of the qubit and adds them to the GDS cell.
        """
        # gdspy variables
        gdspy.library.use_current_library = False
        self.lib = gdspy.GdsLibrary()
        self.cell = self.lib.new_cell(self.name)
        
        ################################ Drawing ##################################
        x = self.gds_pos[0] - self.cross_height - self.cross_width / 2
        y = self.gds_pos[1] - self.cross_width / 2
        width = self.options.cross_width
        height = self.options.cross_height
        gap = self.options.cross_gap
        cl = self.options.claw_length
        gs = self.options.ground_spacing
        cw = self.options.claw_width
        cg = self.options.claw_gap
        in_s = (cl * 2 + cw - width - gap * 2) / 2

        a = self.options.connect_pad_options[0]
        b = self.options.connect_pad_options[1]
        c = self.options.connect_pad_options[2]
        d = self.options.connect_pad_options[3]
       
        x1 = -gap - gs
        y1 = width + gap + in_s
        x2 = height * 2 + width + gap + gs
        y2 = width + gap + in_s
        x3 = height - gap - in_s
        y3 = width + gap + height + gs
        x4 = height + gap + width + in_s
        y4 = -height - gap - gs

        qubit = gdspy.Curve(x, y).l(height, 0, height, -height, height + width, -height, height + width, 0, height * 2 + width, 0, height * 2 + width, width, height + width, width, height + width, height + width, height, height + width, height, width, 0, width,
                                  -gap, width + gap,
                                  -gap + height, width + gap, -gap + height, width + gap + height,
                                  width + gap + height, width + gap + height,
                                  width + gap + height, width + gap, width + gap + height * 2, width + gap,
                                  width + gap + height * 2, -gap, width + gap + height, -gap,
                                  width + gap + height, -gap - height,
                                  height - gap, -gap - height, height - gap, -gap, -gap, -gap, -gap, gap + width, 0, width,
                                  (-gap) * c, (width + gap) * c,
                                  (x1) * c, (y1) * c, (x1 + cl) * c, (y1) * c, (x1 + cl) * c, (y1 + cw + cg * 2) * c, (x1 - cg - cg - cw) * c, (y1 + cw + cg + cg) * c, (x1 - cg - cg - cw) * c, (y1 + cg - cl) * c,
                                  (x1 - cg - cw - cl) * c, (y1 + cg - cl) * c, (x1 - cg - cw - cl) * c, (y1 - cl - cw - cg) * c, (x1 - cg - cg - cw) * c, (y1 - cl - cw - cg) * c, (x1 - cg - cg - cw) * c, (y1 - cl - cl - cw - cw - cg - cg) * c,
                                  (x1 + cl) * c, (y1 - cl - cl - cw - cw - cg - cg) * c, (x1 + cl) * c, (y1 - cl - cl - cw) * c, (x1) * c, (y1 - cl - cl - cw) * c, (x1 - cg) * c, (y1 - cl - cl - cg - cw) * c, (x1 - cg + cl) * c, (y1 - cl - cl - cg - cw) * c,
                                  (x1 - cg + cl) * c, (y1 - cl - cl - cg - cw * 2) * c, (x1 - cg - cw) * c, (y1 - cl - cl - cg - cw * 2) * c, (x1 - cg - cw) * c, (y1 - cl - cw) * c, (x1 - cg - cw - cl) * c, (y1 - cl - cw) * c, (x1 - cg - cw - cl) * c, (y1 - cl) * c,
                                  (x1 - cg - cw) * c, (y1 - cl) * c, (x1 - cg - cw) * c, (y1 + cg + cw) * c, (x1 - cg + cl) * c, (y1 + cg + cw) * c, (x1 - cg + cl) * c, (y1 + cg) * c, (x1 - cg) * c, (y1 + cg) * c,
                                  (x1 - cg) * c, (y1 - cl - cl - cg - cw) * c, (x1) * c, (y1 - cl - cl - cw) * c, (x1) * c, (y1) * c, (-gap) * c, (width + gap) * c, 0, (width) * c,
                                  (-gap) * b, (width + gap) * b, (-gap + height) * b, (width + gap) * b, (-gap + height) * b, (width + gap + height) * b,
                                  (x3) * b, (y3) * b, (x3 + cl * 2 + cw) * b, (y3) * b, (x3 + cl * 2 + cw) * b, (y3 - cl) * b, (x3 + cl * 2 + cw * 2 + cg * 2) * b, (y3 - cl) * b,
                                  (x3 + cl * 2 + cw * 2 + cg * 2) * b, (y3 + cw + cg * 2) * b, (x3 + cl + cw + cg) * b, (y3 + cw + cg * 2) * b, (x3 + cl + cw + cg) * b, (y3 + cl + cw + cg) * b, (x3 + cl - cg) * b, (y3 + cw + cl + cg) * b,
                                  (x3 + cl - cg) * b, (y3 + cw + cg * 2) * b, (x3 - cw - cg * 2) * b, (y3 + cw + cg * 2) * b, (x3 - cw - cg * 2) * b, (y3 - cl) * b, (x3) * b, (y3 - cl) * b,
                                  (x3 - cg) * b, (y3 - cl + cg) * b, (x3 - cg - cw) * b, (y3 - cl + cg) * b, (x3 - cg - cw) * b, (y3 + cw + cg) * b, (x3 + cl) * b, (y3 + cw + cg) * b,
                                  (x3 + cl) * b, (y3 + cl + cg + cw) * b, (x3 + cl + cw) * b, (y3 + cl + cg + cw) * b, (x3 + cl + cw) * b, (y3 + cw + cg) * b, (x3 + cl * 2 + cw * 2 + cg) * b, (y3 + cw + cg) * b,
                                  (x3 + cl * 2 + cw * 2 + cg) * b, (y3 - cl + cg) * b, (x3 + cl * 2 + cw + cg) * b, (y3 - cl + cg) * b, (x3 + cl * 2 + cw + cg) * b, (y3 + cg) * b,
                                  (x3 - cg) * b, (y3 + cg) * b, (x3 - cg) * b, (y3 - cl + cg) * b, (x3) * b, (y3 - cl) * b, (x3) * b, (y3) * b,
                                  (-gap + height) * b, (width + gap + height) * b, (-gap + height) * b, (width + gap) * b, (-gap) * b, (width + gap) * b, 0, (width) * b,
                                  (-gap) * a, (width + gap) * a, (-gap + height) * a, (width + gap) * a, (-gap + height) * a, (width + gap + height) * a,
                                  (width + gap + height) * a, (width + gap + height) * a, (width + gap + height) * a, (width + gap) * a, (width + gap + height * 2) * a, (width + gap) * a,
                                  (x2) * a, (y2) * a, (x2) * a, (y2 - cl * 2 - cw) * a, (x2 - cl) * a, (y2 - cl * 2 - cw) * a, (x2 - cl) * a, (y2 - cl * 2 - cg * 2 - cw * 2) * a, (x2 + cg * 2 + cw) * a, (y2 - cl * 2 - cg * 2 - cw * 2) * a,
                                  (x2 + cg * 2 + cw) * a, (y2 - cl - cw - cg) * a, (x2 + cg + cw + cl) * a, (y2 - cl - cg - cw) * a, (x2 + cg + cw + cl) * a, (y2 - cl + cg) * a,
                                  (x2 + cg * 2 + cw) * a, (y2 - cl + cg) * a, (x2 + cg * 2 + cw) * a, (y2 + cg * 2 + cw) * a, (x2 - cl) * a, (y2 + cg * 2 + cw) * a,
                                  (x2 - cl) * a, (y2) * a, (x2 - cl + cg) * a, (y2 + cg) * a, (x2 - cl + cg) * a, (y2 + cg + cw) * a, (x2 + cg + cw) * a, (y2 + cg + cw) * a, (x2 + cg + cw) * a, (y2 - cl) * a,
                                  (x2 + cg + cw + cl) * a, (y2 - cl) * a, (x2 + cg + cw + cl) * a, (y2 - cl - cw) * a, (x2 + cg + cw) * a, (y2 - cl - cw) * a, (x2 + cg + cw) * a, (y2 - cl * 2 - cw * 2 - cg) * a,
                                  (x2 + cg - cl) * a, (y2 - cl * 2 - cw * 2 - cg) * a, (x2 + cg - cl) * a, (y2 - cl * 2 - cw - cg) * a, (x2 + cg) * a, (y2 - cl * 2 - cw - cg) * a, (x2 + cg) * a, (y2 + cg) * a,
                                  (x2 + cg - cl) * a, (y2 + cg) * a, (x2 - cl) * a, (y2) * a, (x2) * a, (y2) * a,
                                  (width + gap + height * 2) * a, (width + gap) * a, (width + gap + height) * a, (width + gap) * a, (width + gap + height) * a, (width + gap + height) * a,
                                  (-gap + height) * a, (width + gap + height) * a, (-gap + height) * a, (width + gap) * a, (-gap) * a, (width + gap) * a, 0, (width) * a,
                                  (-gap) * d, (width + gap) * d, (-gap + height) * d, (width + gap) * d, (-gap + height) * d, (width + gap + height) * d,
                                  (width + gap + height) * d, (width + gap + height) * d, (width + gap + height) * d, (width + gap) * d, (width + gap + height * 2) * d, (width + gap) * d,
                                  (width + gap + height * 2) * d, (-gap) * d, (width + gap + height) * d, (-gap) * d, (width + gap + height) * d, (-gap - height) * d,
                                  (x4) * d, (y4) * d, (x4 - cl * 2 - cw) * d, (y4) * d, (x4 - cl * 2 - cw) * d, (y4 + cl) * d, (x4 - cl * 2 - cw * 2 - cg * 2) * d, (y4 + cl) * d, (x4 - cl * 2 - cw * 2 - cg * 2) * d, (y4 - cg * 2 - cw) * d,
                                  (x4 - cl - cw - cg) * d, (y4 - cg * 2 - cw) * d, (x4 - cl - cw - cg) * d, (y4 - cg - cw - cl) * d, (x4 - cl + cg) * d, (y4 - cg - cw - cl) * d, (x4 - cl + cg) * d, (y4 - cg * 2 - cw) * d,
                                  (x4 + cw + cg * 2) * d, (y4 - cg * 2 - cw) * d, (x4 + cw + cg * 2) * d, (y4 + cl) * d, (x4) * d, (y4 + cl) * d, (x4 + cg) * d, (y4 + cl - cg) * d, (x4 + cg + cw) * d, (y4 + cl - cg) * d,
                                  (x4 + cg + cw) * d, (y4 - cg - cw) * d, (x4 - cl) * d, (y4 - cg - cw) * d, (x4 - cl) * d, (y4 - cg - cw - cl) * d, (x4 - cl - cw) * d, (y4 - cg - cw - cl) * d,
                                  (x4 - cl - cw) * d, (y4 - cg - cw) * d, (x4 - cl * 2 - cw * 2 - cg) * d, (y4 - cg - cw) * d, (x4 - cl * 2 - cw * 2 - cg) * d, (y4 - cg + cl) * d,
                                  (x4 - cl * 2 - cw - cg) * d, (y4 - cg + cl) * d, (x4 - cl * 2 - cw - cg) * d, (y4 - cg) * d, (x4 + cg) * d, (y4 - cg) * d, (x4 + cg) * d, (y4 + cl - cg) * d,
                                  (x4) * d, (y4 + cl) * d, (x4) * d, (y4) * d,
                                  (width + gap + height) * d, (-gap - height) * d, (width + gap + height) * d, (-gap) * d, (width + gap + height * 2) * d, (-gap) * d,
                                  (width + gap + height * 2) * d, (width + gap) * d, (width + gap + height) * d, (width + gap) * d, (width + gap + height) * d, (width + gap + height) * d,
                                  (-gap + height) * d, (width + gap + height) * d, (-gap + height) * d, (width + gap) * d, (-gap) * d, (width + gap) * d, 0, (width) * d,
                                  )
        self.cell.add([gdspy.Polygon(qubit.get_points())])
        ########################################################################
        return
    
    def move(self, dx, dy):
        """
        Moves the qubit's position.
        
        Input:
            dx: Distance to move in the x direction.
            dy: Distance to move in the y direction.
        """
        gds_pos = copy.deepcopy(self.gds_pos)
        x = gds_pos[0]
        y = gds_pos[1]
        self.gds_pos = (x + dx, y + dy)
        self.calc_general_ops()