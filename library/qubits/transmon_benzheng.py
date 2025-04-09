#########################################################################
# File Name: transmon_benzheng.py
# Description: Defines the TransmonBenzheng class, which is used to draw the geometric structure of a superconducting qubit and generate elements in a GDS design database.
#              Includes qubit parameter settings, pin calculations, and geometric shape drawing functions.
#########################################################################
import gdspy
import math, copy
import numpy as np
from addict import Dict
from base.library_base import LibraryBase

class TransmonBenzheng(LibraryBase):
    default_options = Dict(
        # Framework
        name="TransmonBenzheng0",
        type="TransmonBenzheng",
        chip="chip0",
        gds_pos = [0,0],
        topo_pos = [0,0],
        square_width = 650,
        pad_width = 455,
        pad_height = 90,
        gap = 30,
        small_pad_width = [73.5,30,73.5,73.5,30,73.5],
        small_pad_height = [4,30,10,10,30,10],
        small_pad_gap = [30,15,30,30,15,30],
        small_pad_angel = [39,0,39,39,0,39],
        small_pad_incline = [86.7,10,86.7,86.7,10,86.7], # Dual meaning, the slant length of the four corners, the width in the middle
        small_pad_end = [7,175,7,7,175,7], # End length
        small_pad_offset = [180.5,0,180.5,180.5,0,180.5], # Offset from the center
        small_pad_options = [0,0,0,0,0,0],
        coupling_pins = [],
        readout_pins = []
    )
    
    def __init__(self, options = Dict()):
        """
        Initializes the TransmonBenzheng class.
        
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
        pos = self.options.gds_pos
        topo_pos = self.options.topo_pos
        square_width = self.options.square_width
        pad_width = self.options.pad_width
        pad_height = self.options.pad_height
        gap = self.options.gap
        small_pad_width = self.options.small_pad_width
        small_pad_height = self.options.small_pad_height
        small_pad_gap = self.options.small_pad_gap
        small_pad_incline = self.options.small_pad_incline
        small_pad_end = self.options.small_pad_end
        small_pad_angel = self.options.small_pad_angel
        small_pad_offset = self.options.small_pad_offset
        small_pad_options = self.options.small_pad_options

        self.coupling_pins = []
        self.coupling_pins.append((pos[0]-square_width/2,pos[1]-gap/2-pad_height-small_pad_height[3]/2-small_pad_gap[3]-small_pad_incline[3]*math.sin(math.radians(small_pad_angel[3]))))
        self.coupling_pins.append((pos[0]+square_width/2,pos[1]-gap/2-pad_height-small_pad_height[5]/2-small_pad_gap[5]-small_pad_incline[5]*math.sin(math.radians(small_pad_angel[5]))))
        self.coupling_pins.append((pos[0],pos[1]+square_width/2))
        self.coupling_pins.append((pos[0],pos[1]-square_width/2))
        self.readout_pins = []
        self.readout_pins.append((pos[0]-square_width/2,pos[1]+gap/2+pad_height+small_pad_height[0]/2+small_pad_gap[0]+small_pad_incline[0]*math.sin(math.radians(small_pad_angel[0]))))
        self.readout_pins.append((pos[0]+square_width/2,pos[1]+gap/2+pad_height+small_pad_height[0]/2+small_pad_gap[0]+small_pad_incline[0]*math.sin(math.radians(small_pad_angel[0]))))

        return
    
    def draw_gds(self):  
        ################################ gdspy variables ################################
        self.lib = gdspy.GdsLibrary()
        gdspy.library.use_current_library = False
        self.cell = self.lib.new_cell(self.name + "_cell")
    
        ################################ Interface ################################
        # The purpose of the interface is to facilitate subsequent user parameter updates. Only the interface needs to be updated, and the code below the interface does not need to be changed.
        # Framework

        pos = self.options.gds_pos
        square_width = self.options.square_width
        pad_width = self.options.pad_width
        pad_height = self.options.pad_height
        gap = self.options.gap
        small_pad_width = self.options.small_pad_width
        small_pad_height = self.options.small_pad_height
        small_pad_gap = self.options.small_pad_gap
        small_pad_incline = self.options.small_pad_incline
        small_pad_end = self.options.small_pad_end
        small_pad_angel = self.options.small_pad_angel
        small_pad_offset = self.options.small_pad_offset
        small_pad_options = self.options.small_pad_options

        square = gdspy.Rectangle((pos[0]-square_width/2,pos[1]-square_width/2), (pos[0]+square_width/2,pos[1]+square_width/2))
        upper_pad = gdspy.Rectangle((pos[0]-pad_width/2,pos[1]+gap/2), (pos[0]+pad_width/2,pos[1]+pad_height + gap/2))
        lower_pad = gdspy.Rectangle((pos[0]-pad_width/2,pos[1]-pad_height - gap/2), (pos[0]+pad_width/2,pos[1]-gap/2))
        pad = gdspy.boolean(upper_pad, lower_pad, "or")

        transmon = gdspy.boolean(square, pad, "not")
        small_pad_end = [square_width/2-small_pad_offset[0]-small_pad_width[0]-small_pad_incline[0]*math.cos(math.radians(small_pad_angel[0])),
                         square_width/2-gap/2-pad_height-small_pad_gap[1]-small_pad_height[1],
                         square_width/2-small_pad_offset[2]-small_pad_width[2]-small_pad_incline[2]*math.cos(math.radians(small_pad_angel[2])),
                         square_width/2-small_pad_offset[3]-small_pad_width[3]-small_pad_incline[3]*math.cos(math.radians(small_pad_angel[3])),
                         square_width/2-gap/2-pad_height-small_pad_gap[4]-small_pad_height[4],
                         square_width/2-small_pad_offset[5]-small_pad_width[5]-small_pad_incline[5]*math.cos(math.radians(small_pad_angel[5]))]
        
        if small_pad_options[0]!= 0:
            path_pos0 = [(pos[0]-small_pad_offset[0],pos[1]+gap/2+pad_height+small_pad_height[0]/2+small_pad_gap[0]),
                        (pos[0]-small_pad_offset[0]-small_pad_width[0],pos[1]+gap/2+pad_height+small_pad_height[0]/2+small_pad_gap[0]),
                        (pos[0]-small_pad_offset[0]-small_pad_width[0]-small_pad_incline[0]*math.cos(math.radians(small_pad_angel[0])),pos[1]+gap/2+pad_height+small_pad_height[0]/2+small_pad_gap[0]+small_pad_incline[0]*math.sin(math.radians(small_pad_angel[0]))),
                        (pos[0]-small_pad_offset[0]-small_pad_width[0]-small_pad_incline[0]*math.cos(math.radians(small_pad_angel[0]))-small_pad_end[0],pos[1]+gap/2+pad_height+small_pad_height[0]/2+small_pad_gap[0]+small_pad_incline[0]*math.sin(math.radians(small_pad_angel[0])))]
            small_pad0 = gdspy.FlexPath(path_pos0,small_pad_height[0])
            transmon = gdspy.boolean(transmon, small_pad0, "not")
        if small_pad_options[2]!= 0:
            path_pos2 = [(pos[0]+small_pad_offset[2],pos[1]+gap/2+pad_height+small_pad_height[2]/2+small_pad_gap[2]),                    
                        (pos[0]+small_pad_offset[2]+small_pad_width[2],pos[1]+gap/2+pad_height+small_pad_height[2]/2+small_pad_gap[2]),
                        (pos[0]+small_pad_offset[2]+small_pad_width[2]+small_pad_incline[2]*math.cos(math.radians(small_pad_angel[2])),pos[1]+gap/2+pad_height+small_pad_height[2]/2+small_pad_gap[2]+small_pad_incline[2]*math.sin(math.radians(small_pad_angel[2]))),
                        (pos[0]+small_pad_offset[2]+small_pad_width[2]+small_pad_incline[2]*math.cos(math.radians(small_pad_angel[2]))+small_pad_end[2],pos[1]+gap/2+pad_height+small_pad_height[2]/2+small_pad_gap[2]+small_pad_incline[2]*math.sin(math.radians(small_pad_angel[2])))]
            small_pad2 = gdspy.FlexPath(path_pos2,small_pad_height[2])
            transmon = gdspy.boolean(transmon, small_pad2, "not")
        if small_pad_options[3] != 0:
            path_pos3 = [(pos[0]-small_pad_offset[3],pos[1]-gap/2-pad_height-small_pad_height[3]/2-small_pad_gap[3]),
                        (pos[0]-small_pad_offset[3]-small_pad_width[3],pos[1]-gap/2-pad_height-small_pad_height[3]/2-small_pad_gap[3]),
                        (pos[0]-small_pad_offset[3]-small_pad_width[3]-small_pad_incline[3]*math.cos(math.radians(small_pad_angel[3])),pos[1]-gap/2-pad_height-small_pad_height[3]/2-small_pad_gap[3]-small_pad_incline[3]*math.sin(math.radians(small_pad_angel[3]))),
                        (pos[0]-small_pad_offset[3]-small_pad_width[3]-small_pad_incline[3]*math.cos(math.radians(small_pad_angel[3]))-small_pad_end[3],pos[1]-gap/2-pad_height-small_pad_height[3]/2-small_pad_gap[3]-small_pad_incline[3]*math.sin(math.radians(small_pad_angel[3])))]
            small_pad3 = gdspy.FlexPath(path_pos3,small_pad_height[3])
            transmon = gdspy.boolean(transmon, small_pad3, "not")
        if small_pad_options[5] != 0:
            path_pos5 = [(pos[0]+small_pad_offset[5],pos[1]-gap/2-pad_height-small_pad_height[5]/2-small_pad_gap[5]),
                        (pos[0]+small_pad_offset[5]+small_pad_width[5],pos[1]-gap/2-pad_height-small_pad_height[5]/2-small_pad_gap[5]),
                        (pos[0]+small_pad_offset[5]+small_pad_width[5]+small_pad_incline[5]*math.cos(math.radians(small_pad_angel[5])),pos[1]-gap/2-pad_height-small_pad_height[5]/2-small_pad_gap[5]-small_pad_incline[5]*math.sin(math.radians(small_pad_angel[5]))),
                        (pos[0]+small_pad_offset[5]+small_pad_width[5]+small_pad_incline[5]*math.cos(math.radians(small_pad_angel[5]))+small_pad_end[5],pos[1]-gap/2-pad_height-small_pad_height[5]/2-small_pad_gap[5]-small_pad_incline[5]*math.sin(math.radians(small_pad_angel[5])))]
            small_pad5 = gdspy.FlexPath(path_pos5,small_pad_height[5])
            transmon = gdspy.boolean(transmon, small_pad5, "not")
        
        if small_pad_options[1] != 0:
            rec = gdspy.Rectangle((pos[0]-small_pad_width[1]/2,pos[1]+gap/2+pad_height+small_pad_gap[1]), 
                                  (pos[0]+small_pad_width[1]/2,pos[1]+gap/2+pad_height+small_pad_height[1]+small_pad_gap[1]))
            line = gdspy.Path(small_pad_incline[1],(pos[0],pos[1]+gap/2+pad_height+small_pad_height[1]+small_pad_gap[1]))
            line.segment(small_pad_end[1], direction='+y')
            small_pad2 = gdspy.boolean(rec, line, "or")
            transmon = gdspy.boolean(transmon, small_pad2, "not")
        if small_pad_options[4] != 0:
            rec = gdspy.Rectangle((pos[0]-small_pad_width[4]/2,pos[1]-gap/2-pad_height-small_pad_gap[4]), 
                                  (pos[0]+small_pad_width[4]/2,pos[1]-gap/2-pad_height-small_pad_height[4]-small_pad_gap[4]))
            line = gdspy.Path(small_pad_incline[4],(pos[0],pos[1]-gap/2-pad_height-small_pad_height[4]-small_pad_gap[4]))
            line.segment(small_pad_end[4], direction='-y')
            small_pad3 = gdspy.boolean(rec, line, "or")
            transmon = gdspy.boolean(transmon, small_pad3, "not")
            
        self.cell.add(transmon)

        return