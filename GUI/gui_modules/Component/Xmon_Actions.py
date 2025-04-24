# Xmon_Actions.py
import os
from PyQt5 import QtCore  # Directly import QtCore module
from PyQt5.QtCore import pyqtSignal, QObject, Qt  

from ..Component_Actions import ComponentActions  # Import parent class

import GUI.gui_modules.global_parameters as gp  # Access global variables via module name


class XmonActions(ComponentActions):
    operation_completed = pyqtSignal(str)  # Operation completion signal

    def __init__(self, current_design, parent=None):  
        super().__init__(parent)  
        self.current_design = current_design  # Store the current design  

    def xmon(self):
        """Xmon Component parameter window"""
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
         # Retrieve the directory where the current script file is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Build image path（Relative to the upper directory of the current script file）
        # use os.path.dirname twice，Retrieve the superior directory
        project_root = os.path.dirname(os.path.dirname(current_dir))
        image_path = os.path.join(project_root, "icons", "type", "Xmon.svg")
        self.show_param_window(fields, "Xmon", image_path)
        
    def save_params_plus(self, dialog, component_type):
        print('XmonActions here')
        return super().save_params(dialog, component_type)


    def design_exists(self, name: str) -> bool:
        """Check if a design exists"""
        return name in gp.global_designs

