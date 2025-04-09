import gdspy
import math, copy
import numpy as np
from addict import Dict
from base.library_base import LibraryBase

class Smon0815(LibraryBase):
    default_options = Dict(
        # 框架
        name="Smon0815_01",
        type="Smon0815",
        chip="chip0",
        gds_pos = [0,0],
        topo_pos = [0,0],
        square_width = 650,
        pad_width = 485,
        pad_height = 90,
        gap = 30,
        small_pad_width = [73.5,30,73.5,73.5,30,73.5],
        small_pad_height = [4,30,10,10,30,10],
        small_pad_gap = [30,15,30,30,15,30],
        small_pad_angel = [39,0,39,39,0,39],
        small_pad_incline = [86.7,10,86.7,86.7,10,86.7], # 两重含义，四个角的斜长度，中间的宽度
        small_pad_end = [7,175,7,7,175,7], # 末尾长度 
        small_pad_offset = [180.5,0,180.5,180.5,0,180.5], # 偏移中心的距离
        small_pad_options = [0,0,0,0,0,0],
        coupling_pins = [],
        readout_pins = []

    )
    def __init__(self, options = Dict()):
        super().__init__(options)
        return
    
    def calc_general_ops(self):
        """
        需要计算以下参数
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

        return
    
    def draw_gds(self):  
        ################################ gdspy变量 ################################
        self.lib = gdspy.GdsLibrary()
        gdspy.library.use_current_library = False
        self.cell = self.lib.new_cell(self.name + "_cell")
    
        ################################ 接口 ################################
        # 接口存在的意义是，便于后续用户参数更新时的维护，可以只更新接口，接口下面的代码不用动。
        # 框架

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
        #pos[0]=pos[0]-square_width/2  #默认正中间是x,y 我画的最左下角是x,y 所以这里做了一个坐标转换
        #pos[1]=pos[1]-square_width/2
        
        square = gdspy.Rectangle((pos[0]-square_width/2,pos[1]-square_width/2), (pos[0]-square_width/2+square_width,pos[1]-square_width/2+square_width))

        upper_pad = gdspy.Rectangle((pos[0]-square_width/2+square_width/2-pad_width/2,pos[1]-square_width/2+square_width/2), (pos[0]-square_width/2+square_width/2+pad_width/2,pos[1]-square_width/2+square_width/2+pad_height + gap/2))
        circle0 = gdspy.Round((square_width/2+pos[0]-square_width/2, square_width/2+pos[1]-square_width/2), 60, tolerance=0.01)
        qubit1 = gdspy.boolean(upper_pad,circle0, "not")
        circle1 = gdspy.Round((square_width/2-90+pos[0]-square_width/2, square_width/2+pos[1]-square_width/2), 30, tolerance=0.01)
        qubit1 = gdspy.boolean(qubit1,circle1, "or")
        circle2 = gdspy.Round((square_width/2+90+pos[0]-square_width/2, square_width/2+pos[1]-square_width/2), 30, tolerance=0.01)
        qubit1 = gdspy.boolean(qubit1,circle2, "or")
        circle3 = gdspy.Round((square_width/2-90-90+pos[0]-square_width/2, square_width/2+pos[1]-square_width/2), 60, tolerance=0.01)
        qubit1 = gdspy.boolean(qubit1,circle3, "not")
        circle4 = gdspy.Round((square_width/2+90+90+pos[0]-square_width/2, square_width/2+pos[1]-square_width/2), 60, tolerance=0.01)
        upper_pad = gdspy.boolean(qubit1,circle4, "not")

        lower_pad = gdspy.Rectangle((pos[0]-square_width/2+square_width/2-pad_width/2,pos[1]-square_width/2+square_width/2-pad_height - gap/2), (pos[0]-square_width/2+square_width/2+pad_width/2,pos[1]-square_width/2+square_width/2))
        circle0 = gdspy.Round((square_width/2+pos[0]-square_width/2, square_width/2+pos[1]-square_width/2), 30, tolerance=0.01)
        qubit1 = gdspy.boolean(lower_pad,circle0, "or")
        circle1 = gdspy.Round((square_width/2-90+pos[0]-square_width/2, square_width/2+pos[1]-square_width/2), 60, tolerance=0.01)
        #qubit1 = gdspy.boolean(rect,circle1, "or")   
        qubit1 = gdspy.boolean(qubit1,circle1, "not")
        circle2 = gdspy.Round((square_width/2+90+pos[0]-square_width/2, square_width/2+pos[1]-square_width/2), 60, tolerance=0.01)
        qubit1 = gdspy.boolean(qubit1,circle2, "not")
        circle3 = gdspy.Round((square_width/2-90-90+pos[0]-square_width/2, square_width/2+pos[1]-square_width/2), 30, tolerance=0.01)
        qubit1 = gdspy.boolean(qubit1,circle3, "or")
        circle4 = gdspy.Round((square_width/2+90+90+pos[0]-square_width/2, square_width/2+pos[1]-square_width/2), 30, tolerance=0.01)
        qubit1 = gdspy.boolean(qubit1,circle4, "or")
        circle5 = gdspy.Round((square_width/2+90+90+90+pos[0]-square_width/2, square_width/2+pos[1]-square_width/2), 60, tolerance=0.01)
        qubit1 = gdspy.boolean(qubit1,circle5, "not")
        circle6 = gdspy.Round((square_width/2-90-90-90+pos[0]-square_width/2, square_width/2+pos[1]-square_width/2), 60, tolerance=0.01)
        lower_pad = gdspy.boolean(qubit1,circle6, "not")

        pad = gdspy.boolean(upper_pad, lower_pad, "or")

        smon = gdspy.boolean(square, pad, "not")
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
            smon = gdspy.boolean(smon, small_pad0, "not")
        if small_pad_options[2]!= 0:
            path_pos2 = [(pos[0]+small_pad_offset[2],pos[1]+gap/2+pad_height+small_pad_height[2]/2+small_pad_gap[2]),                    
                        (pos[0]+small_pad_offset[2]+small_pad_width[2],pos[1]+gap/2+pad_height+small_pad_height[2]/2+small_pad_gap[2]),
                        (pos[0]+small_pad_offset[2]+small_pad_width[2]+small_pad_incline[2]*math.cos(math.radians(small_pad_angel[2])),pos[1]+gap/2+pad_height+small_pad_height[2]/2+small_pad_gap[2]+small_pad_incline[2]*math.sin(math.radians(small_pad_angel[2]))),
                        (pos[0]+small_pad_offset[2]+small_pad_width[2]+small_pad_incline[2]*math.cos(math.radians(small_pad_angel[2]))+small_pad_end[2],pos[1]+gap/2+pad_height+small_pad_height[2]/2+small_pad_gap[2]+small_pad_incline[2]*math.sin(math.radians(small_pad_angel[2])))]
            small_pad2 = gdspy.FlexPath(path_pos2,small_pad_height[2])
            smon = gdspy.boolean(smon, small_pad2, "not")
        if small_pad_options[3] != 0:
            path_pos3 = [(pos[0]-small_pad_offset[3],pos[1]-gap/2-pad_height-small_pad_height[3]/2-small_pad_gap[3]),
                        (pos[0]-small_pad_offset[3]-small_pad_width[3],pos[1]-gap/2-pad_height-small_pad_height[3]/2-small_pad_gap[3]),
                        (pos[0]-small_pad_offset[3]-small_pad_width[3]-small_pad_incline[3]*math.cos(math.radians(small_pad_angel[3])),pos[1]-gap/2-pad_height-small_pad_height[3]/2-small_pad_gap[3]-small_pad_incline[3]*math.sin(math.radians(small_pad_angel[3]))),
                        (pos[0]-small_pad_offset[3]-small_pad_width[3]-small_pad_incline[3]*math.cos(math.radians(small_pad_angel[3]))-small_pad_end[3],pos[1]-gap/2-pad_height-small_pad_height[3]/2-small_pad_gap[3]-small_pad_incline[3]*math.sin(math.radians(small_pad_angel[3])))]
            small_pad3 = gdspy.FlexPath(path_pos3,small_pad_height[3])
            smon = gdspy.boolean(smon, small_pad3, "not")
        if small_pad_options[5] != 0:
            path_pos5 = [(pos[0]+small_pad_offset[5],pos[1]-gap/2-pad_height-small_pad_height[5]/2-small_pad_gap[5]),
                        (pos[0]+small_pad_offset[5]+small_pad_width[5],pos[1]-gap/2-pad_height-small_pad_height[5]/2-small_pad_gap[5]),
                        (pos[0]+small_pad_offset[5]+small_pad_width[5]+small_pad_incline[5]*math.cos(math.radians(small_pad_angel[5])),pos[1]-gap/2-pad_height-small_pad_height[5]/2-small_pad_gap[5]-small_pad_incline[5]*math.sin(math.radians(small_pad_angel[5]))),
                        (pos[0]+small_pad_offset[5]+small_pad_width[5]+small_pad_incline[5]*math.cos(math.radians(small_pad_angel[5]))+small_pad_end[5],pos[1]-gap/2-pad_height-small_pad_height[5]/2-small_pad_gap[5]-small_pad_incline[5]*math.sin(math.radians(small_pad_angel[5])))]
            small_pad5 = gdspy.FlexPath(path_pos5,small_pad_height[5])
            smon = gdspy.boolean(smon, small_pad5, "not")
        

        if small_pad_options[1] != 0:
            rec = gdspy.Rectangle((pos[0]-small_pad_width[1]/2,pos[1]+gap/2+pad_height+small_pad_gap[1]), 
                                  (pos[0]+small_pad_width[1]/2,pos[1]+gap/2+pad_height+small_pad_height[1]+small_pad_gap[1]))
            line = gdspy.Path(small_pad_incline[1],(pos[0],pos[1]+gap/2+pad_height+small_pad_height[1]+small_pad_gap[1]))
            line.segment(small_pad_end[1], direction='+y')
            small_pad2 = gdspy.boolean(rec, line, "or")
            smon = gdspy.boolean(smon, small_pad2, "not")
        if small_pad_options[4] != 0:
            rec = gdspy.Rectangle((pos[0]-small_pad_width[4]/2,pos[1]-gap/2-pad_height-small_pad_gap[4]), 
                                  (pos[0]+small_pad_width[4]/2,pos[1]-gap/2-pad_height-small_pad_height[4]-small_pad_gap[4]))
            line = gdspy.Path(small_pad_incline[4],(pos[0],pos[1]-gap/2-pad_height-small_pad_height[4]-small_pad_gap[4]))
            line.segment(small_pad_end[4], direction='-y')
            small_pad3 = gdspy.boolean(rec, line, "or")
            smon = gdspy.boolean(smon, small_pad3, "not")
            

        self.cell.add(smon)



        return