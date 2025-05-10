import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QDialog, QLabel, QLineEdit, QHBoxLayout,
                             QVBoxLayout, QDialogButtonBox, QMessageBox, QPushButton)
from PyQt5.QtCore import Qt
from addict import Dict
from api.design import Design


class Dialog_cpls(QDialog):
    # Define a signal for design updates
    designUpdated = QtCore.pyqtSignal(object)

    def __init__(self, design, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Generate Coupling Lines")
        self.setFont(QFont("Microsoft YaHei", int(10)))  # Set font for the dialog
        self.resize(500, 350)  # Set initial size
        self.design = design

        # Default values
        self.default_values = Dict(
            coupling_line_type="CouplingLineStraight",
            chip_layer_name="chip0"
        )

        # Store input fields and types
        self.lineEdits = {}
        self.input_types = {}

        # Main layout
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(20, 20, 20, 20)  # Set margins for the main layout
        self.mainLayout.setSpacing(25)  # Increase spacing between controls in the layout

        # Title label
        titleLabel = QLabel("Coupling Line Generation")
        titleLabel.setFont(QFont("Arial", 14, QFont.Bold))
        titleLabel.setAlignment(Qt.AlignCenter)
        self.mainLayout.addWidget(titleLabel)

        # Instructions label
        instructionsLabel = QLabel("Please enter the details for the coupling lines below:")
        instructionsLabel.setAlignment(Qt.AlignCenter)
        instructionsLabel.setWordWrap(True)  # Enable word wrapping for long text
        self.mainLayout.addWidget(instructionsLabel)

        # Dynamically generate input fields with default values
        self.loadInputs()

        # Button layout
        self.createButtonLayout()

    def loadInputs(self):
        """Dynamically generate input fields with default values"""
        labels = {
            "coupling_line_type": "CouplingLine type:",
            "chip_layer_name": "Chip Name:"
        }

        for key, value in self.default_values.items():
            # Create horizontal layout for each input field
            layout = QHBoxLayout()

            # Create label
            label = QLabel(labels[key])
            label.setFixedWidth(180)  # Set fixed width for alignment
            layout.addWidget(label)

            # Create input field with placeholder text
            line_edit = QLineEdit()
            line_edit.setPlaceholderText(str(value))  # Set default value as placeholder
            layout.addWidget(line_edit)

            # Store input field and type
            self.lineEdits[key] = line_edit
            self.input_types[key] = type(value)

            # Add to the main layout
            self.mainLayout.addLayout(layout)

            # Adjust spacing after each input field
            self.mainLayout.addSpacing(10)  # Add spacing between input fields

            # Connect the event to allow using Tab to accept the default value
            line_edit.installEventFilter(self)  # Install an event filter for the line edit

        self.mainLayout.addStretch()  # Add stretch to push the layout to the top

    def eventFilter(self, source, event):
        """Handle Tab key event to set default values"""
        if event.type() == QtCore.QEvent.KeyPress and event.key() == QtCore.Qt.Key_Tab:
            for key, line_edit in self.lineEdits.items():
                if line_edit.hasFocus():
                    # Set text to placeholder value on Tab press
                    if line_edit.text().strip() == "":
                        line_edit.setText(line_edit.placeholderText())
                    # Move focus to the next input field
                    next_index = list(self.lineEdits.keys()).index(key) + 1
                    if next_index < len(self.lineEdits):
                        next_line_edit = self.lineEdits[list(self.lineEdits.keys())[next_index]]
                        next_line_edit.setFocus()
                    return True
        return super().eventFilter(source, event)

    def createButtonLayout(self):
        """Create and set up the button layout"""
        buttonLayout = QHBoxLayout()
        okButton = QPushButton("OK")
        cancelButton = QPushButton("Cancel")

        # Set button sizes
        okButton.setFixedSize(80, 30)
        cancelButton.setFixedSize(80, 30)

        # Add buttons to layout with proper alignment
        buttonLayout.addStretch()  # Add space before buttons to right-align
        buttonLayout.addWidget(okButton)
        buttonLayout.addWidget(cancelButton)

        # Add button layout to the main layout
        self.mainLayout.addLayout(buttonLayout)

        # Remove spacing between input fields and button layout
        self.mainLayout.addSpacing(10)  # Smaller spacing between inputs and button layout

        # Connect button events
        okButton.clicked.connect(self.submitValues)  # OK button
        cancelButton.clicked.connect(self.reject)  # Cancel button

    def submitValues(self):
        """Process user input and return result"""
        coupling_line_params = Dict()
        valid_input = True

        for key, line_edit in self.lineEdits.items():
            value_str = line_edit.text() if line_edit.text() else line_edit.placeholderText()
            expected_type = self.input_types[key]

            try:
                # Convert input value based on type
                if expected_type == list:
                    converted_value = eval(value_str)
                    if not isinstance(converted_value, list):
                        raise ValueError("Input value is not a valid list")
                elif expected_type == tuple:
                    converted_value = eval(value_str)
                    if not isinstance(converted_value, tuple):
                        raise ValueError("Input value is not a valid tuple")
                else:
                    converted_value = expected_type(value_str)

                coupling_line_params[key] = converted_value  # Save to updated dictionary
            except (ValueError, SyntaxError) as e:
                QMessageBox.warning(self, "Invalid Input", f"Invalid input for {key}: {e}")
                valid_input = False
                break

        # Check if all parameters are provided
        if valid_input and all(line_edit.text().strip() or line_edit.placeholderText() for line_edit in self.lineEdits.values()):
            # Print result for verification
            print("User input values:", coupling_line_params)
            self.design.generate_coupling_lines(topology=True, qubits=True, cpls_type=coupling_line_params["coupling_line_type"], chip_name=coupling_line_params["chip_layer_name"])
            self.designUpdated.emit(self.design)  # Emit design update signal
            self.accept()  # Close dialog
        else:
            QMessageBox.warning(self, "Input Error", "Please fill all fields or use the default values.")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    design = Design()  # Assuming Design class exists
    dialog = Dialog_cpls(design=design)

    # If the dialog is accepted, print the input content
    if dialog.exec() == QDialog.Accepted:
        print("Dialog accepted")

    # Exit the application
    sys.exit(app.exec())