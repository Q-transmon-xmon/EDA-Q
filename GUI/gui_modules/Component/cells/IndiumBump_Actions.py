import os
from PyQt5.QtCore import pyqtSignal

from GUI.gui_modules.Component.Component_Actions import ComponentActions  # Import parent class
import GUI.gui_modules.Global.global_parameters as gp  # Access global variables via module name
from GUI.icons.path_manager import get_icon_path


class IndiumBumpActions(ComponentActions):
    operation_completed = pyqtSignal(str)

    def __init__(self, current_design, parent=None):  
        super().__init__(parent)  
        self.current_design = current_design  

    def indium_bump(self):
        """IndiumBump Component parameter window"""
        print("IndiumBump")
        fields = [
            ("Name", "In0"),
            ("Center Pos", "(0, 0)"),
            ("Radius", "10")
        ]
        image_path =get_icon_path("type", "IndiumBump.svg")
        self.show_param_window(fields, "IndiumBump", image_path)

    def save_params_plus(self, dialog, component_type):
        
        print('IndiumBumpActions here')
        return super().save_params(dialog, component_type)
    

    def design_exists(self, name: str) -> bool:
        """Check if a design exists"""
        return name in gp.global_designs