import os
from PyQt5.QtCore import pyqtSignal

from GUI.gui_modules.Component.Component_Actions import ComponentActions  # Import parent class
import GUI.gui_modules.Global.global_parameters as gp  # Access global variables via module name
from GUI.icons.path_manager import get_icon_path


class TransmissionPathActions(ComponentActions):
    operation_completed = pyqtSignal(str)

    def __init__(self, current_design, parent=None):  
        super().__init__(parent)  
        self.current_design = current_design  

    def transmission_path(self):
        """TransmissionPath Component parameter window"""
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
        image_path = get_icon_path("type", "TransmissionPath.svg")
        self.show_param_window(fields, "TransmissionPath", image_path)


    def save_params_plus(self, dialog, component_type):
        print('TransmissionPathActions here')
        return super().save_params(dialog, component_type)
    
    def design_exists(self, name: str) -> bool:
        """Check if a design exists"""
        return name in gp.global_designs

