from addict import Dict
from base.library_base import LibraryBase

class ControlLine(LibraryBase):
    def __init__(self, options):
        self.name = "ctl0"
        self.type = "ControlLine"
        self.chip = "chip0"
        qubits = ["q0", "q1"],
        outline = [],
        width = 10,
        gap = 5,
        start_pos = [0, 0],
        end_pos = [500, 0],
        # 参数列表
        self.op_name_list = list(self.__dict__.keys())
        # 初始化
        self.inject_options(Dict(options))
        return
    
    def calc_general_ops(self):
        return

    def draw_gds(self):
        return