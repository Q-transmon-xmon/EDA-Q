"""
GUI模块初始化文件
"""
import os
import sys

# 获取当前脚本所在的目录
current_path = os.path.dirname(os.path.abspath(__file__))
GUI_PATH = os.path.dirname(current_path)
PROJ_PATH = os.path.dirname(GUI_PATH)

# 添加路径
sys.path.append(GUI_PATH)
sys.path.append(PROJ_PATH)

from GUI.gui_modules.menu_bar import MenuBarManager
from GUI.gui_modules.tool_bar import ToolBarManager
from GUI.gui_modules.design_manager import DesignManager
from GUI.gui_modules.Component_Library import ComponentLibrary
from GUI.gui_modules.display_area import DisplayArea

__all__ = [
    'MenuBarManager',
    'ToolBarManager',
    'DesignManager',
    'ComponentLibrary',
    'DisplayArea'
]