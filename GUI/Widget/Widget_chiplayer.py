# -*- coding: utf-8 -*-
import sys
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import QCoreApplication, QSettings
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QDialog, QDialogButtonBox, QHBoxLayout,
                               QLabel, QLineEdit, QRadioButton,
                               QVBoxLayout, QWidget)
from api.design import Design

class Ui_Dialog_ChipLayer:
    def setupUi(self, Dialog_ChipLayer):
        if not Dialog_ChipLayer.objectName():
            Dialog_ChipLayer.setObjectName("Dialog_ChipLayer")
        Dialog_ChipLayer.resize(450, 350)
        # Set the font of the entire interface to Microsoft YaHei
        Dialog_ChipLayer.setFont(QFont("Microsoft YaHei", 10.5))

        # Create button box
        self.buttonBox = QDialogButtonBox(Dialog_ChipLayer)
        self.buttonBox.setGeometry(30, 300, 341, 32)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.buttonBox.button(QDialogButtonBox.Ok).setText("Add")  # Change "Ok" button to "Add"

        # Create Delete button
        self.deleteButton = QtWidgets.QPushButton("Delete", Dialog_ChipLayer)
        self.deleteButton.setGeometry(380, 300, 60, 32)  # Set position and size of the Delete button

        # Create main layout
        self.layoutWidget = QWidget(Dialog_ChipLayer)
        self.layoutWidget.setGeometry(40, 20, 331, 251)
        self.verticalLayout = QVBoxLayout(self.layoutWidget)

        # Create a chip layer name input box
        layout_h = QHBoxLayout()
        self.chip_name_label = QLabel("Chip Layer Name:")
        self.chip_name_input = QLineEdit()
        layout_h.addWidget(self.chip_name_label)
        layout_h.addWidget(self.chip_name_input)
        self.verticalLayout.addLayout(layout_h)

        # Radio Button
        layout_h = QHBoxLayout()
        label = QLabel("Chip Layer Parameters:")
        self.radioButton_define = QRadioButton("Custom")
        self.radioButton_adapt = QRadioButton("Adaptive Distance Parameters")
        layout_h.addWidget(label)
        layout_h.addWidget(self.radioButton_define)
        layout_h.addWidget(self.radioButton_adapt)
        self.verticalLayout.addLayout(layout_h)

        # Create parameter input boxes
        layout_h = QHBoxLayout()
        self.left_param_label = QLabel("Top Left Parameter:")
        self.left_param_input = QLineEdit()
        layout_h.addWidget(self.left_param_label)
        layout_h.addWidget(self.left_param_input)
        self.verticalLayout.addLayout(layout_h)

        layout_h = QHBoxLayout()
        self.right_param_label = QLabel("Top Right Parameter:")
        self.right_param_input = QLineEdit()
        layout_h.addWidget(self.right_param_label)
        layout_h.addWidget(self.right_param_input)
        self.verticalLayout.addLayout(layout_h)

        layout_h = QHBoxLayout()
        self.distance_label = QLabel("Distance:")
        self.distance_input = QLineEdit()
        layout_h.addWidget(self.distance_label)
        layout_h.addWidget(self.distance_input)
        self.verticalLayout.addLayout(layout_h)

        # Hide top left, top right, and distance input boxes and labels
        self.left_param_label.setVisible(False)
        self.left_param_input.setVisible(False)
        self.right_param_label.setVisible(False)
        self.right_param_input.setVisible(False)
        self.distance_label.setVisible(False)
        self.distance_input.setVisible(False)

        self.retranslateUi(Dialog_ChipLayer)

        # Connect signal and slot
        self.buttonBox.accepted.connect(Dialog_ChipLayer.accept)
        self.buttonBox.rejected.connect(Dialog_ChipLayer.reject)

        # Connect custom radio button status change signal
        self.radioButton_define.toggled.connect(self.toggleInputs)
        self.radioButton_adapt.toggled.connect(self.toggleInputs)

    def toggleInputs(self):
        if self.radioButton_define.isChecked():
            self.left_param_label.setVisible(True)
            self.left_param_input.setVisible(True)
            self.right_param_label.setVisible(True)
            self.right_param_input.setVisible(True)
            self.distance_label.setVisible(False)
            self.distance_input.setVisible(False)
        elif self.radioButton_adapt.isChecked():
            self.left_param_label.setVisible(False)
            self.left_param_input.setVisible(False)
            self.right_param_label.setVisible(False)
            self.right_param_input.setVisible(False)
            self.distance_label.setVisible(True)
            self.distance_input.setVisible(True)
        else:
            self.left_param_label.setVisible(False)
            self.left_param_input.setVisible(False)
            self.right_param_label.setVisible(False)
            self.right_param_input.setVisible(False)
            self.distance_label.setVisible(False)
            self.distance_input.setVisible(False)

    def retranslateUi(self, Dialog_ChipLayer):
        Dialog_ChipLayer.setWindowTitle(QCoreApplication.translate("Dialog_ChipLayer", "Generate Chip Layer"))


