# main_window.py
import os
from PyQt5.QtWidgets import QMainWindow, QSplitter, QWidget, QVBoxLayout, QApplication
from PyQt5.QtCore import Qt, pyqtSlot
from api.design import Design
from .design_manager import DesignManager
from .menu_bar import MenuBarManager
from .Component_Library import ComponentLibrary
from . import ToolBarManager
from .display_area import DisplayArea  # Import DisplayArea


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Initialize core data
        self.design = Design()
        self.design_updated_flag = False

        # Initialize UI components
        self._init_components()

        # Build the interface
        self._setup_ui()

    def _init_components(self):
        """Initialize all components"""
        # Manager class components
        self.menu_manager = MenuBarManager(parent=self)
        self.toolbar_manager = ToolBarManager(self)
        self.design_manager = DesignManager(parent=self)
        self.component_lib = ComponentLibrary(self)

        # Display area components
        self.display_area = DisplayArea()
        self.topo_display = self.display_area.topo_display
        self.gds_display = self.display_area.gds_display

    def _setup_ui(self):
        """Build the main interface layout"""
        self.setWindowTitle("QEDA v3.0")
        self._setup_window_geometry()
        self._setup_main_layout()
        self._setup_menu()

    def _setup_window_geometry(self):
        """Set the initial position and size of the window"""
        screen = QApplication.primaryScreen().availableGeometry()
        self.resize(int(screen.width() * 0.8), int(screen.height() * 0.8))
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )

    def _setup_main_layout(self):
        """Main layout configuration"""
        # Main splitter
        main_splitter = QSplitter(Qt.Horizontal)

        # Left panel (vertical splitter)
        left_panel = QSplitter(Qt.Vertical)
        left_panel.addWidget(self.design_manager)
        left_panel.addWidget(self.component_lib)
        left_panel.setSizes([200, 100])

        # Combined layout
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(self.display_area)
        main_splitter.setSizes([250, 800])

        # Set the central widget
        container = QWidget()
        container.setLayout(QVBoxLayout())
        container.layout().addWidget(main_splitter)
        self.setCentralWidget(container)

    def _setup_menu(self):
        """Menu bar configuration"""
        self.setMenuBar(self.menu_manager.menu_bar)
        self.addToolBar(Qt.TopToolBarArea, self.toolbar_manager)

    @pyqtSlot(Design)
    def updateMainDesign(self, updated_design):
        """Handle design update"""
        try:
            self.design = updated_design
            self.design_updated_flag = True

            # Ensure the directory exists
            os.makedirs('./picture', exist_ok=True)

            # Update the topology image
            self.design.topology.save_image('./picture/topology.png')
            self.topo_display.show_image('./picture/topology.png')

            # Update the GDS layout
            self.design.gds.save_svg('./picture/gds.svg')
            self.gds_display.show_image('./picture/gds.svg')

        except Exception as e:
            self._show_error_dialog("Design update failed", str(e))

    def _show_error_dialog(self, title, message):
        """Display an error dialog"""
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.critical(
            self,
            title,
            f"{message}\n\nPossible reasons:\n1. File permission issues\n2. Data format errors\n3. Components not initialized",
            QMessageBox.Ok
        )