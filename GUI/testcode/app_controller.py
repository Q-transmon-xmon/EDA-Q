# app_controller.py
import sys
import os

# 获取当前脚本所在的目录
current_path = os.path.dirname(os.path.abspath(__file__))
GUI_PATH = os.path.dirname(current_path)
PROJ_PATH = os.path.dirname(GUI_PATH)

# 添加路径
sys.path.append(GUI_PATH)
sys.path.append(PROJ_PATH)

import logging
from api.design import Design
from GUI.gui_modules.global_state import global_state
from GUI.gui_modules.Design_options import DesignOptions
from GUI.gui_modules.global_state import global_state
from GUI.gui_modules.styles import set_stylesheet
class AppController:
    """业务逻辑控制器，处理数据操作和复杂交互"""

    def __init__(self, window):
        self.window = window
        self.design_options = DesignOptions(window)
        self._init_global_design()
        self._connect_business_signals()
    def _init_global_design(self):
        """初始化全局设计实例"""
        if not global_state.design_exists("Initial Design"):
            initial_design = Design()
            global_state.create_design("Initial Design", path=None)
            global_state.update_design("Initial Design", initial_design)

    def _connect_business_signals(self):
        """连接业务相关信号"""
        global_state.current_design_changed.connect(self._on_design_changed)
        global_state.design_updated.connect(self._update_interface)

    def _on_design_changed(self, design_name: str):
        """处理设计切换事件"""
        if design_name:
            self._update_interface()

    def _update_interface(self):
        """更新所有界面元素"""
        current_name = global_state.get_current_design_name()
        design = global_state.get_design(current_name)

        if design:
            try:
                self._update_component_library(design)
                self._update_display(design)
            except Exception as e:
                logging.error(f"界面更新失败: {str(e)}")
                self.window.statusBar().showMessage(f"错误: {str(e)}", 5000)

    def _update_component_library(self, design: Design):
        """更新组件库内容"""
        # 调用组件库的更新方法
        pass

    def _update_display(self, design: Design):
        """更新显示区域"""
        try:
            design.topology.save_image('./picture/topology.png')
            design.gds.save_svg('./picture/gds.svg')
            self.window.display_area.topo_tab.show_image('./picture/topology.png')
            self.window.display_area.gds_tab.show_image('./picture/gds.svg')
        except Exception as e:
            logging.error(f"图像显示失败: {str(e)}")