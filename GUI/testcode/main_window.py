# main_window.py
import sys
import os
import logging

# Retrieve the directory where the current script is located
current_path = os.path.dirname(os.path.abspath(__file__))
GUI_PATH = os.path.dirname(current_path)
PROJ_PATH = os.path.dirname(GUI_PATH)

# Add path
sys.path.append(GUI_PATH)
sys.path.append(PROJ_PATH)

from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QSplitter
from PyQt5.QtCore import Qt
from GUI.gui_modules import DesignManager, ComponentLibrary, ToolBarManager, MenuBarManager
from GUI.gui_modules.display_area import DisplayArea
from GUI.gui_modules.styles import set_stylesheet
from GUI.gui_modules.global_state import global_state


class MainWindow(QMainWindow):
    """Main Window Class，Only includes interface layout and basic interaction"""

    def __init__(self):
        super().__init__()
        self._init_ui_components()
        self._setup_layout()
        self._connect_core_signals()
        set_stylesheet(self)
    def _init_ui_components(self):
        """Initialize allUIcomponent"""
        self.design_manager = DesignManager(parent=self)
        self.component_library = ComponentLibrary(self)
        self.display_area = DisplayArea(main_window=MainWindow,parent=self)
        self.toolbar = ToolBarManager(self)
        self.menu = MenuBarManager(self)

    def _setup_layout(self):
        """Build the main layout"""
        # Window settings
        self.setWindowTitle("EDA-Q")
        self.setWindowIcon(self._load_icon())
        self._set_initial_geometry()

        # Main splitter layout
        main_splitter = QSplitter(Qt.Horizontal)
        left_splitter = self._create_left_panel()
        main_splitter.addWidget(left_splitter)
        main_splitter.addWidget(self.display_area)
        self.setCentralWidget(main_splitter)

        # Add menu bar and toolbar
        self.setMenuBar(self.menu.menu_bar)
        self.addToolBar(self.toolbar)

    def _create_left_panel(self) -> QSplitter:
        """Create the left management panel"""
        left_splitter = QSplitter(Qt.Vertical)
        left_splitter.addWidget(self.design_manager)
        left_splitter.addWidget(self.component_library)
        return left_splitter

    def _set_initial_geometry(self):
        """Set the initial position and size of the window"""
        screen = QApplication.primaryScreen().availableGeometry()
        self.resize(int(screen.width() * 0.8), int(screen.height() * 0.8))
        self.move(int((screen.width() - self.width()) / 2), int((screen.height() - self.height()) / 2))

    def _load_icon(self) -> QIcon:
        """Load window icon"""
        icon_path = os.path.join(os.path.dirname(__file__), "../icons/logo/logo_2.png")
        return QIcon(icon_path)

    def _connect_core_signals(self):
        """Connect the core signal（Non business logic）"""
        self.menu.toggle_design_manager.connect(self.design_manager.setVisible)
        self.menu.toggle_component_lib.connect(self.component_library.setVisible)