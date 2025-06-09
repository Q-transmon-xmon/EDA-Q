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

from GUI.icons.path_manager import get_icon_path
# Import module
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout,
    QWidget, QSplitter, QMessageBox
)
from PyQt5.QtCore import Qt
from api.design import Design
from GUI.gui_modules import DesignManager, MenuBarManager, ComponentLibrary, ToolBarManager
from GUI.gui_modules.Display.display_area import DisplayArea
from GUI.gui_modules.Global.styles import set_stylesheet
from GUI.gui_modules.Global.global_state import global_state

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class MyMainWindow(QMainWindow):
    """Main window class, responsible for the application's main interface and logic."""

    def __init__(self):
        super(MyMainWindow, self).__init__()
        self.node_dialog = None
        self.design_manager_visible = True  # Design manager is visible by default
        self.component_lib_visible = True  # Component library is visible by default

        # Initialize global design
        initial_design = Design()
        global_state.create_design("Initial Design", path=None)
        global_state.update_design("Initial Design", initial_design)
        self.current_name = global_state.get_current_design_name()
        self.design_instance = global_state.get_design(self.current_name)
        # Initialize UI components
        self._init_components()
        self._setup_ui()
        self._connect_signals()

    def _init_components(self):
        """Initialize all UI components"""
        # Core components
        self.design_manager = DesignManager(parent=self)
        self.component_library = ComponentLibrary(self)
        self.display_area = DisplayArea(parent=self)

        # Manager class components
        self.toolbar_manager = ToolBarManager(self)
        self.menu_manager = MenuBarManager(parent=self)
        # Set window icon
        icon_path = get_icon_path("logo", "logo.png")
        self.setWindowIcon(QIcon(str(icon_path)))

    def _setup_ui(self):
        """Construct the user interface"""
        self.setWindowTitle("EDA-Q")
        self._setup_window_geometry()
        self._setup_main_layout()
        self._setup_splitter()
        self.setMenuBar(self.menu_manager.menu_bar)
        self.addToolBar(self.toolbar_manager)
        set_stylesheet(self)

    def _setup_window_geometry(self):
        """Set the initial size and position of the window"""
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        self.resize(int(screen_geometry.width() * 0.8), int(screen_geometry.height() * 0.8))
        self.move(
            int((screen_geometry.width() - self.width()) / 2),
            int((screen_geometry.height() - self.height()) / 2)
        )

    def _setup_main_layout(self):
        """Construct the main layout container"""
        central_widget = QWidget()
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(2, 2, 2, 2)  # Reduce margin space
        self.setCentralWidget(central_widget)

    def _setup_splitter(self):
        """Construct the dynamic splitter layout"""
        # Main horizontal splitter (left: management panel, right: display area)
        main_splitter = QSplitter(Qt.Horizontal)

        # Left vertical splitter
        left_splitter = QSplitter(Qt.Vertical)
        left_splitter.addWidget(self.design_manager)
        left_splitter.addWidget(self.component_library)
        left_splitter.setChildrenCollapsible(False)  # Prevent complete collapse

        # Set minimum and maximum width for the left splitter
        left_splitter.setMinimumWidth(330)  # Minimum width 300px
        left_splitter.setMaximumWidth(530)  # Maximum width 500px
        left_splitter.setSizes([200, 400])  # Initial height allocation: Design Manager 200px, Component Library 400px

        # Right display area
        main_splitter.addWidget(left_splitter)
        main_splitter.addWidget(self.display_area)

        # Set main splitter parameters
        main_splitter.setSizes([300, 700])  # Initial width allocation: left 300px, right 700px
        main_splitter.setHandleWidth(4)

        # Set minimum size for child components
        self.design_manager.setMinimumSize(300, 150)  # Width 300px, height 150px
        self.component_library.setMinimumSize(300, 200)  # Width 300px, height 200px

        self.main_layout.addWidget(main_splitter)

    def _connect_signals(self):
        """Connect all signals and slots"""
        # Global state signals
        global_state.current_design_changed.connect(self._handle_design_change)
        global_state.design_updated.connect(self._update_main_design)

        # Menu bar view toggle signals
        self.menu_manager.toggle_design_manager.connect(self.toggle_design_manager)
        self.menu_manager.toggle_component_lib.connect(self.toggle_component_library)

    # region View Control Functions
    def toggle_design_manager(self, visible: bool):
        """Toggle the visibility of the design manager"""
        self.design_manager_visible = visible
        self.design_manager.setVisible(visible)
        self._adjust_layout()

    def toggle_component_library(self, visible: bool):
        """Toggle the visibility of the component library"""
        self.component_lib_visible = visible
        self.component_library.setVisible(visible)
        self._adjust_layout()

    def _adjust_layout(self):
        """Force refresh the layout"""
        # Update splitter states
        for splitter in self.findChildren(QSplitter):
            splitter.refresh()

        # Trigger layout recalculation
        self.main_layout.update()
        self.updateGeometry()

    # endregion

    # region Design Management Functions
    def _handle_design_change(self, design_name: str):
        """Handle design change event"""
        if design_name:
            self._update_main_design()

    def _update_main_design(self):
        """Update the main design view"""
        self.current_name = global_state.get_current_design_name()
        self.design_instance = global_state.get_design(self.current_name)

        if self.design_instance:
            try:
                self._update_component_library(self.design_instance)
                self._update_display_area(self.design_instance)
            except Exception as e:
                logging.error(f"Design update failed: {str(e)}")
        else:
            logging.warning(f"Current design '{self.current_name}' does not exist")

    def _update_component_library(self, design: Design):
        """Update the component library (example method)"""
        # Actual implementation should call the component library's update method
        # self.component_library.load_components(design)
        pass

    def _update_display_area(self, design: Design):
        """Update the content of the display area"""
        try:
            # Ensure the picture directory exists
            os.makedirs('./picture', exist_ok=True)

            # Update status flags
            topo_updated = False
            gds_updated = False

            # Generate and display the topology image
            topology_path = './picture/topology.png'
            try:
                design.topology.save_image(path=topology_path)
                self.display_area.show_topo_image(topology_path)  # Update the display area to show the topology image
                topo_updated = True  # Mark topology image update as successful
            except Exception as topo_error:
                logging.error(f"Failed to update topology image: {str(topo_error)}")

            # Generate and display the GDS image
            gds_path = './picture/gds.svg'
            try:
                design.gds.save_svg(path=gds_path)  # Attempt to save the GDS file as an SVG
                self.display_area.show_gds_image(gds_path)  # Attempt to update the GDS tab to display the image
                gds_updated = True  # Mark GDS update as successful
            except Exception as gds_error:
                logging.error(f"Failed to update GDS image: {str(gds_error)}")
                print(f"Error occurred, error message has been logged: {str(gds_error)}")

            # Display messages based on update status
            if topo_updated and gds_updated:
                self.statusBar().showMessage("Topology Updated! GDS Updated!", 5000)
            elif topo_updated:
                self.statusBar().showMessage("Topology Updated, GDS Not Updated", 5000)
            elif gds_updated:
                self.statusBar().showMessage("Topology Not Updated, GDS Updated", 5000)
            else:
                self.statusBar().showMessage("Error: Failed to update all", 5000)

        except Exception as e:
            logging.error(f"Image display failed: {str(e)}")
            self.statusBar().showMessage(f"Error: {str(e)}", 5000)


# Add a global exception handling function
def handle_exception(exc_type, exc_value, exc_traceback):
    """
    Global exception handling function to capture all unhandled exceptions.
    """
    # Log the exception information
    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

    # Check if the QApplication instance exists
    app = QApplication.instance()
    if app is not None:
        # Show an error dialog
        error_box = QMessageBox()
        error_box.setIcon(QMessageBox.Critical)
        error_box.setText("An unexpected error has occurred")
        error_box.setInformativeText(f"{exc_type.__name__}: {exc_value}")
        error_box.setWindowTitle("Error")
        error_box.exec_()
    else:
        # If QApplication is not initialized, output to standard error
        sys.stderr.write(f"Critical error: {exc_type.__name__}: {exc_value}\n")

    # Exit the program
    sys.exit(1)


# Set the global exception hook
sys.excepthook = handle_exception
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))

    window = MyMainWindow()
    window.show()

    sys.exit(app.exec_())