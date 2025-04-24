import os
from PyQt5 import QtCore  # Directly import QtCore module
from PyQt5.QtCore import pyqtSignal, QObject, Qt  

from ..Component_Actions import ComponentActions  # Import parent class
import GUI.gui_modules.global_parameters as gp  # Access global variables via module name


class ReadoutArrowActions(ComponentActions):
    operation_completed = pyqtSignal(str)

    def __init__(self, current_design, parent=None):  
        super().__init__(parent)  
        self.current_design = current_design  

    def readout_arrow(self):
        """ReadoutArrow Component parameter window"""
        print("ReadoutArrow")
        fields = [
            ("Name", "readout1"),
            ("Start Pos", "(0, 0)"),
            ("End Pos", "(0, 1000)"),
            ("Start Length", "300"),
            ("Start Radius", "90"),
            ("Arrow Length", "200"),
            ("CPW Height", "800"),
            ("CPW Length", "2000"),
            ("CPW Radius", "90"),
            ("Couple Length", "275"),
            ("Space", "26.5"),
            ("Gap", "6"),
            ("Width", "10"),
            ("Orientation", "0")
        ]
        # Retrieve the directory where the current script file is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Build image path（Relative to the upper directory of the current script file）
        # use os.path.dirname twice，Retrieve the superior directory
        project_root = os.path.dirname(os.path.dirname(current_dir))
        image_path = os.path.join(project_root, "icons", "type", "ReadoutArrow.svg")    
        self.show_param_window(fields, "ReadoutArrow", image_path)

    def save_params_plus(self, dialog, component_type):
        # return super().save_params(dialog, component_type)
        print('ReadoutArrowActions here')

    def design_exists(self, name: str) -> bool:
        """Check if a design exists"""
        return name in gp.global_designs