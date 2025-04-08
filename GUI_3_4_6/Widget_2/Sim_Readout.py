import os
import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QDialog, QLabel, QLineEdit, QVBoxLayout,
                             QPushButton, QMessageBox, QHBoxLayout, QWidget, QDialogButtonBox)
from PyQt5.QtCore import Qt, QSettings, pyqtSignal
from api.design import Design


class Ui_Dialog:
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setMinimumSize(400, 300)  # Set minimum size of the dialog
        Dialog.setFont(QFont("Microsoft YaHei", 10))

        # Main layout
        self.mainLayout = QVBoxLayout(Dialog)
        self.mainLayout.addStretch(1)

        # Title label
        titleLabel = QLabel("Readout Simulation Configuration")
        titleLabel.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        titleLabel.setAlignment(Qt.AlignCenter)
        self.mainLayout.addWidget(titleLabel)

        # Instruction label
        instructionsLabel = QLabel("Please enter the parameters below:")
        instructionsLabel.setAlignment(Qt.AlignCenter)
        self.mainLayout.addWidget(instructionsLabel)

        # Input section
        self.layoutWidget = QWidget(Dialog)
        self.verticalLayout = QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setSpacing(20)
        self.verticalLayout.setContentsMargins(20, 20, 20, 20)

        self.defaults = ["q0", "5.6"]  # Default values
        self.lineEdits = []

        self.createLabeledInput("Qubit Name:", self.defaults[0])
        self.createLabeledInput("Qubit Frequency:", self.defaults[1])
        self.createLabeledInput("Pin0 Name:", "")
        self.createLabeledInput("Pin1 Name:", "")
        self.createLabeledInput("ReadoutLine Name:", "")
        self.createLabeledInput("Tml Name:", "")

        self.mainLayout.addWidget(self.layoutWidget)

        # Button box
        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(self.buttonBox.button(QDialogButtonBox.Ok))
        buttonLayout.addWidget(self.buttonBox.button(QDialogButtonBox.Cancel))

        self.mainLayout.addLayout(buttonLayout)
        self.mainLayout.addStretch(1)

    def createLabeledInput(self, label_text, default_value):
        """Create a labeled input field"""
        layout = QHBoxLayout()  # Create layout for each input item
        label = QLabel(label_text)
        label.setFixedWidth(150)  # Set label width
        line_edit = QLineEdit()
        line_edit.setMinimumWidth(200)
        line_edit.setPlaceholderText(default_value)  # Set default value
        layout.addWidget(label)
        layout.addWidget(line_edit)
        self.verticalLayout.addLayout(layout)  # Add to vertical layout
        self.lineEdits.append(line_edit)  # Save the input field

    def get_line_edits(self):
        return self.lineEdits


class Dialog_s21(QDialog):
    designUpdated = pyqtSignal(object)  # Define signal to notify design update

    def __init__(self, design):
        super().__init__()
        self.design = design
        self.settings = QSettings("MyCompany", "MyApp")

        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # Connect signals
        self.ui.buttonBox.accepted.connect(self.checkInputs)  # OK button
        self.ui.buttonBox.rejected.connect(self.reject)  # Cancel button

        # Install event filter for input fields
        for line_edit in self.ui.get_line_edits():
            line_edit.installEventFilter(self)

    def eventFilter(self, source, event):
        """Handle Tab key events to set default values"""
        if event.type() == QtCore.QEvent.KeyPress and event.key() == Qt.Key_Tab:
            for line_edit in self.ui.get_line_edits():
                if line_edit.hasFocus():
                    # Set default value if input field is empty
                    if line_edit.text().strip() == "":
                        line_edit.setText(line_edit.placeholderText())
                    # Move to the next input field
                    next_index = self.ui.get_line_edits().index(line_edit) + 1
                    if next_index < len(self.ui.get_line_edits()):
                        self.ui.get_line_edits()[next_index].setFocus()
                    return True  # Prevent further processing
        return super().eventFilter(source, event)

    def checkInputs(self):
        inputs = []
        for i, line_edit in enumerate(self.ui.get_line_edits()):
            value = line_edit.text().strip() or self.ui.defaults[i]
            if not value:  # Check value
                QMessageBox.critical(self, "Input Error", "All fields must be filled out. Please enter valid values.")
                return
            inputs.append(value)

        self.processNode(inputs)

    def processNode(self, inputs):
        self.settings.setValue("Qubit_name", inputs[0])
        self.settings.setValue("Qubit_freq", inputs[1])
        self.settings.setValue("pin0_name", inputs[2])
        self.settings.setValue("pin1_name", inputs[3])
        self.settings.setValue("read_line_name", inputs[4])
        self.settings.setValue("tml_name", inputs[5])

        print(f"Qubit Name: {inputs[0]}")
        print(f"Qubit Frequency: {inputs[1]}")
        print(f"Pin 0 Name: {inputs[2]}")
        print(f"Pin 1 Name: {inputs[3]}")
        print(f"Read Line Name: {inputs[4]}")
        print(f"Transmission Line Name: {inputs[5]}")

        # Execute design-related operations
        self.design.simulate(design_parameters=inputs)  # Assuming it has a simulate method
        self.designUpdated.emit(self.design)  # Emit design updated signal
        self.accept()  # Close the dialog


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    design = Design()  # Instantiate design object
    dialog = Dialog_s21(design=design)  # Create dialog

    dialog.designUpdated.connect(
        lambda updated_design: print("Design Updated Back to Main Window!"))  # Connect signal
    dialog.exec_()  # Show dialog

    sys.exit(app.exec_())