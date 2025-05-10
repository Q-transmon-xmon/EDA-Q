import os
from PyQt5.QtCore import pyqtSignal

from GUI.gui_modules.Component.Component_Actions import ComponentActions  # Import parent class
import GUI.gui_modules.Global.global_parameters as gp  # Access global variables via module name
from GUI.icons.path_manager import get_icon_path


class ReadoutCavityFlipchipActions(ComponentActions):
    operation_completed = pyqtSignal(str)

    def __init__(self, current_design, parent=None):  
        super().__init__(parent)  
        self.current_design = current_design  

    def readout_cavity_flipchip(self):
        """ReadoutCavityFlipchip Component parameter window"""
        print("ReadoutResonatorFlipchip")
        fields = [
            ("Name", "readout1"),
            ("Start Pos", "(0, 0)"),
            ("Coupling Length", "275"),
            ("Coupling Dist", "16"),
            ("Width", "5"),
            ("Gap", "4"),
            ("Start Dir", "up"),
            ("Height", "400"),
            ("Length", "3000"),
            ("Start Length", "600"),
            ("Space Dist", "60"),
            ("Radius", "30"),
            ("Orientation", "90"),
            ("Smallpad Width", "125"),
            ("Smallpad Height", "30"),
            ("Flip Length Outer", "5"),
            ("Flip Direction", "145"),
            ("Flip Length Sideling", "93"),
            ("Flip Length Inner", "25")
        ]
        image_path =get_icon_path("type", "ReadoutCavityFlipchip.svg")
        self.show_param_window(fields, "ReadoutCavityFlipchip", image_path)

    def save_params_plus(self, dialog, component_type):
        print('ReadoutResonatorFlipchipActions here')
        return super().save_params(dialog, component_type)


    def design_exists(self, name: str) -> bool:
        """Check if a design exists"""
        return name in gp.global_designs