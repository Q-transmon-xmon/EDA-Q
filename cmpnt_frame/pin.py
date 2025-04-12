from addict import Dict
from base.library_base import LibraryBase

class Pin(LibraryBase):
    def __init__(self, options):
        self.name = "pin0"
        self.type = "Pin"
        self.chip = "chip0"
        self.pos = (0, 0)
        self.outline = []
        # 参数列表
        self.op_name_list = list(self.__dict__.keys())
        # 初始化
        self.inject_options(Dict(options))
        return
    
    def calc_general_ops(self):
        return

    def draw_gds(self):
        return