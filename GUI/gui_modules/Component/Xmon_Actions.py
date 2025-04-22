# Xmon_Actions.py
import os
from PyQt5 import QtCore  # 直接导入 QtCore 模块
from PyQt5.QtCore import pyqtSignal, QObject, Qt  

from ..Component_Actions import ComponentActions  # 导入父类

import GUI.gui_modules.global_parameters as gp  # Access global variables via module name


class XmonActions(ComponentActions):
    operation_completed = pyqtSignal(str)  # 操作完成信号

    def __init__(self, current_design, parent=None):  
        super().__init__(parent)  
        self.current_design = current_design  # 存储当前设计  

    def xmon(self):
        """Xmon 组件参数窗口"""
        print("xmon")
        fields = [
            ("Name", "q0"),
            ("GDS Pos", "(0, 0)"),
            ("Topo Pos", "(0, 0)"),
            ("Cross Width", "10"),
            ("Cross Height", "300"),
            ("Cross Gap", "20"),
            ("Claw Length", "30"),
            ("Ground Spacing", "5"),
            ("Claw Width", "10"),
            ("Claw Gap", "6"),
            ("Rotate", "0")
        ]
         # 获取当前脚本文件所在的目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 构建图片路径（相对于当前脚本文件的上上级目录）
        # 使用 os.path.dirname 两次，获取上上级目录
        project_root = os.path.dirname(os.path.dirname(current_dir))
        image_path = os.path.join(project_root, "icons", "type", "Xmon.svg")
        self.show_param_window(fields, "Xmon", image_path)
        
    def save_params_plus(self, dialog, component_type):
        print('XmonActions here')
        return super().save_params(dialog, component_type)


    def design_exists(self, name: str) -> bool:
        """Check if a design exists"""
        return name in gp.global_designs

