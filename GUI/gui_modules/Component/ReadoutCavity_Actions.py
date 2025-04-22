import os
from PyQt5 import QtCore  # 直接导入 QtCore 模块
from PyQt5.QtCore import pyqtSignal, QObject, Qt  

from ..Component_Actions import ComponentActions  # 导入父类
import GUI.gui_modules.global_parameters as gp  # Access global variables via module name


class ReadoutCavityActions(ComponentActions):
    operation_completed = pyqtSignal(str)

    def __init__(self, current_design, parent=None):  
        super().__init__(parent)  
        self.current_design = current_design  

    def readout_cavity(self):
        """ReadoutCavity 组件参数窗口"""
        print("ReadoutResonator")
        fields = [
            ("Name", "rdl0"),
            ("Start Pos", "[0, 0]"),
            ("End Pos", "[0, 600]"),
            ("Coupling Length", "300"),
            ("Orientation", "90"),
            ("Length", "4000"),
            ("CPW Width", "10"),
            ("Start Straight", "1000"),
            ("Start Radius", "60"),
            ("Radius", "60"),
            ("Couple Length", "275"),
            ("Space", "26.5"),
            ("Gap", "5")
        ]
        # 获取当前脚本文件所在的目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 构建图片路径（相对于当前脚本文件的上上级目录）
        # 使用 os.path.dirname 两次，获取上上级目录
        project_root = os.path.dirname(os.path.dirname(current_dir))
        image_path = os.path.join(project_root, "icons", "type", "ReadoutCavity.svg")
        self.show_param_window(fields, "ReadoutCavity", image_path)

    def save_params_plus(self, dialog, component_type):
        print('ReadoutResonatorActions here')
        return super().save_params(dialog, component_type)
    
    def design_exists(self, name: str) -> bool:
        """Check if a design exists"""
        return name in gp.global_designs

