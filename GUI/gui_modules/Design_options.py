# Design_options.py

from PyQt5.QtWidgets import QMessageBox, QInputDialog, QFileDialog
from api.design import Design  # Ensure Design is imported


class DesignOptions:
    def __init__(self, main_window):
        self.main_window = main_window

    def new_design(self):
        """Create a new design instance"""
        design_name, ok = QInputDialog.getText(self.main_window, "New Design", "Enter design name:")
        if ok and design_name:
            if design_name in self.main_window.designs:
                QMessageBox.warning(self.main_window, "Duplicate Name",
                                    f"Design '{design_name}' already exists!")
                return

            new_design = Design()  # Create a new Design instance
            self.main_window.designs[design_name] = (new_design, None)  # Store the Design instance and file path
            self.main_window.current_design = new_design
            self.main_window.design_manager.update_display()  # Update the tree structure in DesignManager

    def save_design(self):
        """Save the currently active Design instance"""
        if self.main_window.current_design is None:
            QMessageBox.warning(self.main_window, "No Design Selected",
                                "Please select a design to save.")
            return

        # Get the name and path corresponding to the current design
        design_name = self._find_design_name_by_instance()
        if not design_name:
            QMessageBox.critical(self.main_window, "Error", "Design not found!")
            return

        _, file_path = self.main_window.designs[design_name]
        if file_path is None:
            self.save_design_as()  # Trigger Save As if no path exists
        else:
            try:
                self.main_window.current_design.save(file_path)
                QMessageBox.information(self.main_window, "Save Design",
                                        "Design saved successfully.")
            except Exception as e:
                QMessageBox.critical(self.main_window, "Save Error",
                                     f"Failed to save design: {str(e)}")

    def save_design_as(self):
        """Save the currently active Design instance as a new file"""
        if self.main_window.current_design is None:
            QMessageBox.warning(self.main_window, "No Design Selected",
                                "Please select a design to save.")
            return

        design_name = self._find_design_name_by_instance()
        if not design_name:
            return

        file_path, _ = QFileDialog.getSaveFileName(self.main_window, "Save Design As",
                                                   "", "Design Files (*.design)")
        if file_path:
            try:
                self.main_window.current_design.save(file_path)
                # Update the file path while retaining the design name
                self.main_window.designs[design_name] = (self.main_window.current_design, file_path)
                QMessageBox.information(self.main_window, "Save Design",
                                        "Design saved successfully.")
            except Exception as e:
                QMessageBox.critical(self.main_window, "Save Error",
                                     f"Failed to save design: {str(e)}")

    def close_design(self):
        """Close the currently active Design instance"""
        if self.main_window.current_design is None:
            QMessageBox.warning(self.main_window, "No Design Selected",
                                "Please select a design to close.")
            return

        design_name = self._find_design_name_by_instance()
        if not design_name:
            return

        confirm = QMessageBox.question(self.main_window, "Confirm Close",
                                       f"Close design '{design_name}'?",
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            # Delete by design name
            del self.main_window.designs[design_name]

            # Automatically select the next available design
            if self.main_window.designs:
                next_design = next(iter(self.main_window.designs.values()))[0]
                self.main_window.current_design = next_design
            else:
                self.main_window.current_design = None

            self.main_window.design_manager.update_display()

    def _find_design_name_by_instance(self):
        """Find the corresponding design name by instance"""
        for name, (design, _) in self.main_window.designs.items():
            if design is self.main_window.current_design:
                return name
        QMessageBox.critical(self.main_window, "Error", "Current design not found!")
        return None