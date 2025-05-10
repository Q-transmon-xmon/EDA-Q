import os
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (QDockWidget, QWidget, QVBoxLayout,
                             QScrollArea, QSizePolicy, QMessageBox)
from .Ledit_Launcher import launch_ledit
from .component_config import get_component_config
from .component_handlers import ComponentHandlers
from .ui_builder import UIBuilder
from .styles import get_component_styles


class ComponentLibrary(QDockWidget):
    """Main component library dock widget"""

    operation_completed = pyqtSignal(str)

    def __init__(self, parent=None, current_design=None, categories=None):
        super().__init__("Component Library", parent)
        self.categories = categories or get_component_config()
        self.handlers = ComponentHandlers(current_design, parent)
        self.isResizing = False

        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self):
        """Initialize the user interface"""
        UIBuilder.setup_custom_titlebar(self)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        scroll.setWidget(content)

        main_layout = QVBoxLayout(content)
        main_layout.setAlignment(Qt.AlignTop)
        main_layout.setContentsMargins(8, 12, 8, 12)
        main_layout.setSpacing(8)

        for category in self.categories:
            UIBuilder.create_category(main_layout, category, self.handle_component_click)

        self.setWidget(scroll)

    def _setup_connections(self):
        """Setup signal connections"""
        self.operation_completed.connect(self._handle_operation_completed)

    def handle_component_click(self, command):
        """Handle component button clicks"""
        if handler := self.handlers.get_handler(command):
            try:
                handler()
                self.operation_completed.emit(f"Component {command} added successfully")
            except Exception as e:
                self.operation_completed.emit(f"Operation exception: {str(e)}")
        else:
            self.operation_completed.emit(f"Undefined operation: {command}")

    def handle_custom_button_clicked(self):
        """Handle custom button click (import GDS)"""
        try:
            launch_ledit(self)
            self.operation_completed.emit("LedIt launch initiated")
        except Exception as e:
            QMessageBox.critical(self, "Launch Error", f"Failed to start LedIt: {str(e)}")

    def toggle_floating(self):
        """Toggle floating state of the dock widget"""
        self.setFloating(not self.isFloating())

    def _handle_operation_completed(self, message):
        """Handle operation completion signals"""
        print(f"ComponentLibrary: {message}")

    def mousePressEvent(self, event):
        """Handle mouse press for resizing"""
        if event.button() == Qt.LeftButton:
            self.isResizing = True
            self.startPos = event.pos()

    def mouseMoveEvent(self, event):
        """Handle mouse move for resizing"""
        if self.isResizing:
            newWidth = self.width() + (event.x() - self.startPos.x())
            if 380 <= newWidth <= 550:
                self.setFixedWidth(newWidth)

    def mouseReleaseEvent(self, event):
        """Handle mouse release after resizing"""
        if event.button() == Qt.LeftButton:
            self.isResizing = False