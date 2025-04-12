from addict import Dict
from base.library_base import LibraryBase

class CrossOver(LibraryBase):
    def __init__(self, options):
        # 框架
        self.name = "crosvs0"
        self.type = "CrossOver"
        self.chip = "chip0"
        self.pos = (0, 0)
        self.outline = []
        # 参数列表
        self.op_name_list = list(self.__dict__.keys())
        # 初始化
        self.inject_options(Dict(options))
        self.calc_general_ops()
        return
    
    def calc_general_ops(self):
        return

    def draw_gds(self):
        return