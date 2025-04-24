from addict import Dict
import gdspy, copy
from base.library_base import LibraryBase

class Chip(LibraryBase):
    """
    Chipclass,Inherited fromLibraryBase,Used to define the basic properties and functions of chips。
    """

    def __init__(self, options: Dict = None):
        """
        initializationChipobject。

        input：
            options: Dict,包含芯片initialization参数的字典,Default isNone。

        output：
            not have
        """
        self.name = "chip0"  # The default name of the chip
        self.type = "RecChip"  # Default type of chip（Rectangular chip）
        self.op_name_list = copy.deepcopy(list(self.__dict__.keys()))  # Save the list of parameter names during initialization
        self.inject_options(options)  # Inject the incoming parameters into the object
        return

    def calc_general_ops(self):
        return

    def draw_gds(self):
        return
