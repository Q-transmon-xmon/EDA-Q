from base.cmpnts_base import CmpntsBase
from addict import Dict
import gdspy
import toolbox
import func_modules
import routing
import copy

class Chips(CmpntsBase):
    """
    Chips类，继承自CmpntsBase，用于管理和操作多个芯片组件的集合。
    """

    def __init__(self, **init_ops):
        """
        初始化Chips对象。

        输入：
            init_ops: dict，初始化所需的参数。

        输出：
            无
        """
        self.initialization(**init_ops)  # 调用初始化方法
        return
    
    def initialization(self, **init_ops):
        """
        初始化芯片组件集合。

        输入：
            init_ops: dict，生成芯片组件集合的初始化参数。

        输出：
            无
        """
        # 初始化组件名称列表
        self.cmpnt_name_list = []
        # 调用功能模块生成芯片选项
        options = func_modules.chips.generate_chips(**init_ops)
        self.inject_options(options)  # 注入参数
        return
    
    def draw_gds(self):
        """
        绘制多个芯片组件的GDS版图。

        输入：
            无

        输出：
            无
        """
        gdspy.library.use_current_library = False
        self.lib = gdspy.GdsLibrary()  # 创建一个新的GDS库
        self.cell_Dict = Dict()

        # 生成每个组件的lib
        for cmpnt_name in self.cmpnt_name_list:
            cmpnt = getattr(self, cmpnt_name)
            cmpnt.draw_gds()

        # 遍历组件，将每个组件添加到对应芯片的cell中
        for cmpnt_name in self.cmpnt_name_list:
            cmpnt = getattr(self, cmpnt_name)
            chip_name = cmpnt.name
            if chip_name not in self.cell_Dict.keys():
                self.cell_Dict[chip_name] = self.lib.new_cell(chip_name)
            self.cell_Dict[chip_name].add(cmpnt.cell)

        # 根据芯片名称分层（设置图层号）
        for chip_name, cell in self.cell_Dict.items():
            layer_num = toolbox.custom_hash(chip_name)
            self.cell_Dict[chip_name].flatten(single_layer=layer_num, single_datatype=0)

        # 创建总的cell，并将所有芯片cell添加到总cell中
        module_name = toolbox.convert_to_snake_case(self.__class__.__name__)
        self.cell = self.lib.new_cell(module_name)
        for chip_name, chip_cell in self.cell_Dict.items():
            self.cell.add(chip_cell)
        return
    
    def change_size_from_Flipichip_routing(self, chip_name, qubits_ops, rdls_ops):
        """
        根据Flipchip路由调整芯片尺寸。

        输入：
            chip_name: str，芯片名称。
            qubits_ops: dict，量子比特的选项参数。
            rdls_ops: dict，读出线的选项参数。

        输出：
            无

        当前逻辑：
            调用routing.Flipchip的calculate_chip_size方法调整芯片尺寸（未实现具体逻辑）。
        """
        chip_ops = copy.deepcopy(getattr(self, chip_name).options)  # 提取芯片参数
        routing.Flipchip.calculate_chip_size()  # 调用路由模块计算芯片尺寸
        return
    
    def change_size_from_pins(self, chip_name, pins_ops):
        """
        根据引脚位置调整芯片尺寸。

        输入：
            chip_name: str，芯片名称。
            pins_ops: dict，引脚的选项参数。

        输出：
            无

        当前逻辑：
            调用routing.Flipchip的calculate_chip_size方法调整芯片尺寸（未实现具体逻辑）。
        """
        chip_ops = copy.deepcopy(getattr(self, chip_name).options)  # 提取芯片参数
        routing.Flipchip.calculate_chip_size()  # 调用路由模块计算芯片尺寸
        return
    
    def generate(self, **gene_ops):
        """
        根据生成参数添加一个新芯片组件。

        输入：
            gene_ops: dict，生成芯片的参数。

        输出：
            无
        """
        chip_ops = func_modules.chips.generate_chip(**gene_ops)  # 调用功能模块生成芯片选项
        chip_name = chip_ops.name  # 获取芯片名称
        chips_ops = copy.deepcopy(self.options)  # 获取当前芯片集合的选项
        chips_ops[chip_name] = copy.deepcopy(chip_ops)  # 将新芯片加入选项字典
        self.inject_options(chips_ops)  # 注入更新后的选项
        return
    
    def copy_chip(self, old_chip_name, new_chip_name):
        """
        复制一个现有的芯片组件。

        输入：
            old_chip_name: str，要复制的原芯片名称。
            new_chip_name: str，新芯片的名称。

        输出：
            无
        """
        chips_ops = self.extract_options()  # 提取当前芯片集合的参数
        chips_ops[new_chip_name] = copy.deepcopy(chips_ops[old_chip_name])  # 复制原芯片参数
        chips_ops[new_chip_name].name = new_chip_name  # 更新新芯片的名称
        self.inject_options(chips_ops)  # 注入更新后的参数
        return
