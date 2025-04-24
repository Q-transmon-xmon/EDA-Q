from addict import Dict
from base.library_base import LibraryBase

class TransmissionLine(LibraryBase):
    def __init__(self, options):
        self.name = "tml0"
        self.type = "TransmissionLine"
        self.chip = "chip0"
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