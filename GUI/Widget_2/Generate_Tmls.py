import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox
)
from addict import Dict
from api.design import Design

class Dialog_tmls(QDialog):
    # Signal for design updates
    designUpdated = QtCore.pyqtSignal(object)

    def __init__(self, design, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Transmission Line")
        self.setFont(QFont("Microsoft YaHei", 10))  # Use an integer for font size
        self.resize(800, 450)  # Set initial size of the dialog
        self.design = design

        # Predefined dictionary template for transmission lines
        self.tml_ops_template = Dict(
            name="tmls0",
            type="TransmissionPath",
            chip_name="chip0",
            pos=[(-1000, 1100), (-1000, 1250), (15000, 1250), (15000, 1000)],
            corner_radius=90
        )

        # Store input fields and their types
        self.lineEdits = {}
        self.input_types = {}

        # Main layout for the dialog
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setAlignment(QtCore.Qt.AlignCenter)  # Center align center within the dialog
        self.mainLayout.setContentsMargins(30, 30, 30, 30)  # Set outer margins
        self.mainLayout.setSpacing(10)  # Set spacing between widgets

        # Title label
        titleLabel = QLabel("Transmission Line Configuration")
        titleLabel.setFont(QFont("Arial", 14, QFont.Bold))  # Title font styling
        titleLabel.setAlignment(QtCore.Qt.AlignCenter)  # Center alignment
        self.mainLayout.addWidget(titleLabel)

        # Instructions label
        instructionsLabel = QLabel("Please enter the details below. Use 'Tab' to set defaults:")
        instructionsLabel.setWordWrap(True)  # Enable word wrapping
        instructionsLabel.setAlignment(QtCore.Qt.AlignCenter)  # Center alignment
        self.mainLayout.addWidget(instructionsLabel)

        # Add spacing between the instructions and input fields
        self.mainLayout.addSpacing(10)  # Add spacing for better separation

        # Dynamically generate input fields with default values
        self.loadInputs()

        # Create button layout
        self.createButtonLayout()

    def loadInputs(self):
        """Dynamically generate input fields with predefined values"""
        labels = {
            "name": "Tml name",
            "type": "Tml type",
            "chip_name": "Chip name",
            "pos": "Tml position",
            "corner_radius": "Corner Radius"
        }

        for key, value in self.tml_ops_template.items():
            # Create a horizontal layout for each input field
            layout = QHBoxLayout()

            # Create label with fixed width for alignment
            label = QLabel(f"{labels[key]}:")
            label.setFixedWidth(150)
            layout.addWidget(label)

            # Create input field with default value as placeholder text
            line_edit = QLineEdit()
            line_edit.setPlaceholderText(str(value))  # Set default value
            layout.addWidget(line_edit)

            # Store input field and its type
            self.lineEdits[key] = line_edit
            self.input_types[key] = type(value)

            # Add the layout to the main layout
            self.mainLayout.addLayout(layout)

            # Connect the event to allow using Tab to accept the default value
            line_edit.installEventFilter(self)  # Install an event filter for the line edit

        self.mainLayout.addStretch()  # Push layout content to the top

    def eventFilter(self, source, event):
        """Event filter for handling Tab key to set default values"""
        if event.type() == QtCore.QEvent.KeyPress and event.key() == QtCore.Qt.Key_Tab:
            for key, line_edit in self.lineEdits.items():
                if line_edit.hasFocus():
                    # Set text to placeholder value on Tab press
                    if line_edit.text().strip() == "":
                        line_edit.setText(line_edit.placeholderText())
                    # Move to the next input field
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

        # Add buttons to the layout with right alignment
        buttonLayout.addStretch()  # Stretchable space before buttons
        buttonLayout.addWidget(okButton)
        buttonLayout.addWidget(cancelButton)

        # Add button layout to the main layout
        self.mainLayout.addLayout(buttonLayout)

        # Connect button events
        okButton.clicked.connect(self.submitValues)  # On OK button click, submit the values
        cancelButton.clicked.connect(self.reject)  # On Cancel button click, reject the dialog

    def submitValues(self):
        """Process user input and handle the outcomes"""
        tml_ops = Dict()
        valid_input = True

        for key, line_edit in self.lineEdits.items():
            value_str = line_edit.text() if line_edit.text() else line_edit.placeholderText()  # Capture input
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

                tml_ops[key] = converted_value  # Save to updated dictionary
            except (ValueError, SyntaxError) as e:
                QMessageBox.warning(self, "Invalid Input", f"Invalid input for {key}: {e}")
                valid_input = False
                break

        # Check if all parameters are complete
        if valid_input and all(line_edit.text().strip() or line_edit.placeholderText() for line_edit in self.lineEdits.values()):
            print("User input values:", tml_ops)
            self.design.gds.transmission_lines.add(options=tml_ops)
            self.designUpdated.emit(self.design)  # Emit design update signal
            self.accept()  # Close the dialog
        else:
            QMessageBox.warning(self, "Input Error", "Please ensure all fields are filled or use the default values.")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    # Create and display the dialog
    dialog = Dialog_tmls(design=Design())
    dialog.exec()

    sys.exit(app.exec())