import os
from PyQt5 import QtCore  # 直接导入 QtCore 模块
from PyQt5.QtCore import pyqtSignal, QObject, Qt  

from ..Component_Actions import ComponentActions  # 导入父类
import GUI_3_4_6.gui_modules.global_parameters as gp  # Access global variables via module name


class ReadoutCavityFlipchipActions(ComponentActions):
    operation_completed = pyqtSignal(str)

    def __init__(self, current_design, parent=None):  
        super().__init__(parent)  
        self.current_design = current_design  

    def readout_cavity_flipchip(self):
        """ReadoutCavityFlipchip 组件参数窗口"""
        print("ReadoutResonatorFlipchip")
        fields = [
            ("Name", "readout1"),
            ("Start Pos", "(0, 0)"),
            ("Coupling Length", "275"),
            ("Coupling Dist", "16"),
            ("Width", "5"),
            ("Gap", "4"),
            ("Start Dir", "up"),
            ("Height", "400"),
            ("Length", "3000"),
            ("Start Length", "600"),
            ("Space Dist", "60"),
            ("Radius", "30"),
            ("Orientation", "90"),
            ("Smallpad Width", "125"),
            ("Smallpad Height", "30"),
            ("Flip Length Outer", "5"),
            ("Flip Direction", "145"),
            ("Flip Length Sideling", "93"),
            ("Flip Length Inner", "25")
        ]
         # 获取当前脚本文件所在的目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 构建图片路径（相对于当前脚本文件的上上级目录）
        # 使用 os.path.dirname 两次，获取上上级目录
        project_root = os.path.dirname(os.path.dirname(current_dir))
        image_path = os.path.join(project_root, "icons", "type", "ReadoutCavityFlipchip.svg")  
        self.show_param_window(fields, "ReadoutCavityFlipchip", image_path)

    def save_params_plus(self, dialog, component_type):
        print('ReadoutResonatorFlipchipActions here')
        return super().save_params(dialog, component_type)


    def design_exists(self, name: str) -> bool:
        """Check if a design exists"""
        return name in gp.global_designs