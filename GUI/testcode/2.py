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


from GUI.gui_modules.signal_handler import signal_handler
from GUI.gui_modules.state_manager import state_manager

from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout,
    QWidget, QSplitter
)
from PyQt5.QtCore import Qt
from api.design import Design
from GUI.gui_modules import DesignManager, MenuBarManager, ComponentLibrary, ToolBarManager
from GUI.gui_modules.display_area import DisplayArea
from GUI.gui_modules.styles import set_stylesheet
from GUI.gui_modules.Design_options import DesignOptions

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class MyMainWindow(QMainWindow):
    """Main Window Class，Responsible for the main interface and logic of the application。"""

    def __init__(self):
        super(MyMainWindow, self).__init__()
        self.node_dialog = None
        self.designs = {}
        # Create initialDesignexample，And add it to the dictionary
        initial_design = Design()
        self.designs["Initial Design"] = (initial_design, None)
        self.current_design = initial_design

        # Initialize design operation object
        self.design_options = DesignOptions(self)

        # Set window icon
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../icons/logo/logo_2.png")
        self.setWindowIcon(QIcon(icon_path))
        # initializationDesignManagerAnd component library
        self.design_manager = DesignManager(parent=self)
        self.component_library = ComponentLibrary(self, current_design=self.current_design)  # transfer current_design

        # Initialize user interface
        self.init_ui()

        # Initialize menu bar manager
        self.menu_manager = MenuBarManager(parent=self)
        self.setMenuBar(self.menu_manager.menu_bar)

    def init_ui(self):
        """Initialize user interface，Including window title、layout、Toolbars and Style Settings。"""
        self.setWindowTitle("EDA-Q")
        self.setup_window_geometry()
        self.setup_main_layout()
        self.setup_toolbar()
        self.setup_splitter()
        set_stylesheet(self)

    def setup_window_geometry(self):
        """Set window size and position。"""
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        window_width = int(screen_geometry.width() * 0.8)
        window_height = int(screen_geometry.height() * 0.8)
        self.resize(window_width, window_height)
        self.move(
            int((screen_geometry.width() - window_width) / 2),
            int((screen_geometry.height() - window_height) / 2)
        )

    def setup_main_layout(self):
        """Set the main layout。"""
        self.main_layout = QVBoxLayout()
        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)

    def setup_toolbar(self):
        """Set toolbar。"""
        self.toolbar_manager = ToolBarManager(self)
        self.addToolBar(self.toolbar_manager)

    def setup_splitter(self):
        """Set up a splitter，Includes Design Manager and Display Area。"""
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

        left_splitter = QSplitter(Qt.Vertical)
        left_splitter.addWidget(self.design_manager)
        left_splitter.addWidget(self.component_library)

        self.display_area = DisplayArea(main_window=self)
        splitter.addWidget(left_splitter)
        splitter.addWidget(self.display_area)

        self.main_layout.addWidget(splitter)
        splitter.setSizes([250, 800])

    def updateMainDesign(self, updated_design):
        """Update the main window design，And update the relevant display content。"""
        state_manager.set_current_design(updated_design)  # Design in Update Status Manager
        self.current_design = updated_design
        signal_handler.current_design_changed.emit(self.current_design)
        logging.info("Main window design has been updated")
        self.design_manager.update_display()

        try:
            self.current_design.topology.save_image(path='./picture/topology.png')
            self.display_area.topo_tab.show_image('./picture/topology.png', show=True)

            self.current_design.gds.save_svg(path='./picture/gds.svg')
            self.display_area.gds_tab.show_image('./picture/gds.svg', show=True)
        except Exception as e:
            logging.error(f"Failed to display image: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))

    window = MyMainWindow()
    window.show()

    sys.exit(app.exec_())