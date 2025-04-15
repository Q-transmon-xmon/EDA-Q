import os
from PyQt5 import QtCore  # 直接导入 QtCore 模块
from PyQt5.QtCore import pyqtSignal, QObject, Qt  

from ..Component_Actions import ComponentActions  # 导入父类
import GUI_3_4_6.gui_modules.global_parameters as gp  # Access global variables via module name


class ControlLineWidthDiffActions(ComponentActions):
    operation_completed = pyqtSignal(str)

    def __init__(self, current_design, parent=None):  
        super().__init__(parent)  
        self.current_design = current_design  

    def control_line_width_diff(self):
        """ControlLineWidthDiff 组件参数窗口"""
        print("ControlLineWidthDiff")
        fields = [
            ("Name", "ControlLineWidthDiff0"),
            ("Pos", "[(0, 0), (0, 500), (500, 500), (500, 0), (1000, 0), (1500, 0)]"),
            ("Width", "[15, 10]"),
            ("Gap", "[5, 4]"),
            ("Buffer Length", "100"),
            ("Corner Radius", "20")
        ]
        # 获取当前脚本文件所在的目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 构建图片路径（相对于当前脚本文件的上上级目录）
        # 使用 os.path.dirname 两次，获取上上级目录
        project_root = os.path.dirname(os.path.dirname(current_dir))
        image_path = os.path.join(project_root, "icons", "type", "ControlLineWidthDiff.svg")
        self.show_param_window(fields, "ControlLineWidthDiff", image_path)

    def save_params_plus(self, dialog, component_type):
        print('ControlLineWidthDiffActions here')
        super().save_params(dialog, component_type)

    def design_exists(self, name: str) -> bool:
        """Check if a design exists"""
        return name in gp.global_designs
