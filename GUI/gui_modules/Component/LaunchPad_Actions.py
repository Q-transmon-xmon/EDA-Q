import os
from PyQt5 import QtCore  # Directly import QtCore module
from PyQt5.QtCore import pyqtSignal, QObject, Qt  

from ..Component_Actions import ComponentActions  # Import parent class
import GUI.gui_modules.global_parameters as gp  # Access global variables via module name


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
        # Retrieve the directory where the current script file is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Build image path（Relative to the upper directory of the current script file）
        # use os.path.dirname twice，Retrieve the superior directory
        project_root = os.path.dirname(os.path.dirname(current_dir))
        image_path = os.path.join(project_root, "icons", "type", "LaunchPad.svg")    
        self.show_param_window(fields, "LaunchPad", image_path)

    def save_params_plus(self, dialog, component_type):
        print('LaunchPadActions here')
        return super().save_params(dialog, component_type)
    

    def design_exists(self, name: str) -> bool:
        """Check if a design exists"""
        return name in gp.global_designs
