# main_window.py
import sys
import os
import logging

# 获取当前脚本所在的目录
current_path = os.path.dirname(os.path.abspath(__file__))
GUI_PATH = os.path.dirname(current_path)
PROJ_PATH = os.path.dirname(GUI_PATH)

# 添加路径
sys.path.append(GUI_PATH)
sys.path.append(PROJ_PATH)

from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QSplitter
from PyQt5.QtCore import Qt
from GUI_3_4_6.gui_modules import DesignManager, ComponentLibrary, ToolBarManager, MenuBarManager
from GUI_3_4_6.gui_modules.display_area import DisplayArea
from GUI_3_4_6.gui_modules.styles import set_stylesheet
from GUI_3_4_6.gui_modules.global_state import global_state


class MainWindow(QMainWindow):
    """主窗口类，仅包含界面布局和基础交互"""

    def __init__(self):
        super().__init__()
        self._init_ui_components()
        self._setup_layout()
        self._connect_core_signals()
        set_stylesheet(self)
    def _init_ui_components(self):
        """初始化所有UI组件"""
        self.design_manager = DesignManager(parent=self)
        self.component_library = ComponentLibrary(self)
        self.display_area = DisplayArea(main_window=MainWindow,parent=self)
        self.toolbar = ToolBarManager(self)
        self.menu = MenuBarManager(self)

    def _setup_layout(self):
        """构建主布局"""
        # 窗口设置
        self.setWindowTitle("EDA-Q")
        self.setWindowIcon(self._load_icon())
        self._set_initial_geometry()

        # 主分割器布局
        main_splitter = QSplitter(Qt.Horizontal)
        left_splitter = self._create_left_panel()
        main_splitter.addWidget(left_splitter)
        main_splitter.addWidget(self.display_area)
        self.setCentralWidget(main_splitter)

        # 添加菜单栏和工具栏
        self.setMenuBar(self.menu.menu_bar)
        self.addToolBar(self.toolbar)

    def _create_left_panel(self) -> QSplitter:
        """创建左侧管理面板"""
        left_splitter = QSplitter(Qt.Vertical)
        left_splitter.addWidget(self.design_manager)
        left_splitter.addWidget(self.component_library)
        return left_splitter

    def _set_initial_geometry(self):
        """设置窗口初始位置和大小"""
        screen = QApplication.primaryScreen().availableGeometry()
        self.resize(int(screen.width() * 0.8), int(screen.height() * 0.8))
        self.move(int((screen.width() - self.width()) / 2), int((screen.height() - self.height()) / 2))

    def _load_icon(self) -> QIcon:
        """加载窗口图标"""
        icon_path = os.path.join(os.path.dirname(__file__), "../icons/logo/logo_2.png")
        return QIcon(icon_path)

    def _connect_core_signals(self):
        """连接核心信号（非业务逻辑）"""
        self.menu.toggle_design_manager.connect(self.design_manager.setVisible)
        self.menu.toggle_component_lib.connect(self.component_library.setVisible)