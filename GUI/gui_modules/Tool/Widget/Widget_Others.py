import sys
from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QEvent
from PyQt5.QtGui import QFont
from addict import Dict
from api.design import Design

class Dialog_Others(QDialog):
    designUpdated = pyqtSignal(object)

    def __init__(self, design, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Others")
        self.setFont(QFont("Microsoft YaHei", 10))
        self.resize(400, 200)
        self.design = design
        # Updated default value configuration
        self.default_values = {
            "name": "In0",  # Default Line Name
            "type": "IndiumBump",  # Default component type
            "chip": "chip0"  # Default chip name
        }
        self.lineEdits = {}
        self.input_types = {}

        self.mainLayout = QVBoxLayout(self)
        self.loadInputs()

        self.buttonLayout = QHBoxLayout()
        self.okButton = QPushButton("OK")
        self.cancelButton = QPushButton("Cancel")

        self.okButton.setFixedSize(80, 30)
        self.cancelButton.setFixedSize(80, 30)

        self.buttonLayout.addWidget(self.okButton)
        self.buttonLayout.addWidget(self.cancelButton)
        self.buttonLayout.setAlignment(Qt.AlignRight)
        self.mainLayout.addLayout(self.buttonLayout)

        self.okButton.clicked.connect(self.submitValues)
        self.cancelButton.clicked.connect(self.reject)

    def loadInputs(self):
        labels = {
            "name": "Name",
            "type": "Type",
            "chip": "Chip Name"
        }

        for key, value in self.default_values.items():
            layout = QHBoxLayout()
            label = QLabel(f"{labels[key]}:")
            layout.addWidget(label)

            line_edit = QLineEdit()
            line_edit.setPlaceholderText(f"{value}")  # Set floating prompt
            layout.addWidget(line_edit)

            self.lineEdits[key] = line_edit
            self.input_types[key] = type(value)
            self.mainLayout.addLayout(layout)

            # Install event filters to handle Tab Key events
            line_edit.installEventFilter(self)

    def eventFilter(self, source, event):
        """handle Tab Key events"""
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Tab:
            for key, line_edit in self.lineEdits.items():
                if line_edit.hasFocus():
                    # If the input box is empty，Fill in default values
                    if line_edit.text().strip() == "":
                        line_edit.setText(line_edit.placeholderText())
                    # Jump to the next input box
                    next_index = list(self.lineEdits.keys()).index(key) + 1
                    if next_index < len(self.lineEdits):
                        next_line_edit = self.lineEdits[list(self.lineEdits.keys())[next_index]]
                        next_line_edit.setFocus()
                    return True
        return super().eventFilter(source, event)

    def submitValues(self):
        options = Dict()  # useaddictCreate a dictionary that supports attribute access
        valid_input = True

        for key, line_edit in self.lineEdits.items():
            value_str = line_edit.text().strip()
            expected_type = self.input_types[key]

            if not value_str:
                converted_value = self.default_values[key]
            else:
                try:
                    converted_value = expected_type(value_str)
                except ValueError as e:
                    QMessageBox.warning(self, "Invalid Input", f"Invalid input for {key}: {e}")
                    valid_input = False
                    break

            options[key] = converted_value  # Automatically support attribute access

        if valid_input:
            print("User input values:", options)
            self.design.gds.others.add(options)  # Ensure hereaddThe method exists
            self.designUpdated.emit(self.design)
            self.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = Dialog_Others(design=Design())
    dialog.exec_()
    sys.exit(app.exec_())