class Dialog_ChipLayer(QDialog, Ui_Dialog_ChipLayer):
    # Define a signal for design updates
    designUpdated = QtCore.Signal(object)

    def __init__(self, design):
        super(Dialog_ChipLayer, self).__init__()
        self.setupUi(self)
        self.design = design
        self.settings = QSettings("MyCompany", "MyApp")
        self.loadInputs()

        # Connect button signals
        self.buttonBox.accepted.connect(self.Process_ChipLayer)
        self.deleteButton.clicked.connect(self.deleteChipLayer)  # Connect Delete button

    def loadInputs(self):
        """Load default parameter values and display them on the interface"""
        # Set default values
        default_values = {
            "layer_name": "DefaultLayer",  # Default Chip Layer Name
            "param_top_left": "10",  # Default top left parameter
            "param_top_right": "20",  # Default top right parameter
            "distance": "2000",  # Default distance
            "is_custom": True  # Default selection of custom mode
        }

        # Load parameter values from QSettings, or use default values if not previously saved
        self.chip_name_input.setText(self.settings.value("layer_name", default_values["layer_name"], type=str))
        self.left_param_input.setText(self.settings.value("param_top_left", default_values["param_top_left"], type=str))
        self.right_param_input.setText(self.settings.value("param_top_right", default_values["param_top_right"], type=str))
        self.distance_input.setText(self.settings.value("distance", default_values["distance"], type=str))

        # Set radio button status based on saved or default values
        is_custom = self.settings.value("is_custom", default_values["is_custom"], type=bool)
        if is_custom:
            self.radioButton_define.setChecked(True)
        else:
            self.radioButton_adapt.setChecked(True)

        # Show or hide related input boxes based on the status of the radio button
        self.toggleInputs()

    def processCustomSettings(self):
        # Custom mode
        param_top_left = self.left_param_input.text()
        param_top_right = self.right_param_input.text()
        layer_name = self.chip_name_input.text()
        print(f"Custom Mode: Top Left Parameter: {param_top_left}, Top Right Parameter: {param_top_right}, Chip Layer Name: {layer_name}")
        # self.design.  # Need to add actual design operations

    def processAdaptiveSettings(self):
        # Adaptive mode
        layer_name = self.chip_name_input.text()
        distance = self.distance_input.text()
        distance = int(distance)
        print(f"Adaptive Mode: Chip Layer Name: {layer_name}, Distance: {distance}")
        self.design.generate_chip(chip_name=layer_name, dist=distance, qubits=True)

    def Process_ChipLayer(self):
        self.settings.setValue("layer_name", self.chip_name_input.text())
        self.settings.setValue("param_top_left", self.left_param_input.text())
        self.settings.setValue("param_top_right", self.right_param_input.text())
        self.settings.setValue("distance", self.distance_input.text())
        self.settings.setValue("is_custom", self.radioButton_define.isChecked())

        if self.radioButton_define.isChecked():
            self.processCustomSettings()
        elif self.radioButton_adapt.isChecked():
            self.processAdaptiveSettings()

        self.designUpdated.emit(self.design)  # Send design update signal
        self.accept()

    def deleteChipLayer(self):
        """Logic for handling the delete button"""
        layer_name = self.chip_name_input.text()
        print(f"Deleting {layer_name}")  # Output the name of the deleted chip layer
        self.design.gds.chips.clear()
        self.designUpdated.emit(self.design)  # Send design update signal
        self.reject()  # Close dialog box


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    design = Design()
    dialog = Dialog_ChipLayer(design=design)
    dialog.designUpdated.connect(lambda updated_design: print("Chip layer design has been updated"))
    dialog.exec()
    sys.exit(app.exec())