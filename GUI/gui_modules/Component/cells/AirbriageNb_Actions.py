import os
from PyQt5.QtCore import pyqtSignal
import GUI.gui_modules.Global.global_parameters as gp  # Access global variables via module name


from GUI.gui_modules.Component.Component_Actions import ComponentActions  # Import parent class
from GUI.icons.path_manager import get_icon_path


class AirbriageNbActions(ComponentActions):
    operation_completed = pyqtSignal(str)

    def __init__(self, current_design, parent=None):  
        super().__init__(parent)  
        self.current_design = current_design  

    def airbriage_nb(self):
        """AirbriageNb Component parameter window"""
        print("AirbriageNb")
        fields = [
            ("Name", "AirbriageNb0"),
            ("GDS Pos", "(0, 0)"),
            ("Topo Pos", "(0, 0)"),
            ("Rotation", "0")
        ]
        image_path = get_icon_path("type","AirbriageNb.svg")
        self.show_param_window(fields, "AirbriageNb", image_path)  
    
    def save_params_plus(self, dialog, component_type):
        print('AirbriageNb_Actions here')
        super().save_params(dialog, component_type)

    def design_exists(self, name: str) -> bool:
        """Check if a design exists"""
        return name in gp.global_designs