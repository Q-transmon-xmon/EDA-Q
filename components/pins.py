from base.cmpnts_base import CmpntsBase
from addict import Dict
import func_modules
import copy

class Pins(CmpntsBase):
    def __init__(self, **init_ops):
        self.initialization(**init_ops)
        return
    
    def initialization(self, **init_ops):
        # Component List
        self.cmpnt_name_list = []
        # initialization
        options = func_modules.pins.generate_pins(**init_ops)
        self.inject_options(options)
        return
    
    def mirror_LaunchPad(self, name_list):
        # Mirror horizontally
        pins_ops = self.options
        for name in name_list:
            ops = copy.deepcopy(pins_ops[name])
            new_ops = copy.deepcopy(ops)

            new_name = name + "_mirror" 
            new_ops.name = new_name
            
            pos = copy.deepcopy(ops.pos)
            new_pos = (-pos[0], pos[1])
            new_ops.pos = copy.deepcopy(new_pos)

            orientation = ops.orientation
            new_orientation = -orientation
            new_ops.orientation = new_orientation

            pins_ops[new_name] = copy.deepcopy(new_ops)
        
        self.inject_options(pins_ops)
        return