import os
from PyQt5.QtCore import pyqtSignal

import GUI.gui_modules.Global.global_parameters as gp  # Access global variables via module name

from GUI.gui_modules.Component.Component_Actions import ComponentActions  # Import parent class
from GUI.icons.path_manager import get_icon_path


class CouplingLineStraightActions(ComponentActions):
    operation_completed = pyqtSignal(str)

    def __init__(self, current_design, parent=None):  
        super().__init__(parent)  
        self.current_design = current_design  

    def coupling_line_straight(self):
        """CouplingLineStraight Component parameter window"""
        print("CouplingLineStraight")
        fields = [
            ("Name", "q0_cp_q1"),
            ("Qubits", '["q0", "q1"]'),
            ("Width", "10"),
            ("Gap", "5"),
            ("Start Pos", "[0, 0]"),
            ("End Pos", "[500, 0]")
        ]
        image_path = get_icon_path("type", "CouplingLineStraight.svg")
        self.show_param_window(fields, "CouplingLineStraight", image_path)

    def save_params_plus(self, dialog, component_type):
        # return super().save_params(dialog, component_type)
        print('CouplingLineStraightActions here')


    def design_exists(self, name: str) -> bool:
        """Check if a design exists"""
        return name in gp.global_designs