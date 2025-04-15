############################################################################################
# File Name: launch_pad.py
# Description: This file primarily contains functions for constructing and drawing pin devices, 
#              supporting the generation of pin geometric shapes in GDS format.
############################################################################################

import gdspy
import math
import numpy as np
from addict import Dict
from base.library_base import LibraryBase

class LaunchPad(LibraryBase):
    default_options = Dict(
        # Framework
        name = "pin0",
        type = "LaunchPad",
        chip = "chip0",
        pos=(0, 0),
        outline = [],
        # Geometric parameters
        trace_width=15,
        trace_gap=5,
        taper_height=120,
        pad_width=120,
        pad_height=125,
        pad_gap=100,
        orientation=0,
        start_straight=50,
        distance_to_chip=350,
        distance_to_qubits=3650
    )
    
    def __init__(self, options: Dict = None):
        super().__init__(options)
        return

    def calc_general_ops(self):
        # self.outline = [...]
        return

    def draw_gds(self):
        """
        Draw the geometric shape of the pin and add it to the GDS cell.

        Output:
        List[gdspy.Polygon]: A list containing polygons representing the pin.
        """

        # Interfaces
        import copy
        name = self.name
        type = self.type
        chip = self.chip
        pos = copy.deepcopy(self.pos)
        outline = copy.deepcopy(self.outline)
        trace_width = self.trace_width
        trace_gap = self.trace_gap
        taper_height = self.taper_height
        pad_width = self.pad_width
        pad_height = self.pad_height
        pad_gap = self.pad_gap
        orientation = self.orientation
        start_straight = self.start_straight
        distance_to_chip = self.distance_to_chip
        distance_to_qubits = self.distance_to_qubits

        # Drawing
        self.lib = gdspy.GdsLibrary()
        gdspy.library.use_current_library = False
        self.cell_subtract = self.lib.new_cell(name + "_subtract")

        points = [(pos[0] - trace_width/2, pos[1]), 
                    (pos[0] + trace_width/2, pos[1]), 
                    (pos[0] + pad_width/2, pos[1] + taper_height), 
                    (pos[0] + pad_width/2,pos[1] + taper_height + pad_height),
                    (pos[0] - pad_width/2, pos[1] + taper_height + pad_height),
                    (pos[0] - pad_width/2, pos[1] + taper_height)
                ]

        polygon = gdspy.Polygon(points)
        polygon.rotate(math.radians(orientation), pos)
        self.cell_subtract.add(polygon)

        self.cell_extract = self.lib.new_cell(name + "_extract")
        points = [(pos[0] + trace_width/2 + trace_gap, pos[1]),
                    (pos[0] + pad_width/2 + pad_gap, pos[1] + taper_height), 
                    (pos[0] + pad_width/2 + pad_gap, pos[1] + taper_height + pad_height + pad_gap),
                    (pos[0] - pad_width/2 - pad_gap, pos[1] + taper_height + pad_height + pad_gap),
                    (pos[0] - pad_width/2 - pad_gap, pos[1] + taper_height),
                    (pos[0] - trace_width/2 - trace_gap, pos[1])
                ]
        
        path = gdspy.Polygon(points,0.1)
        path.rotate(math.radians(orientation), pos)
        self.cell_extract.add(path)

        sub_ploy = gdspy.boolean(self.cell_extract, self.cell_subtract, "not")
        self.cell = self.lib.new_cell(name + "_cell")
        self.cell.add(sub_ploy)
        return