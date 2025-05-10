import os
from PyQt5.QtCore import pyqtSignal

from GUI.gui_modules.Component.Component_Actions import ComponentActions  # Import parent class
import GUI.gui_modules.Global.global_parameters as gp  # Access global variables via module name
from GUI.icons.path_manager import get_icon_path


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
        image_path = get_icon_path("type", "ReadoutArrow.svg")
        self.show_param_window(fields, "ReadoutArrow", image_path)

    def save_params_plus(self, dialog, component_type):
        # return super().save_params(dialog, component_type)
        print('ReadoutArrowActions here')

    def design_exists(self, name: str) -> bool:
        """Check if a design exists"""
        return name in gp.global_designs