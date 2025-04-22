import os
from PyQt5 import QtCore  # 直接导入 QtCore 模块
from PyQt5.QtCore import pyqtSignal, QObject, Qt  

from ..Component_Actions import ComponentActions  # 导入父类
import GUI.gui_modules.global_parameters as gp  # Access global variables via module name


class ReadoutArrowActions(ComponentActions):
    operation_completed = pyqtSignal(str)

    def __init__(self, current_design, parent=None):  
        super().__init__(parent)  
        self.current_design = current_design  

    def readout_arrow(self):
        """ReadoutArrow 组件参数窗口"""
        print("ReadoutArrow")
        fields = [
            ("Name", "readout1"),
            ("Start Pos", "(0, 0)"),
            ("End Pos", "(0, 1000)"),
            ("Start Length", "300"),
            ("Start Radius", "90"),
            ("Arrow Length", "200"),
            ("CPW Height", "800"),
            ("CPW Length", "2000"),
            ("CPW Radius", "90"),
            ("Couple Length", "275"),
            ("Space", "26.5"),
            ("Gap", "6"),
            ("Width", "10"),
            ("Orientation", "0")
        ]
        # 获取当前脚本文件所在的目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 构建图片路径（相对于当前脚本文件的上上级目录）
        # 使用 os.path.dirname 两次，获取上上级目录
        project_root = os.path.dirname(os.path.dirname(current_dir))
        image_path = os.path.join(project_root, "icons", "type", "ReadoutArrow.svg")    
        self.show_param_window(fields, "ReadoutArrow", image_path)

    def save_params_plus(self, dialog, component_type):
        # return super().save_params(dialog, component_type)
        print('ReadoutArrowActions here')

    def design_exists(self, name: str) -> bool:
        """Check if a design exists"""
        return name in gp.global_designs