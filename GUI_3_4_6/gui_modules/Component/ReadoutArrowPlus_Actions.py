import os
from PyQt5 import QtCore  # 直接导入 QtCore 模块
from PyQt5.QtCore import pyqtSignal, QObject, Qt  

from ..Component_Actions import ComponentActions  # 导入父类
import GUI_3_4_6.gui_modules.global_parameters as gp  # Access global variables via module name


class ReadoutArrowPlusActions(ComponentActions):
    operation_completed = pyqtSignal(str)

    def __init__(self, current_design, parent=None):  
        super().__init__(parent)  
        self.current_design = current_design  

    def readout_arrow_plus(self):
        """ReadoutArrowPlus 组件参数窗口"""
        print("ReadoutArrowPlus")
        fields = [
            ("Name", "readout1"),
            ("Start Pos", "(0, 0)"),
            ("Coupling Length", "300"),
            ("Coupling Dist", "26.5"),
            ("Width", "10"),
            ("Gap", "6"),
            ("Height", "1000"),
            ("Finger Length", "300"),
            ("Finger Orientation", "45"),
            ("Start Dir", "up"),
            ("Start Length", "300"),
            ("Length", "3000"),
            ("Space Dist", "200"),
            ("Radius", "90"),
            ("CPW Orientation", "45"),
            ("Arrow Length", "150"),
            ("Arrow Orientation", "225")
        ]
        # 获取当前脚本文件所在的目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 构建图片路径（相对于当前脚本文件的上上级目录）
        # 使用 os.path.dirname 两次，获取上上级目录
        project_root = os.path.dirname(os.path.dirname(current_dir))
        image_path = os.path.join(project_root, "icons", "type", "ReadoutArrowPlus.svg") 
        self.show_param_window(fields, "ReadoutArrowPlus", image_path)

    def save_params_plus(self, dialog, component_type):
        print('ReadoutArrowPlusActions here')
        return super().save_params(dialog, component_type)
    
    def design_exists(self, name: str) -> bool:
        """Check if a design exists"""
        return name in gp.global_designs
