import os
from PyQt5 import QtCore  # Directly import QtCore module
from PyQt5.QtCore import pyqtSignal, QObject, Qt  

from ..Component_Actions import ComponentActions  # Import parent class
import GUI.gui_modules.global_parameters as gp  # Access global variables via module name


class ReadoutCavityPlusActions(ComponentActions):
    operation_completed = pyqtSignal(str)

    def __init__(self, current_design, parent=None):  
        super().__init__(parent)  
        self.current_design = current_design  

    def readout_cavity_plus(self):
        """ReadoutCavityPlus Component parameter window"""
        print("ReadoutResonatorPlus")
        fields = [
            ("Name", "readout1"),
            ("Start Pos", "(0, 0)"),
            ("Coupling Length", "100"),
            ("Coupling Dist", "26.5"),
            ("Width", "4"),
            ("Gap", "2"),
            ("Start Dir", "up"),
            ("Height", "200"),
            ("Length", "2000"),
            ("Start Length", "500"),
            ("Space Dist", "30"),
            ("Radius", "10"),
            ("Orientation", "90")
        ]
         # Retrieve the directory where the current script file is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Build image path（Relative to the upper directory of the current script file）
        # use os.path.dirname twice，Retrieve the superior directory
        project_root = os.path.dirname(os.path.dirname(current_dir))
        image_path = os.path.join(project_root, "icons", "type", "ReadoutCavityPlus.svg")
        self.show_param_window(fields, "ReadoutCavityPlus", image_path)

    def save_params_plus(self, dialog, component_type):
        print('ReadoutResonatorPlusActions here')
        return super().save_params(dialog, component_type)
    
    def design_exists(self, name: str) -> bool:
        """Check if a design exists"""
        return name in gp.global_designs
