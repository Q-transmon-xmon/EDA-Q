import sys

from PySide6 import QtCore
from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from addict import Dict
from api.design import Design

class Dialog_Others(QDialog):
    # Define a signal for design updates
    designUpdated = QtCore.Signal(object)
    def __init__(self,design, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Others")
        self.setFont(QFont("Microsoft YaHei", 10.5))
        self.resize(400, 200)
        self.design = design
        # Default value
        self.default_values = Dict(
            name="",
            type="",
            chip="chip0"
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

        # Connection button event
        self.okButton.clicked.connect(self.submitValues)
        self.cancelButton.clicked.connect(self.reject)

    def loadInputs(self):
        """Dynamically generate input boxes"""
        labels = {
            "name": "名称",
            "type": "类型",
            "chip": "芯片名称"
        }

        for key, value in self.default_values.items():
            # Create horizontal layout
            layout = QHBoxLayout()

            # create label
            label = QLabel(f"{labels[key]}：")
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
        options = Dict()
        valid_input = True

        for key, line_edit in self.lineEdits.items():
            value_str = line_edit.text()
            expected_type = self.input_types[key]

            try:
                # Convert input values based on type
                converted_value = expected_type(value_str)
                options[key] = converted_value  # Save to the updated dictionary
            except ValueError as e:
                QMessageBox.warning(self, "无效输入", f"{key} 的输入无效: {e}")
                valid_input = False
                break

        if valid_input:
            # Print results
            print("用户输入的值：", options)
            self.design.gds.others.add(options)
            self.designUpdated.emit(self.design)  # Send design update signal
            # QMessageBox.information(self, "Submitted successfully", f"The input value has been submitted：\n{options}")
            self.accept()  # close window


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Create and display a dialog box
    dialog = Dialog_Others(design=Design())
    dialog.exec()

    sys.exit(app.exec())