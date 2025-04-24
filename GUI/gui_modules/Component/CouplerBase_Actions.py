import os
from PyQt5 import QtCore  # Directly import QtCore module
from PyQt5.QtCore import pyqtSignal, QObject, Qt  

from ..Component_Actions import ComponentActions  # Import parent class
import GUI.gui_modules.global_parameters as gp  # Access global variables via module name


class CouplerBaseActions(ComponentActions):
    operation_completed = pyqtSignal(str)

    def __init__(self, current_design, parent=None):  
        super().__init__(parent)  
        self.current_design = current_design  

    def coupler_base (self):
        """CouplerBase Component parameter window"""
        print("CouplerBase")
        fields = [
            ("Name", "CouplerBase0"),
            ("Pos", "[0, 0]"),
            ("Width", "180"),
            ("Metal Width", "30"),
            ("Upper Height", "200"),
            ("Lower Height", "80"),
            ("Gap", "20"),
            ("Claw Height", "15"),
            ("Claw Width", "100"),
            ("Rotate", "90"),
            ("Start Pos", "[0, 0]"),
            ("End Pos", "[500, 0]")
        ]
        # Retrieve the directory where the current script file is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Build image path（Relative to the upper directory of the current script file）
        # use os.path.dirname twice，Retrieve the superior directory
        project_root = os.path.dirname(os.path.dirname(current_dir))
        image_path = os.path.join(project_root, "icons", "type", "CouplerBase.svg")  
        self.show_param_window(fields, "CouplerBase", image_path)


    def save_params_plus(self, dialog, component_type):
        print('CouplerBaseActions here')
        super().save_params(dialog, component_type)

    def design_exists(self, name: str) -> bool:
        """Check if a design exists"""
        return name in gp.global_designs
