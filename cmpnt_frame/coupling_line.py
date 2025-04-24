from addict import Dict
from base.library_base import LibraryBase

class CouplingLine(LibraryBase):
    def __init__(self, options):
        # framework
        self.name = "cpl0"
        self.type = "CouplingLine"
        self.chip = "chip0"
        self.qubits = ["q0", "q1"]
        self.outline = []
        # parameter list
        self.op_name_list = list(self.__dict__.keys())
        # initialization
        self.inject_options(Dict(options))
        self.calc_general_ops()
        return
    
    def calc_general_ops(self):
        return

    def draw_gds(self):
        return