# Xmon_Actions.py
import os
from PyQt5.QtCore import pyqtSignal

from GUI.gui_modules.Component.Component_Actions import ComponentActions  # Import parent class

import GUI.gui_modules.Global.global_parameters as gp  # Access global variables via module name
from GUI.icons.path_manager import get_icon_path


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
        image_path = get_icon_path("type", "Xmon.svg")
        self.show_param_window(fields, "Xmon", image_path)
        
    def save_params_plus(self, dialog, component_type):
        print('XmonActions here')
        return super().save_params(dialog, component_type)


    def design_exists(self, name: str) -> bool:
        """Check if a design exists"""
        return name in gp.global_designs

