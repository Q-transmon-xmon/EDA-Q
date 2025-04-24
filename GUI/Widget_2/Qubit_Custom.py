import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QDialog, QDialogButtonBox, QLabel, QLineEdit,
                             QHBoxLayout, QVBoxLayout, QWidget, QMessageBox, QComboBox)
from PyQt5.QtCore import QSettings, pyqtSignal, Qt

import toolbox
from api.design import Design
# Add Import（Placed after other import statements）
from library.qubits import module_name_list  # Dynamically obtain a list of quantum bit types
import math


# The complete version after modification setupUi method（Only display key parts）
class Ui_Dialog_Qubit_Custom:
    def setupUi(self, dialog):
        dialog.setObjectName("Dialog_Qubit_Custom")
        dialog.resize(600, 400)
        dialog.setMinimumSize(600, 400)
        font = QFont("Arial", 10)
        dialog.setFont(font)

        # Unified management default values
        self.defaults = ["16", "2000", "chip0"]

        # Main layout
        self.mainLayout = QVBoxLayout(dialog)
        self.mainLayout.addStretch(1)

        # Title
        titleLabel = QLabel("Quantum Bit Configuration")
        titleLabel.setFont(QFont("Arial", 14, QFont.Bold))
        titleLabel.setAlignment(Qt.AlignCenter)
        self.mainLayout.addWidget(titleLabel)

        # Instructions
        instructionsLabel = QLabel("Please enter the following information:")
        instructionsLabel.setAlignment(Qt.AlignCenter)
        self.mainLayout.addWidget(instructionsLabel)

        # Input fields
        self.layoutWidget = QWidget(dialog)
        self.verticalLayout = QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setSpacing(20)
        self.verticalLayout.setContentsMargins(30, 20, 30, 20)

        self.lineEdits = []
        self.createLabeledInput("Number of qubit:", self.defaults[0])
        self.createLabeledInput("Margin (mm):", self.defaults[1])
        self.createLabeledInput("Chip name:", self.defaults[2])

        # Add camel hump conversion logic
        try:
            # Generate a list of converted class names
            class_name_list = [toolbox.convert_to_camel_case(name) for name in module_name_list]
        except Exception as e:
            print(f"Name conversion failed: {str(e)}")
            class_name_list = ["Transmon", "Xmon"]  # Use alternative list when abnormal

        # Create dropdown menu
        self.combo_box = QComboBox()
        self.createComboBox("Quantum Bit Type:", class_name_list)

        self.mainLayout.addWidget(self.layoutWidget)

        # Buttons
        self.buttonBox = QDialogButtonBox(dialog)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(self.buttonBox.button(QDialogButtonBox.Ok))
        buttonLayout.addWidget(self.buttonBox.button(QDialogButtonBox.Cancel))
        self.mainLayout.addLayout(buttonLayout)
        self.mainLayout.addStretch(1)

        # Initialize signal connection
        self.retranslateUi(dialog)
        self.buttonBox.accepted.connect(lambda: self.checkInputs(dialog))
        self.buttonBox.rejected.connect(dialog.reject)

    def createLabeledInput(self, label_text, default_value):
        layout = QHBoxLayout()
        label = QLabel(label_text)
        label.setFixedWidth(180)

        line_edit = QLineEdit()
        line_edit.setMinimumWidth(300)
        line_edit.setPlaceholderText(default_value)
        line_edit.setProperty("default", default_value)  # Store default values

        layout.addWidget(label)
        layout.addWidget(line_edit)
        self.verticalLayout.addLayout(layout)
        self.lineEdits.append(line_edit)

    def createComboBox(self, label_text, options):
        layout = QHBoxLayout()
        label = QLabel(label_text)
        label.setFixedWidth(180)
        self.combo_box.addItems(options)
        layout.addWidget(label)
        layout.addWidget(self.combo_box)
        self.verticalLayout.addLayout(layout)

    def retranslateUi(self, dialog):
        dialog.setWindowTitle("Quantum Bit Configuration")


class Dialog_Qubit_Custom(QDialog, Ui_Dialog_Qubit_Custom):
    designUpdated = pyqtSignal(object)

    def __init__(self, design):
        super().__init__()
        self.setupUi(self)
        self.design = design

        # Install event filter
        for line_edit in self.lineEdits:
            line_edit.installEventFilter(self)

        # set upTaborder
        self.setTabOrder(self.lineEdits[0], self.lineEdits[1])
        self.setTabOrder(self.lineEdits[1], self.lineEdits[2])
        self.setTabOrder(self.lineEdits[2], self.combo_box)

    def eventFilter(self, source, event):
        """handleTabKey auto fill and focus switching"""
        if event.type() == QtCore.QEvent.KeyPress and event.key() == Qt.Key_Tab:
            if source in self.lineEdits:
                # Automatically fill empty fields
                if source.text().strip() == "":
                    source.setText(source.property("default"))

                # Focus switching logic
                current_index = self.lineEdits.index(source)
                if current_index < len(self.lineEdits) - 1:
                    self.lineEdits[current_index + 1].setFocus()
                else:  # The last input box jumps to the combo box
                    self.combo_box.setFocus()
                return True  # Prevent default processing
        return super().eventFilter(source, event)

    def checkInputs(self, dialog):
        """Enhanced input validation logic"""
        try:
            # Automatically fill in empty values and convert types
            qubit_num = int(self.lineEdits[0].text() or self.defaults[0])
            margin = float(self.lineEdits[1].text() or self.defaults[1])
            chip_name = self.lineEdits[2].text() or self.defaults[2]

            # Numerical validity verification
            if qubit_num <= 0:
                raise ValueError("Number of qubits must be positive")
            if margin <= 0:
                raise ValueError("Margin must be positive")
            if not chip_name:
                raise ValueError("Chip name cannot be empty")

        except ValueError as e:
            QMessageBox.critical(dialog, "Input Error", f"Invalid input: {str(e)}")
            return

        # Successfully processed logic
        self.processInputs(qubit_num, margin, chip_name)
        dialog.accept()

    def processInputs(self, qubit_num, margin, chip_name):
        """Updated processing logic"""
        print(f"Number of qubit: {qubit_num}")
        print(f"Margin: {margin} μm")
        print(f"Chip name: {chip_name}")
        print(f"Quantum Bit Type: {self.combo_box.currentText()}")

        if self.design:
            try:
                self.design.generate_topology(
                    qubits_num=qubit_num,
                    topo_col=int(math.sqrt(qubit_num))
                )
                self.design.generate_qubits(
                    chip_name=chip_name,
                    dist=margin,
                    qubits_type=self.combo_box.currentText(),
                    topo_positions=self.design.topology.positions
                )
            except Exception as e:
                QMessageBox.critical(self, "Generation Error", str(e))
                return

        self.designUpdated.emit(self.design)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    design = Design()
    dialog = Dialog_Qubit_Custom(design=design)
    dialog.designUpdated.connect(lambda d: print("Design Updated!"))
    dialog.exec_()
    sys.exit(app.exec_())