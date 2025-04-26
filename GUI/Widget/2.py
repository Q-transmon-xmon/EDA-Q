import sys
import copy

from PySide6 import QtCore, QtGui
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QTreeWidget,
                               QTreeWidgetItem, QHBoxLayout, QVBoxLayout,
                               QLabel, QLineEdit, QScrollArea, QFormLayout, QPushButton)
from PySide6.QtCore import Qt
from api.design import Design

class NestedDictViewer(QMainWindow):
    def __init__(self, design):
        super().__init__()
        self.setWindowTitle("Modification of GDS Layout")
        self.setGeometry(100, 100, 800, 600)

        # Set the font for the entire interface
        font = QtGui.QFont("Microsoft YaHei", 10)
        self.setFont(font)

        # Create the main widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Create horizontal layout
        self.layout = QHBoxLayout(self.central_widget)

        # Create tree control
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Design")
        self.tree.setMinimumWidth(150)  # Set the width of the left navigation bar
        self.tree.setFont(font)  # Set navigation bar font

        # Set the background color of the left navigation bar
        # self.tree.setStyleSheet("background-color: #f0f0f0;")

        # Create the right content area
        self.content_widget = QWidget()
        self.content_layout = QFormLayout(self.content_widget)
        self.content_layout.setVerticalSpacing(12)  # Set input box spacing

        # Create a scrolling area
        self.scroll = QScrollArea()
        self.scroll.setWidget(self.content_widget)
        self.scroll.setWidgetResizable(True)

        # Add components to layout
        self.layout.addWidget(self.tree)
        self.layout.addWidget(self.scroll)

        # create Window_Gds example
        self.window_gds = Window_Gds(design, self.tree, self.content_layout)

        # Connection window size change signal
        self.central_widget.resizeEvent = self.on_resize

    def on_resize(self, event):
        # Keep the width of the left navigation bar unchanged
        self.tree.setMinimumWidth(150)
        # Adjust the width of the content area on the right side,Maximum not exceeding the width of the central window minus150pixel
        self.scroll.setMaximumWidth(self.central_widget.width() - 150)
        self.scroll.setMinimumWidth(300)

class Window_Gds(QtCore.QObject):
    # Define a signal for design updates
    designUpdated = QtCore.Signal(object)

    def __init__(self, design, tree, content_layout):
        super().__init__()
        self.design = design
        self.tree = tree
        self.content_layout = content_layout
        self.data = copy.deepcopy(design.options)

        # Fill in tree control
        self.populate_tree(self.data)

        # joining signal
        self.tree.itemClicked.connect(self.on_item_clicked)

    def populate_tree(self, data, parent=None):
        for key, value in data.items():
            if parent is None:
                item = QTreeWidgetItem(self.tree)
            else:
                item = QTreeWidgetItem(parent)

            item.setText(0, str(key))
            if isinstance(value, dict):
                if any(isinstance(v, dict) for v in value.values()):  # If there are still nested dictionaries
                    self.populate_tree(value, item)
                    item.setExpanded(True)  # Expand nodes
                else:  # If it is the last level dictionary
                    self.display_dict(value, item)

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
        for key in path:
            if key in current_dict:
                current_dict = current_dict[key]

        self.display_dict(current_dict, item)

    def display_dict(self, dict_data, item):
        self.current_path = [item.text(0) for item in self.get_path(item)]  # Save the current path for updating purposes
        for key, value in dict_data.items():
            # Create tags and input boxes
            line_edit = QLineEdit(str(value))
            line_edit.setMinimumWidth(300)  # Set the minimum width of the input box
            line_edit.textChanged.connect(lambda text, k=key: self.update_value(k, text))
            self.content_layout.addRow(QLabel(key + ":"), line_edit)

        # Add Save button
        if dict_data:  # If the dictionary is not empty
            save_button = QPushButton("Save")
            save_button.clicked.connect(self.save_changes)
            self.content_layout.addRow(QLabel(), save_button)
            self.content_layout.setAlignment(save_button, Qt.AlignRight)  # Place the save button in the bottom right corner

    def get_path(self, item):
        path = []
        current = item
        while current:
            path.insert(0, current)
            current = current.parent()
        return path

    def update_value(self, key, new_value):
        # update data
        current_dict = self.data
        for path_key in self.current_path[:-1]:  # Navigate to the correct dictionary
            current_dict = current_dict[path_key]
        current_dict[key] = new_value

    def save_changes(self):
        # Send design update signal
        # Update the original design object
        self.design.inject_options(options=copy.deepcopy(self.data))
        self.designUpdated.emit(self.design)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    design = Design()
    design.generate_topology(qubits_num=16, topo_col=4)
    design.generate_qubits(chip_name='Chip_0', dist=2000, qubits_type='Xmon',
                           topo_positions=design.topology.positions)
    viewer = NestedDictViewer(design)
    viewer.window_gds.designUpdated.connect(lambda design: print("Design updated:", design))
    viewer.show()
    sys.exit(app.exec())