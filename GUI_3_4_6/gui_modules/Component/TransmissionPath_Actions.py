import os
from PyQt5 import QtCore  # 直接导入 QtCore 模块
from PyQt5.QtCore import pyqtSignal, QObject, Qt  

from ..Component_Actions import ComponentActions  # 导入父类
import GUI_3_4_6.gui_modules.global_parameters as gp  # Access global variables via module name


class TransmissionPathActions(ComponentActions):
    operation_completed = pyqtSignal(str)

    def __init__(self, current_design, parent=None):  
        super().__init__(parent)  
        self.current_design = current_design  

    def transmission_path(self):
        """TransmissionPath 组件参数窗口"""
        print("TransmissionPath")
        fields = [
            ("Name", "transmission1"),
            ("Pos", "[(-200, 100), (0, 0), (500, 0), (700, 100)]"),
            ("Width", "15"),
            ("Gap", "5"),
            ("Pad Width", "30"),
            ("Pad Height", "50"),
            ("Pad Gap", "5")
        ]
         # 获取当前脚本文件所在的目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 构建图片路径（相对于当前脚本文件的上上级目录）
        # 使用 os.path.dirname 两次，获取上上级目录
        project_root = os.path.dirname(os.path.dirname(current_dir))
        image_path = os.path.join(project_root, "icons", "type", "TransmissionPath.svg")
        self.show_param_window(fields, "TransmissionPath", image_path)


    def save_params_plus(self, dialog, component_type):
        print('TransmissionPathActions here')
        return super().save_params(dialog, component_type)
    
    def design_exists(self, name: str) -> bool:
        """Check if a design exists"""
        return name in gp.global_designs

