import sys

from PySide6 import QtCore
from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from addict import Dict
from api.design import Design

class Dialog_pins(QDialog):
    # Define a signal for design updates
    designUpdated = QtCore.Signal(object)

    def __init__(self, design, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Generate Pins")
        self.setFont(QFont("Microsoft YaHei", 10.5))
        self.resize(500, 300)
        self.design = design
        # Default value
        self.default_values = Dict(
            name="pin0",
            type="LaunchPad",
            chip="chip0",
            pos=(0, 0),
            outline=[]
        )

        # Store input boxes and types
        self.lineEdits = {}
        self.input_types = {}

        # Main layout
        self.mainLayout = QVBoxLayout(self)

        # Dynamically generate input boxes
        self.loadInputs()

        # BUTTON LAYOUT
        self.buttonLayout = QHBoxLayout()
        self.okButton = QPushButton("OK")
        self.cancelButton = QPushButton("Cancel")

        # Set button size
        self.okButton.setFixedSize(80, 30)
        self.cancelButton.setFixedSize(80, 30)

        # Add button to layout
        self.buttonLayout.addWidget(self.okButton)
        self.buttonLayout.addWidget(self.cancelButton)
        self.buttonLayout.setAlignment(Qt.AlignRight)  # Align the button to the right
        self.mainLayout.addLayout(self.buttonLayout)

        # Connect button events
        self.okButton.clicked.connect(self.submitValues)
        self.cancelButton.clicked.connect(self.reject)

    def loadInputs(self):
        """Dynamically generate input boxes"""
        labels = {
            "name": "Name",
            "type": "Type",
            "chip": "Chip",
            "pos": "Position",
            "outline": "Outline"
        }

        for key, value in self.default_values.items():
            # Create horizontal layout
            layout = QHBoxLayout()

            # Create label
            label = QLabel(f"{labels[key]}:")
            layout.addWidget(label)

            # Create input box
            line_edit = QLineEdit()
            line_edit.setText(str(value))  # Set default values
            layout.addWidget(line_edit)

            # Save input box and type
            self.lineEdits[key] = line_edit
            self.input_types[key] = type(value)

            # Add to main layout
            self.mainLayout.addLayout(layout)

    def submitValues(self):
        """Process user input and print results"""
        pin_ops = Dict()
        valid_input = True

        for key, line_edit in self.lineEdits.items():
            value_str = line_edit.text()
            expected_type = self.input_types[key]

            try:
                # Convert input values based on type
                if expected_type == list:
                    # If it is a list type, attempt to parse as Python list
                    converted_value = eval(value_str)
                    if not isinstance(converted_value, list):
                        raise ValueError("Input value is not a valid list")
                elif expected_type == tuple:
                    # If it is a tuple type, attempt to parse as Python tuple
                    converted_value = eval(value_str)
                    if not isinstance(converted_value, tuple):
                        raise ValueError("Input value is not a valid tuple")
                else:
                    converted_value = expected_type(value_str)

                pin_ops[key] = converted_value  # Save to the updated dictionary
            except (ValueError, SyntaxError) as e:
                QMessageBox.warning(self, "Invalid Input", f"Invalid input for {key}: {e}")
                valid_input = False
                break

        if valid_input:
            # Print results
            print("User input values:", pin_ops)
            self.design.gds.pins.add(options=pin_ops)
            self.designUpdated.emit(self.design)  # Send design update signal
            # QMessageBox.information(self, "Submitted successfully", f"The input value has been submitted:\n{pin_ops}")
            self.accept()  # Close window


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Create and display a dialog box
    dialog = Dialog_pins(design=Design())
    dialog.exec()

    sys.exit(app.exec())