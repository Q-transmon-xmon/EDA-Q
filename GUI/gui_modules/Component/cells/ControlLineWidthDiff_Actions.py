import os
from PyQt5.QtCore import pyqtSignal

from GUI.gui_modules.Component.Component_Actions import ComponentActions  # Import parent class
import GUI.gui_modules.Global.global_parameters as gp  # Access global variables via module name
from GUI.icons.path_manager import get_icon_path


class ControlLineWidthDiffActions(ComponentActions):
    operation_completed = pyqtSignal(str)

    def __init__(self, current_design, parent=None):  
        super().__init__(parent)  
        self.current_design = current_design  

    def control_line_width_diff(self):
        """ControlLineWidthDiff Component parameter window"""
        print("ControlLineWidthDiff")
        fields = [
            ("Name", "ControlLineWidthDiff0"),
            ("Pos", "[(0, 0), (0, 500), (500, 500), (500, 0), (1000, 0), (1500, 0)]"),
            ("Width", "[15, 10]"),
            ("Gap", "[5, 4]"),
            ("Buffer Length", "100"),
            ("Corner Radius", "20")
        ]
        image_path = get_icon_path("type", "ControlLineWidthDiff.svg")
        self.show_param_window(fields, "ControlLineWidthDiff", image_path)

    def save_params_plus(self, dialog, component_type):
        print('ControlLineWidthDiffActions here')
        super().save_params(dialog, component_type)

    def design_exists(self, name: str) -> bool:
        """Check if a design exists"""
        return name in gp.global_designs
