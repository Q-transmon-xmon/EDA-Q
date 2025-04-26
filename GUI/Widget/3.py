import sys
from copy import deepcopy  # Corrected the import for deepcopy

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QTreeWidget,
                               QTreeWidgetItem, QHBoxLayout, QVBoxLayout,
                               QLabel, QLineEdit, QScrollArea, QFormLayout)
from PySide6.QtCore import Qt
from api.design import Design

class MainWindow(QMainWindow):
    def __init__(self, design):
        super().__init__()
        self.design = design
        self.setWindowTitle("Nested Dictionary Viewer")
        self.setGeometry(100, 100, 800, 600)
        design_ops = deepcopy(design.options)  # Corrected the usage of deepcopy
        # sample data
        self.data = {
            "Device1": {
                "Channel1": {
                    "qubits": {
                        "Frequency": "5.5 GHz",
                        "Phase": "0.5 rad",
                        "Amplitude": "0.8"
                    }
                },
                "Channel2": {
                    "qubits": {
                        "Frequency": "4.8 GHz",
                        "Phase": "0.3 rad",
                        "Amplitude": "0.7"
                    }
                }
            },
            "Device2": {
                "Channel1": {
                    "qubits": {
                        "Frequency": "6.0 GHz",
                        "Phase": "0.4 rad",
                        "Amplitude": "0.9"
                    }
                }
            }
        }

        # Create the main widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create horizontal layout
        layout = QHBoxLayout(central_widget)

        # Create tree control
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Navigation")
        self.tree.setMinimumWidth(200)
        self.tree.itemClicked.connect(self.on_item_clicked)

        # Create the right content area
        self.content_widget = QWidget()
        self.content_layout = QFormLayout(self.content_widget)

        # Create a scrolling area
        scroll = QScrollArea()
        scroll.setWidget(self.content_widget)
        scroll.setWidgetResizable(True)

        # Add components to layout
        layout.addWidget(self.tree)
        layout.addWidget(scroll)

        # Fill in tree control
        self.populate_tree(self.data)

    def populate_tree(self, data, parent=None):
        for key, value in data.items():
            if parent is None:
                item = QTreeWidgetItem(self.tree)
            else:
                item = QTreeWidgetItem(parent)

            item.setText(0, str(key))
            if isinstance(value, dict):
                self.populate_tree(value, item)

    def on_item_clicked(self, item, column):
        # Clear the content on the right side
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Obtain the complete path
        path = []
        current = item
        while current:
            path.insert(0, current.text(0))
            current = current.parent()

        # Search for the corresponding dictionary
        current_dict = self.data
        for key in path[:-1]:  # Except for the last key
            if key in current_dict:
                current_dict = current_dict[key]

        # If the last item is qubits，Display its key value pairs
        if path[-1] == "qubits":
            qubits_dict = current_dict["qubits"]
            self.display_qubits(qubits_dict, path)

    def display_qubits(self, qubits_dict, path):
        self.current_path = path  # Save the current path for updating purposes
        for key, value in qubits_dict.items():
            # Create labels and input boxes
            line_edit = QLineEdit(str(value))
            line_edit.textChanged.connect(lambda text, k=key: self.update_value(k, text))
            self.content_layout.addRow(QLabel(key + ":"), line_edit)

    def update_value(self, key, new_value):
        # Update data
        current_dict = self.data
        for path_key in self.current_path[:-1]:  # Navigate to the correct dictionary
            current_dict = current_dict[path_key]
        current_dict["qubits"][key] = new_value


if __name__ == "__main__":
    app = QApplication(sys.argv)
    design = Design()  # Assuming Design is a valid class with an options attribute
    window = MainWindow(design)
    window.show()
    sys.exit(app.exec())