import os
import sys

from api.design import Design

# Get the directory where the current script is located
current_path = os.path.dirname(os.path.abspath(__file__))
GUI_PATH = os.path.dirname(current_path)
PROJ_PATH = os.path.dirname(GUI_PATH)

# Add paths
sys.path.append(GUI_PATH)
sys.path.append(PROJ_PATH)

from PyQt5.QtGui import QFont, QDesktopServices
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMenuBar,
                             QAction, QMenu, QFileDialog, QMessageBox)
from PyQt5.QtCore import pyqtSignal, QObject, QUrl
from GUI_3_4_6.gui_modules.global_state import global_state  # Import global state


class MenuBarManager(QObject):
    # New signals
    save_as_requested = pyqtSignal(str)  # Signal for save as path
    toggle_design_manager = pyqtSignal(bool)  # Signal for design manager visibility
    toggle_component_lib = pyqtSignal(bool)  # Signal for component library visibility

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.menu_bar = self._create_menu_bar()

    def _create_menu_bar(self):
        """Create the complete menu structure (adjusted version based on requirements)"""
        menu_bar = QMenuBar()

        # Updated menu structure
        menus = {
            "File": [
                ("Open", "Ctrl+O", self._handle_import),
                ("Save", "Ctrl+S", self._handle_save),
                ("Save As...", "Ctrl+Shift+S", self._handle_save_as),
                None,  # Separator
                ("Exit", "Ctrl+Q", self.parent.close)
            ],
            "Edit": [
                ("Undo", "Ctrl+Z", self._handle_undo),
                ("Redo", "Ctrl+Y", self._handle_redo),
                ("Export GDS", "Ctrl+E", self._handle_export_gds),  # New export GDS feature
                None,
                ("Delete", "Del", self._handle_delete)
            ],
            "View": [
                self._create_checkable_action("Show Design Manager", True, self._toggle_design_manager),
                self._create_checkable_action("Show Component Library", True, self._toggle_component_lib)
            ],
            "Tools": [
                ("Settings", None, self._handle_settings),
                ("Options", None, self._handle_options)
            ],
            "Help": [
                ("Documentation", "F1", self._handle_documentation),
                ("About", None, self._handle_about)
            ]
        }

        # Dynamically create menu items
        for menu_name, actions in menus.items():
            menu = menu_bar.addMenu(menu_name)
            for action_config in actions:
                if action_config is None:
                    menu.addSeparator()
                    continue

                if isinstance(action_config, QAction):  # Handle preset action
                    menu.addAction(action_config)
                else:
                    text, shortcut, handler = action_config
                    action = QAction(text, menu_bar)
                    if shortcut:
                        action.setShortcut(shortcut)
                    action.triggered.connect(handler)
                    menu.addAction(action)

        return menu_bar

    def _create_checkable_action(self, text, checked, handler):
        """Create a checkable action"""
        action = QAction(text, self.parent)
        action.setCheckable(True)
        action.setChecked(checked)
        action.triggered.connect(handler)
        return action

    def _handle_import(self):
        """Handle design import operation (using import_options version)"""
        path, _ = QFileDialog.getOpenFileName(
            self.parent,
            "Import Design Configuration",
            "",
            "Configuration Files (*.txt);;All Files (*)"
        )

        if not path:
            return

        try:
            # Create a temporary design instance for import
            temp_design = Design()
            imported_options = temp_design.import_options(path)

            # Generate design name (based on file name + uniqueness check)
            base_name = os.path.splitext(os.path.basename(path))[0]
            design_name = base_name
            counter = 1
            while global_state.design_exists(design_name):
                design_name = f"{base_name}_{counter}"
                counter += 1

            # Create a formal design entry (with automatic path management)
            global_state.create_design(design_name)
            current_design = global_state.get_design(design_name)

            # Inject imported parameters into the new design
            current_design.inject_options(imported_options)

            # Automatically associate file path
            global_state.update_design_path(design_name, path)

            # Update current design
            global_state.update_current_design_name(design_name)

            QMessageBox.information(
                self.parent,
                "Import Successful",
                f"Configuration successfully imported: {design_name}\nNumber of parameters: {len(imported_options)}"
            )
        except Exception as e:
            QMessageBox.critical(
                self.parent,
                "Import Error",
                f"Import failed: {str(e)}\n{getattr(e, 'args', '')}"
            )

    # region File operation handling
    def _handle_save(self):
        """Handle save operation (supporting metadata path)"""
        try:
            current_name = global_state.get_current_design_name()
            if not current_name:
                QMessageBox.warning(self.parent, "Warning", "No active design")
                return

            # Get existing metadata
            metadata = global_state.get_design_metadata(current_name)
            if not metadata:
                self._handle_save_as()
                return

            design_instance, existing_path = metadata

            if existing_path:
                # Use the design object's own export method
                design_instance.export_options(existing_path)
                QMessageBox.information(
                    self.parent,
                    "Save Successful",
                    f"Design saved to: {existing_path}"
                )
            else:
                # Trigger save as if path does not exist
                self._handle_save_as()

        except Exception as e:
            QMessageBox.critical(
                self.parent,
                "Save Error",
                f"Save failed: {str(e)}"
            )

    def _handle_save_as(self):
        """Handle save as operation (complete metadata update)"""
        try:
            current_name = global_state.get_current_design_name()
            if not current_name:
                QMessageBox.warning(self.parent, "Warning", "No active design")
                return

            metadata = global_state.get_design_metadata(current_name)
            if not metadata:
                raise ValueError("Design metadata does not exist")

            design_instance, _ = metadata

            # Get suggested file name
            suggested_name = f"{current_name}.txt"

            # Pop up save dialog
            path, _ = QFileDialog.getSaveFileName(
                self.parent,
                "Save Design Configuration",
                suggested_name,
                "Configuration Files (*.txt);;All Files (*)"
            )

            if not path:
                return

            # Ensure file extension
            if not path.lower().endswith(".txt"):
                path += ".txt"

            # Call the design object's export method
            design_instance.export_options(path)

            # Update the path in the global state
            global_state.update_design_path(current_name, path)

            QMessageBox.information(
                self.parent,
                "Save Successful",
                f"Configuration saved to: {path}\nPath updated"
            )

        except Exception as e:
            QMessageBox.critical(
                self.parent,
                "Save Error",
                f"Save failed: {str(e)}"
            )

    # endregion
    # region Edit operation handling
    def _handle_undo(self):
        """Undo operation"""
        if global_state.can_undo():
            try:
                global_state.undo()
            except NotImplementedError as e:
                QMessageBox.warning(self.parent, "Warning", str(e))

    def _handle_redo(self):
        """Redo operation"""
        if global_state.can_redo():
            try:
                global_state.redo()
            except NotImplementedError as e:
                QMessageBox.warning(self.parent, "Warning", str(e))

    def _handle_delete(self):
        """Delete current design"""
        current_name = global_state.get_current_design_name()
        if current_name:
            reply = QMessageBox.question(
                self.parent, "Confirm Delete",
                f"Delete design '{current_name}'?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                try:
                    global_state.delete_design(current_name)
                except Exception as e:
                    QMessageBox.critical(self.parent, "Error", str(e))

    # endregion

    # region View operation handling
    def _toggle_design_manager(self, state):
        """Toggle design manager visibility"""
        self.toggle_design_manager.emit(state)

    def _toggle_component_lib(self, state):
        """Toggle component library visibility"""
        self.toggle_component_lib.emit(state)

    # endregion

    # region Tool and Help operations
    def _handle_settings(self):
        """Open settings dialog (placeholder)"""
        QMessageBox.information(self.parent, "Settings", "Settings dialog placeholder")

    def _handle_options(self):
        """Open options dialog (placeholder)"""
        QMessageBox.information(self.parent, "Options", "Options dialog placeholder")

    def _handle_documentation(self):
        """Open local documentation"""
        doc_path = os.path.abspath("../tutorial.pdf")
        if os.path.exists(doc_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(doc_path))
        else:
            QMessageBox.warning(self.parent, "Error", "Documentation file not found")

    def _handle_about(self):
        """Show about page"""
        about_url = QUrl("https://yourdomain.com/about")
        QDesktopServices.openUrl(about_url)

    # endregion

    def _handle_export_gds(self):
        """Handle GDS export operation"""
        current_name = global_state.get_current_design_name()
        if not current_name:
            QMessageBox.warning(self.parent, "Warning", "No active design to export")
            return

        try:
            # Get the current design object (assuming global_state has a method to get the design object)
            current_design = global_state.get_design(current_name)
            if not current_design:
                raise ValueError("Unable to get design object")

            path, _ = QFileDialog.getSaveFileName(
                self.parent,
                "Export GDS File",
                "",
                "GDSII Files (*.gds);;All Files (*)"
            )

            if not path:
                return

            # Ensure correct file extension
            if not path.lower().endswith(".gds"):
                path += ".gds"

            # Call the actual save method
            saved_path = current_design.gds.save_gds(path)

            QMessageBox.information(
                self.parent,
                "Export Successful",
                f"GDS file successfully exported to: {saved_path}"
            )
        except Exception as e:
            QMessageBox.critical(
                self.parent,
                "Export Error",
                f"Export failed: {str(e)}"
            )


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

        # Initialize view states
        self.design_manager_visible = True
        self.component_lib_visible = True

    def init_ui(self):
        self.setWindowTitle("EDA Tool")
        self.setGeometry(100, 100, 1024, 768)

        # Initialize menu bar
        self.menu_manager = MenuBarManager(self)
        self.setMenuBar(self.menu_manager.menu_bar)

        # Connect view toggle signals
        self.menu_manager.toggle_design_manager.connect(self.toggle_design_manager)
        self.menu_manager.toggle_component_lib.connect(self.toggle_component_lib)

    def toggle_design_manager(self, visible):
        """Control design manager visibility"""
        self.design_manager_visible = visible
        # Here you need to actually control the visibility of the corresponding component, for example:
        # self.design_manager.setVisible(visible)
        print(f"Design Manager visibility: {visible}")

    def toggle_component_lib(self, visible):
        """Control component library visibility"""
        self.component_lib_visible = visible
        # Here you need to actually control the visibility of the corresponding component, for example:
        # self.component_library.setVisible(visible)
        print(f"Component Library visibility: {visible}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())