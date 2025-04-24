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
        # Set the font of the entire interface to Microsoft Yahei
        Dialog_ChipLayer.setFont(QFont("Microsoft YaHei", 10.5))

        # Create button box
        self.buttonBox = QDialogButtonBox(Dialog_ChipLayer)
        self.buttonBox.setGeometry(30, 300, 341, 32)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.buttonBox.button(QDialogButtonBox.Ok).setText("Add")  # support Ok Change button to Add

        # create Delete button
        self.deleteButton = QtWidgets.QPushButton("Delete", Dialog_ChipLayer)
        self.deleteButton.setGeometry(380, 300, 60, 32)  # set up Delete Position and size of buttons

        # Create main layout
        self.layoutWidget = QWidget(Dialog_ChipLayer)
        self.layoutWidget.setGeometry(40, 20, 331, 251)
        self.verticalLayout = QVBoxLayout(self.layoutWidget)

        # Create a chip layer name input box
        layout_h = QHBoxLayout()
        self.chip_name_label = QLabel("芯片层名称：")
        self.chip_name_input = QLineEdit()
        layout_h.addWidget(self.chip_name_label)
        layout_h.addWidget(self.chip_name_input)
        self.verticalLayout.addLayout(layout_h)

        # Radio Button
        layout_h = QHBoxLayout()
        label = QLabel("芯片层参数：")
        self.radioButton_define = QRadioButton("自定义")
        self.radioButton_adapt = QRadioButton("自适应距离参数")
        layout_h.addWidget(label)
        layout_h.addWidget(self.radioButton_define)
        layout_h.addWidget(self.radioButton_adapt)
        self.verticalLayout.addLayout(layout_h)

        # Create parameter input box
        layout_h = QHBoxLayout()
        self.left_param_label = QLabel("左上角参数：")
        self.left_param_input = QLineEdit()
        layout_h.addWidget(self.left_param_label)
        layout_h.addWidget(self.left_param_input)
        self.verticalLayout.addLayout(layout_h)

        layout_h = QHBoxLayout()
        self.right_param_label = QLabel("右上角参数：")
        self.right_param_input = QLineEdit()
        layout_h.addWidget(self.right_param_label)
        layout_h.addWidget(self.right_param_input)
        self.verticalLayout.addLayout(layout_h)

        layout_h = QHBoxLayout()
        self.distance_label = QLabel("距离：")
        self.distance_input = QLineEdit()
        layout_h.addWidget(self.distance_label)
        layout_h.addWidget(self.distance_input)
        self.verticalLayout.addLayout(layout_h)

        # Hide top left corner、Top right corner and distance input box and label
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
        Dialog_ChipLayer.setWindowTitle(QCoreApplication.translate("Dialog_ChipLayer", "生成芯片层"))

class Dialog_ChipLayer(QDialog, Ui_Dialog_ChipLayer):
    # Define a signal for design updates
    designUpdated = QtCore.Signal(object)
    def __init__(self, design):
        super(Dialog_ChipLayer, self).__init__()
        self.setupUi(self)
        self.design = design
        self.settings = QSettings("MyCompany", "MyApp")
        self.loadInputs()

        # Connect button signal
        self.buttonBox.accepted.connect(self.Process_Chiplayer)
        self.deleteButton.clicked.connect(self.deleteChipLayer)  # connect Delete button

    def loadInputs(self):
        """Load default parameter values and display them on the interface"""
        # Set default values
        default_values = {
            "layer_name": "DefaultLayer",  # Default Chip Layer Name
            "param_top_left": "10",  # Default upper left corner parameter
            "param_top_right": "20",  # Default upper right corner parameter
            "distance": "2000",  # Default distance
            "is_custom": True  # Default selection of custom mode
        }

        # follow QSettings Load parameter values，If it has not been saved before，Then use default values
        self.chip_name_input.setText(self.settings.value("layer_name", default_values["layer_name"], type=str))
        self.left_param_input.setText(self.settings.value("param_top_left", default_values["param_top_left"], type=str))
        self.right_param_input.setText(
            self.settings.value("param_top_right", default_values["param_top_right"], type=str))
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
        # customize
        param_top_left = self.left_param_input.text()
        param_top_right = self.right_param_input.text()
        layer_name = self.chip_name_input.text()
        print(f"自定义模式: 左上角参数: {param_top_left}, 右上角参数: {param_top_right}, 芯片层名称: {layer_name}")
        # self.design.  #  Need to add actualdesignoperate

    def processAdaptiveSettings(self):
        # adaptive
        layer_name = self.chip_name_input.text()
        distance = self.distance_input.text()
        distance = int(distance)
        print(f"自适应模式: 芯片层名称: {layer_name}, 距离: {distance}")
        self.design.generate_chip(chip_name=layer_name, dist=distance, qubits=True)

    def Process_Chiplayer(self):
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
        print(f"删除 {layer_name}")  # Output the name of the deleted chip layer
        self.design.gds.chips.clear()
        self.designUpdated.emit(self.design)  # Send design update signal
        self.reject()  # close dialog boxes

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    design = Design()
    dialog = Dialog_ChipLayer(design=design)
    dialog.designUpdated.connect(lambda updated_design: print("chiplayer设计已更新"))
    dialog.exec()
    sys.exit(app.exec())