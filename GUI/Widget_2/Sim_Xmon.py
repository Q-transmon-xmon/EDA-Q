import os
import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QDialog, QLabel, QLineEdit, QGridLayout,
                             QPushButton, QMessageBox, QVBoxLayout, QHBoxLayout, QWidget, QDialogButtonBox)
from PyQt5.QtCore import Qt, QSettings, pyqtSignal
from api.design import Design


class Ui_Dialog:
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setMinimumSize(850, 420)  # Set the minimum size of the dialog box
        Dialog.setFont(QFont("Microsoft YaHei", 10))

        # Main layout
        self.mainLayout = QVBoxLayout(Dialog)
        self.mainLayout.addStretch(1)

        # title tag
        titleLabel = QLabel("Xmon Parameter Configuration")
        titleLabel.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        titleLabel.setAlignment(Qt.AlignCenter)
        self.mainLayout.addWidget(titleLabel)

        # Guidance information label
        instructionsLabel = QLabel("Please enter the simulation parameters below:")
        instructionsLabel.setAlignment(Qt.AlignCenter)
        self.mainLayout.addWidget(instructionsLabel)

        # input section
        self.layoutWidget = QWidget(Dialog)
        self.verticalLayout = QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setSpacing(20)
        self.verticalLayout.setContentsMargins(20, 20, 20, 20)

        self.defaults = ["control_lines_upper_0", "q0", "C:/sim_proj/PlaneXmon_sim/Xmon_random_capacity_{}.txt"]  # Default value
        self.lineEdits = []

        self.createLabeledInput("Control Line Name:", self.defaults[0])
        self.createLabeledInput("Qubit Name:", self.defaults[1])
        self.createLabeledInput("Save Path:", self.defaults[2])

        self.mainLayout.addWidget(self.layoutWidget)

        # button box
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(self.buttonBox.button(QDialogButtonBox.Ok))
        buttonLayout.addWidget(self.buttonBox.button(QDialogButtonBox.Cancel))

        self.mainLayout.addLayout(buttonLayout)
        self.mainLayout.addStretch(1)

    def createLabeledInput(self, label_text, default_value):
        """Create a labeled input box"""
        layout = QHBoxLayout()  # Create a layout for each input item
        label = QLabel(label_text)
        label.setFixedWidth(180)  # Set label width
        line_edit = QLineEdit()
        line_edit.setMinimumWidth(300)

        # Set default values
        line_edit.setPlaceholderText(default_value)
        layout.addWidget(label)
        layout.addWidget(line_edit)
        self.verticalLayout.addLayout(layout)  # Add to Vertical Layout
        self.lineEdits.append(line_edit)  # Save input box

    def get_line_edits(self):
        return self.lineEdits


class Dialog_Xmon(QDialog):
    designUpdated = pyqtSignal(object)  # Define signals to notify design updates

    def __init__(self, design):
        super().__init__()
        self.design = design
        self.settings = QSettings("MyCompany", "MyApp")

        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # joining signal
        self.ui.buttonBox.accepted.connect(self.checkInputs)  # OKbutton
        self.ui.buttonBox.rejected.connect(self.reject)  # cancel button

        # Set event filters for input boxes
        for line_edit in self.ui.get_line_edits():
            line_edit.installEventFilter(self)

    def eventFilter(self, source, event):
        """handleTabKey events to set default values"""
        if event.type() == QtCore.QEvent.KeyPress and event.key() == Qt.Key_Tab:
            for line_edit in self.ui.get_line_edits():
                if line_edit.hasFocus():
                    # If the input box is empty，Set as default value
                    if line_edit.text().strip() == "":
                        line_edit.setText(line_edit.placeholderText())
                        # Go to the next input box
                    next_index = self.ui.get_line_edits().index(line_edit) + 1
                    if next_index < len(self.ui.get_line_edits()):
                        self.ui.get_line_edits()[next_index].setFocus()
                    return True  # Prevent further processing
        return super().eventFilter(source, event)

    def checkInputs(self):
        inputs = []
        for i, line_edit in enumerate(self.ui.get_line_edits()):
            # If it is empty，Use default values
            value = line_edit.text().strip() or self.ui.defaults[i]
            # Check value
            if not value:
                QMessageBox.critical(self, "Input Error", "All fields must be filled out. Please enter valid values.")
                return

                # Attempt to convert to a string
            inputs.append(value)

            # Processing node inputs
        self.processNode(inputs)

    def processNode(self, inputs):
        self.settings.setValue("control_line_name", inputs[0])
        self.settings.setValue("Qubit_name", inputs[1])
        self.settings.setValue("save_path", inputs[2])

        print(f"Control Line Name: {inputs[0]}")
        print(f"Qubit Name: {inputs[1]}")
        print(f"Save Path: {inputs[2]}")

        # Generate topology and send update signals
        self.design.simulation(sim_module="PlaneXmonSim", qubit_name=inputs[1], gds_ops=True)
        # self.design.generate_topology(control_line=inputs[0], bit_name=inputs[1], save_path=inputs[2])
        self.designUpdated.emit(self.design)  # Send design update signal
        self.accept()  # close dialog boxes


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    design = Design()  # Instantiate design object
    dialog = Dialog_Xmon(design=design)  # create a dialog box

    dialog.designUpdated.connect(
        lambda updated_design: print("Design Updated Back to Main Window!"))  # joining signal
    dialog.exec_()  # display a dialog box

    sys.exit(app.exec_())