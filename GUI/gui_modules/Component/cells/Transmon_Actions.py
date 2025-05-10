import os
from PyQt5.QtCore import pyqtSignal
import GUI.gui_modules.Global.global_parameters as gp  # Access global variables via module name

from GUI.gui_modules.Component.Component_Actions import ComponentActions  # Import parent class
from GUI.icons.path_manager import get_icon_path


class TransmonActions(ComponentActions):
    operation_completed = pyqtSignal(str)  # Operation completion signal

    def __init__(self, current_design, parent=None):  
        super().__init__(parent)  
        self.current_design = current_design  # Store the current design  

    def transmon(self):
        """Transmon Component parameter window"""
        print("Transmon")
        fields = [
            ("Name", "q1"),
            ("GDS Pos", "(0, 0)"),
            ("Topo Pos", "(0, 0)"),
            ("Width", "455"),
            ("Height", "150"),
            ("Gap", "30"),
            ("Rotate", "0"),
            ("Subtract Width", "600"),
            ("Subtract Height", "500")
        ]
        image_path = get_icon_path("type", "Transmon.svg")
        self.show_param_window(fields, "Transmon", image_path)

    def save_params_plus(self, dialog, component_type):
        print('TransmonActions here')
        super().save_params(dialog, component_type)

    def design_exists(self, name: str) -> bool:
        """Check if a design exists"""
        return name in gp.global_designs
        

