import os
from PyQt5.QtCore import pyqtSignal

from GUI.gui_modules.Component.Component_Actions import ComponentActions  # Import parent class
import GUI.gui_modules.Global.global_parameters as gp  # Access global variables via module name
from GUI.icons.path_manager import get_icon_path


class LaunchPadActions(ComponentActions):
    operation_completed = pyqtSignal(str)

    def __init__(self, current_design, parent=None):  
        super().__init__(parent)  
        self.current_design = current_design  

    def launch_pad(self):
        """LaunchPad Component parameter window"""
        print("LaunchPad")
        fields = [
            ("Name", "pin0"),
            ("Pos", "(0, 0)"),
            ("Trace Width", "5"),
            ("Trace Gap", "3"),
            ("Taper Height", "100"),
            ("Pad Width", "250"),
            ("Pad Height", "250"),
            ("Pad Gap", "100"),
            ("Orientation", "0"),
            ("Start Straight", "50"),
            ("Distance to Chip", "350"),
            ("Distance to Qubits", "3650")
        ]
        image_path = get_icon_path("type", "LaunchPad.svg")
        self.show_param_window(fields, "LaunchPad", image_path)

    def save_params_plus(self, dialog, component_type):
        print('LaunchPadActions here')
        return super().save_params(dialog, component_type)
    

    def design_exists(self, name: str) -> bool:
        """Check if a design exists"""
        return name in gp.global_designs
