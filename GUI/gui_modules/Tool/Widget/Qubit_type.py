import sys
from PyQt5 import QtCore
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QApplication, QDialog, QHBoxLayout, QVBoxLayout,
                             QLabel, QSizePolicy, QSpacerItem, QMessageBox, QComboBox, QDialogButtonBox)

from GUI.gui_modules.Manager.design_validator import design_validator
from api.design import Design

# Add Import
import toolbox
from library.qubits import module_name_list

class Dialog_Selection(QDialog):
    designUpdated = QtCore.pyqtSignal(object)

    def __init__(self, design):
        super().__init__()

        self.design = design
        self.setWindowTitle("Select Qubit Type")
        self.setGeometry(100, 100, 400, 250)  # Set window size and initial position

        # set font
        font = QFont("Arial", 10)
        self.setFont(font)

        # Create main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 40, 20, 20)

        # title tag
        title_label = QLabel("Please select the type of qubit you want to generate:")
        title_label.setStyleSheet("font-size: 22px; font-weight: bold; color: black;")
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        title_label.setWordWrap(True)
        main_layout.addWidget(title_label)

        # Add fixed intervals
        main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Create dropdown layout
        combo_layout = QHBoxLayout()

        # Generate a dynamic option list
        try:
            # Convert to camel hump naming
            class_names = [toolbox.convert_to_camel_case(name) for name in module_name_list]
            # Filter invalid values and ensure they are not empty
            valid_names = [name for name in class_names if isinstance(name, str) and name]
            if not valid_names:
                valid_names = ["DefaultQubitType"]
        except Exception as e:
            print(f"Error generating options: {str(e)}")
            valid_names = ["Xmon", "Transmon"]  # Alternative options

        # Create dropdown menu
        self.type_combo = QComboBox()
        self.type_combo.addItems(valid_names)
        self.type_combo.setFixedWidth(250)  # Set the fixed width to250px
        self.type_combo.setFixedHeight(25)  # Set the fixed height to40px
        # Center the dropdown menu
        combo_layout.addStretch(1)
        combo_layout.addWidget(self.type_combo)
        combo_layout.addStretch(1)

        # Add to main layout
        main_layout.addLayout(combo_layout)

        # Add bottom spacing
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Add button box
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.on_confirm)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

        self.setLayout(main_layout)
        self.move(400, 400)

    def on_confirm(self):
        """Process confirmation button click event"""
        selected_type = self.type_combo.currentText()
        print(f"You selected: {selected_type}")

        # inspecttopologyDoes it exist
        if design_validator.is_component_empty(self.design, 'topology'):
            QMessageBox.warning(self, "Warning", "Topology does not exist or is not initialized.")
            return

        try:
            # Generate quantum bits
            self.design.generate_qubits(
                topology=True,
                qubits_type=selected_type
            )
            self.designUpdated.emit(self.design)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate qubits: {str(e)}")
            self.reject()

    def on_qubit_selected(self):
        """Handling dropdown menu option change events"""
        selected_type = self.type_combo.currentText()
        print(f"You selected: {selected_type}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    design = Design()
    dialog = Dialog_Selection(design)
    dialog.exec_()