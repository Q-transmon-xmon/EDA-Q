import os
from PyQt5.QtCore import pyqtSignal

from GUI.gui_modules.Component.Component_Actions import ComponentActions  # Import parent class
import GUI.gui_modules.Global.global_parameters as gp  # Access global variables via module name
from GUI.icons.path_manager import get_icon_path


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
        image_path = get_icon_path("type", "ReadoutCavityPlus.svg")
        self.show_param_window(fields, "ReadoutCavityPlus", image_path)

    def save_params_plus(self, dialog, component_type):
        print('ReadoutResonatorPlusActions here')
        return super().save_params(dialog, component_type)
    
    def design_exists(self, name: str) -> bool:
        """Check if a design exists"""
        return name in gp.global_designs
