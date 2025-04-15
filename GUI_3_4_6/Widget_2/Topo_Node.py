import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QDialog, QDialogButtonBox, QLabel, QLineEdit,
                             QHBoxLayout, QVBoxLayout, QWidget, QMessageBox)
from PyQt5.QtCore import QSettings, pyqtSignal, Qt
from api.design import Design


class Ui_Dialog:
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setMinimumSize(600, 400)  # Set a minimum size for the dialog
        Dialog.setFont(QFont("Arial", 10))

        # Main layout
        self.mainLayout = QVBoxLayout(Dialog)
        self.mainLayout.addStretch(1)

        # Title label
        titleLabel = QLabel("Topology Node Generation")
        titleLabel.setFont(QFont("Arial", 14, QFont.Bold))
        titleLabel.setAlignment(Qt.AlignCenter)
        self.mainLayout.addWidget(titleLabel)

        # Instructions label
        instructionsLabel = QLabel("Please enter the following information:")
        instructionsLabel.setAlignment(Qt.AlignCenter)
        self.mainLayout.addWidget(instructionsLabel)

        # Input section
        self.layoutWidget = QWidget(Dialog)
        self.verticalLayout = QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setSpacing(20)
        self.verticalLayout.setContentsMargins(30, 20, 30, 20)

        self.defaults = ["8", "8"]  # Default values for rows and columns
        self.lineEdits = []

        self.createLabeledInput("Number of Rows:", self.defaults[0])
        self.createLabeledInput("Number of Columns:", self.defaults[1])

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
        layout = QHBoxLayout()  # Layout for each input item
        label = QLabel(label_text)
        label.setFixedWidth(180)  # Set label width
        line_edit = QLineEdit()
        line_edit.setMinimumWidth(300)

        # Set placeholder to default value
        line_edit.setPlaceholderText(default_value)
        layout.addWidget(label)
        layout.addWidget(line_edit)
        self.verticalLayout.addLayout(layout)  # Add to vertical layout
        self.lineEdits.append(line_edit)  # Save line edit

    def get_line_edits(self):
        return self.lineEdits


class Dialog_Node(QDialog):
    designUpdated = pyqtSignal(object)  # Define a signal to notify when the design is updated

    def __init__(self, design):
        super().__init__()
        self.design = design
        self.settings = QSettings("MyCompany", "MyApp")

        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # Connect signals
        self.ui.buttonBox.accepted.connect(self.checkInputs)  # OK button
        self.ui.buttonBox.rejected.connect(self.reject)  # Cancel button

        # Set up event filter for line edits
        for line_edit in self.ui.get_line_edits():
            line_edit.installEventFilter(self)

    def eventFilter(self, source, event):
        """Handle the Tab key event to set default values."""
        if event.type() == QtCore.QEvent.KeyPress and event.key() == Qt.Key_Tab:
            for line_edit in self.ui.get_line_edits():
                if line_edit.hasFocus():
                    # If the line edit is empty, set it to the placeholder value
                    if line_edit.text().strip() == "":
                        line_edit.setText(line_edit.placeholderText())
                        # Move to the next line edit
                    next_index = self.ui.get_line_edits().index(line_edit) + 1
                    if next_index < len(self.ui.get_line_edits()):
                        self.ui.get_line_edits()[next_index].setFocus()
                    return True  # Prevent further processing
        return super().eventFilter(source, event)

    def checkInputs(self):
        inputs = []
        for i, line_edit in enumerate(self.ui.get_line_edits()):
            # If empty, use default value
            value = line_edit.text().strip() or self.ui.defaults[i]

            try:
                # Try converting to integer
                int_value = int(value)
                inputs.append(int_value)
            except ValueError:
                QMessageBox.critical(self, "Input Error", "Please enter valid integer values!")
                return

        # Check for valid parameters
        if inputs[0] <= 0 or inputs[1] <= 0:
            QMessageBox.critical(self, "Input Error", "All values must be greater than 0!")
            return

        # Calculate the number of quantum bits based on rows and columns
        num_qubits = inputs[0] * inputs[1]

        # Process node with inputs
        self.processNode(num_qubits, inputs)

    def processNode(self, num_qubits, inputs):
        self.settings.setValue("quantum_bits", num_qubits)
        self.settings.setValue("rows", inputs[0])
        self.settings.setValue("columns", inputs[1])

        print(f"Number of Quantum Bits: {num_qubits}")
        print(f"Number of Rows: {inputs[0]}")
        print(f"Number of Columns: {inputs[1]}")

        # Generate topology and emit update signal
        self.design.generate_topology(topo_col=inputs[1], topo_row=inputs[0])
        self.designUpdated.emit(self.design)  # Emit design update signal
        self.accept()  # Close the dialog


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    design = Design()  # Instantiate design object
    dialog = Dialog_Node(design=design)  # Create dialog

    dialog.designUpdated.connect(
        lambda updated_design: print("Design Updated Back to Main Window!"))  # Connect signal
    dialog.exec_()  # Show dialog

    sys.exit(app.exec_())