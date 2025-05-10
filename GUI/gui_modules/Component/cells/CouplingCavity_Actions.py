import os
from PyQt5.QtCore import pyqtSignal

from GUI.gui_modules.Component.Component_Actions import ComponentActions  # Import parent class
import GUI.gui_modules.Global.global_parameters as gp  # Access global variables via module name
from GUI.icons.path_manager import get_icon_path


class CouplingCavityActions(ComponentActions):
    operation_completed = pyqtSignal(str)

    def __init__(self, current_design, parent=None):  
        super().__init__(parent)  
        self.current_design = current_design  

    def coupling_cavity(self):
        """CouplingCavity Component parameter window"""
        print("CouplingCavity")
        fields = [
            ("Name", "q0_cp_q1"),
            ("Qubits", '["q0", "q1"]'),
            ("Width", "10"),
            ("Gap", "5"),
            ("Start Pos", "(0, 0)"),
            ("End Pos", "(1000, 0)"),
            ("Length", "3000"),
            ("Start Straight", "200"),
            ("End Straight", "200"),
            ("Radius", "60")
        ]
        image_path = get_icon_path("type", "CouplingCavity.svg")
        self.show_param_window(fields, "CouplingCavity", image_path)

    def save_params_plus(self, dialog, component_type):
        print('CouplingCavityActions here')
        super().save_params(dialog, component_type)


    def design_exists(self, name: str) -> bool:
        """Check if a design exists"""
        return name in gp.global_designs
