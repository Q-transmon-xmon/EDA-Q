import os
from PyQt5.QtCore import pyqtSignal

from GUI.gui_modules.Component.Component_Actions import ComponentActions  # Import parent class
import GUI.gui_modules.Global.global_parameters as gp  # Access global variables via module name
from GUI.icons.path_manager import get_icon_path


class ReadoutArrowPlusActions(ComponentActions):
    operation_completed = pyqtSignal(str)

    def __init__(self, current_design, parent=None):  
        super().__init__(parent)  
        self.current_design = current_design  

    def readout_arrow_plus(self):
        """ReadoutArrowPlus Component parameter window"""
        print("ReadoutArrowPlus")
        fields = [
            ("Name", "readout1"),
            ("Start Pos", "(0, 0)"),
            ("Coupling Length", "300"),
            ("Coupling Dist", "26.5"),
            ("Width", "10"),
            ("Gap", "6"),
            ("Height", "1000"),
            ("Finger Length", "300"),
            ("Finger Orientation", "45"),
            ("Start Dir", "up"),
            ("Start Length", "300"),
            ("Length", "3000"),
            ("Space Dist", "200"),
            ("Radius", "90"),
            ("CPW Orientation", "45"),
            ("Arrow Length", "150"),
            ("Arrow Orientation", "225")
        ]
        image_path = get_icon_path("type", "ReadoutArrowPlus.svg")
        self.show_param_window(fields, "ReadoutArrowPlus", image_path)

    def save_params_plus(self, dialog, component_type):
        print('ReadoutArrowPlusActions here')
        return super().save_params(dialog, component_type)
    
    def design_exists(self, name: str) -> bool:
        """Check if a design exists"""
        return name in gp.global_designs
