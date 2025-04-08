from addict import Dict
import gdspy, copy
from base.library_base import LibraryBase

class Chip(LibraryBase):
    """
    Chip类,继承自LibraryBase,用于定义芯片的基本属性和功能。
    """

    def __init__(self, options: Dict = None):
        """
        初始化Chip对象。

        输入：
            options: Dict,包含芯片初始化参数的字典,默认为None。

        输出：
            无
        """
        self.name = "chip0"  # 芯片的默认名称
        self.type = "RecChip"  # 芯片的默认类型（矩形芯片）
        self.op_name_list = copy.deepcopy(list(self.__dict__.keys()))  # 保存初始化时的参数名称列表
        self.inject_options(options)  # 将传入的参数注入到对象中
        return

    def calc_general_ops(self):
        return

    def draw_gds(self):
        return
