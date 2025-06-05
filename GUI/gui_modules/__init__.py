"""
GUIModule initialization file
"""
import os
import sys

# Retrieve the directory where the current script is located
current_path = os.path.dirname(os.path.abspath(__file__))
GUI_PATH = os.path.dirname(current_path)
PROJ_PATH = os.path.dirname(GUI_PATH)

# Add path
sys.path.append(GUI_PATH)
sys.path.append(PROJ_PATH)

from GUI.gui_modules.Menu.menu_bar import MenuBarManager
from GUI.gui_modules.Tool.tool_bar import ToolBarManager
from GUI.gui_modules.Manager.design_manager import DesignManager
from GUI.gui_modules.Component.Component_Library import ComponentLibrary
from GUI.gui_modules.Display.display_area import DisplayArea

__all__ = [
    'MenuBarManager',
    'ToolBarManager',
    'DesignManager',
    'ComponentLibrary',
    'DisplayArea'
]