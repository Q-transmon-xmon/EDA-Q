import sys
import copy
import numpy as np

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QTreeWidget,
                             QTreeWidgetItem, QHBoxLayout, QVBoxLayout,
                             QLabel, QLineEdit, QScrollArea, QFormLayout, QPushButton,
                             QMessageBox)
from PyQt5.QtCore import Qt
from api.design import Design


class Dialog_NestedDictViewer(QMainWindow):
    # designUpdated = QtCore.pyqtSignal(object)  # definition designUpdated signal
    def __init__(self, design):
        super().__init__()
        self.setWindowTitle("GDS Layout Modification")
        self.setGeometry(100, 100, 800, 600)

        # Set the font for the entire interface
        font = QtGui.QFont("Microsoft YaHei", 10)
        self.setFont(font)

        # Create main window widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Create horizontal layout
        self.layout = QHBoxLayout(self.central_widget)

        # Create tree widget
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Design")
        self.tree.setMinimumWidth(150)
        self.tree.setFont(font)

        # Create right content area
        self.content_widget = QWidget()
        self.content_layout = QFormLayout(self.content_widget)
        self.content_layout.setVerticalSpacing(12)

        # Create scroll area
        self.scroll = QScrollArea()
        self.scroll.setWidget(self.content_widget)
        self.scroll.setWidgetResizable(True)

        # Add widgets to layout
        self.layout.addWidget(self.tree)
        self.layout.addWidget(self.scroll)

        # Create Window_Gds instance
        self.window_gds = Window_Gds(design, self.tree, self.content_layout)

        # Connect window resize event
        self.central_widget.resizeEvent = self.on_resize

    def on_resize(self, event):
        self.tree.setMinimumWidth(150)
        self.scroll.setMaximumWidth(self.central_widget.width() - 150)
        self.scroll.setMinimumWidth(300)



class Window_Gds(QtCore.QObject):
    designUpdated = QtCore.pyqtSignal(object)

    def __init__(self, design, tree, content_layout):
        super().__init__()
        self.design = design
        self.tree = tree
        self.content_layout = content_layout
        self.data = copy.deepcopy(design.options)
        self.current_item = None
        self.original_values = {}  # Store original values and type information

        # Populate tree widget
        self.populate_tree(self.data)

        # Connect signals
        self.tree.itemClicked.connect(self.on_item_clicked)

    def populate_tree(self, data, parent=None):
        for key, value in data.items():
            if parent is None:
                item = QTreeWidgetItem(self.tree)
            else:
                item = QTreeWidgetItem(parent)

            item.setText(0, str(key))
            if isinstance(value, dict):
                if any(isinstance(v, dict) for v in value.values()):
                    self.populate_tree(value, item)
                    item.setExpanded(True)
                else:
                    self.display_dict(value, item)

    def display_dict(self, dict_data, item):
        if not isinstance(dict_data, dict):
            return

        self.current_path = [item.text(0) for item in self.get_path(item)]
        for key, value in dict_data.items():
            if isinstance(value, dict):
                continue

            # Store original values and type information
            path_key = '.'.join(self.current_path + [str(key)])
            self.original_values[path_key] = {
                'value': value,
                'type': type(value),
                'is_numpy': isinstance(value, np.ndarray)
            }

            # Create label and line edit
            line_edit = QLineEdit(str(value))
            line_edit.setMinimumWidth(300)
            line_edit.setProperty("path_key", path_key)
            line_edit.textChanged.connect(self.on_text_changed)
            self.content_layout.addRow(QLabel(f"{key} ({type(value).__name__}):"), line_edit)

        # Add save button
        if dict_data:
            save_button = QPushButton("Save")
            save_button.clicked.connect(self.save_changes)
            self.content_layout.addRow(QLabel(), save_button)
            self.content_layout.setAlignment(save_button, Qt.AlignRight)

    def get_path(self, item):
        path = []
        current = item
        while current:
            path.insert(0, current)
            current = current.parent()
        return path

    def parse_value(self, text, original_info):
        """Parse input value based on original type"""
        try:
            if original_info['is_numpy']:
                # Handle numpy array
                try:
                    # Try to evaluate string as Python expression
                    value = eval(text)
                    return np.array(value, dtype=original_info['value'].dtype)
                except:
                    return original_info['value']  # Keep original value
            elif original_info['type'] == bool:
                return text.lower() in ('true', '1', 'yes', 'y', 't')
            elif original_info['type'] == int:
                return int(float(text))  # Allow decimal input but convert to integer
            elif original_info['type'] == float:
                return float(text)
            elif original_info['type'] == str:
                return text
            else:
                # For other types, try using eval
                try:
                    return eval(text)
                except:
                    return text
        except:
            return None

    def on_text_changed(self, text):
        line_edit = self.sender()
        path_key = line_edit.property("path_key")
        original_info = self.original_values.get(path_key)

        if not original_info:
            return

        # Parse new value
        new_value = self.parse_value(text, original_info)

        if new_value is not None:
            # Update data
            current_dict = self.data
            path_parts = path_key.split('.')
            for part in path_parts[:-1]:
                current_dict = current_dict[part]
            current_dict[path_parts[-1]] = new_value
            line_edit.setStyleSheet("")
        else:
            # Set red border on parse failure
            line_edit.setStyleSheet("border: 1px solid red;")

    def on_item_clicked(self, item, column):
        self.current_item = item
        # Clear right content
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Get full path
        path = []
        current = item
        while current:
            path.insert(0, current.text(0))
            current = current.parent()

        # Find corresponding dictionary
        current_dict = self.data
        for key in path:
            if key in current_dict:
                current_dict = current_dict[key]

        self.display_dict(current_dict, item)
    def save_changes(self):
        try:
            # Update original design object
            self.design.inject_options(self.data)
            # Emit update signal
            self.designUpdated.emit(self.design)

            if self.current_item:
                self.on_item_clicked(self.current_item, 0)

            # Show success message
            QMessageBox.information(None, "Success", "Changes have been saved")
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Save failed: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    design = Design()
    design.generate_topology(qubits_num=16, topo_col=4)
    design.generate_qubits(chip_name='Chip_0', dist=2000, qubits_type='Xmon',
                           topo_positions=design.topology.positions)
    viewer = Dialog_NestedDictViewer(design)

    def updateMainDesign(updated_design):
        design = updated_design
        design.topology.show_image()
        print("Main window design has been updated")

    viewer.window_gds.designUpdated.connect(updateMainDesign)
    viewer.show()

    sys.exit(app.exec_())