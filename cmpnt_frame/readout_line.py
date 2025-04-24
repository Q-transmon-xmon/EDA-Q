from addict import Dict
from base.library_base import LibraryBase

class ReadoutLine(LibraryBase):
    def __init__(self, options):
        self.name = "rdl0"
        self.type = "ReadoutLine"
        self.chip = "chip0"
        self.start_pos = (0, 0)
        self.end_pos = (0, 500)
        self.coupling_length = 300
        self.orientation = 90
        self.outline = []
        # parameter list
        self.op_name_list = list(self.__dict__.keys())
        # initialization
        self.inject_options(Dict(options))
        return
    
    def calc_general_ops(self):
        return

    def draw_gds(self):
        return