import sys
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import QCoreApplication, QMetaObject, QSettings
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QDialog, QDialogButtonBox, QLabel, QLineEdit,
                               QRadioButton, QVBoxLayout, QWidget)

from api.design import Design

class Ui_Dialog_RAlgorithm(object):
    def setupUi(self, Dialog_RAlgorithm):
        Dialog_RAlgorithm.setObjectName("Dialog_RAlgorithm")
        Dialog_RAlgorithm.resize(419, 332)
        # Set the font of the entire interface to Microsoft Yahei
        Dialog_RAlgorithm.setFont(QFont("Microsoft YaHei", 10.5))
        self.settings = QSettings("MyCompany", "MyApp")  # initialization QSettings

        self.buttonBox = QDialogButtonBox(Dialog_RAlgorithm)
        self.buttonBox.setGeometry(30, 280, 341, 32)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)

        self.label = QLabel(Dialog_RAlgorithm)
        self.label.setGeometry(10, 60, 51, 25)
        self.label.setText("算法：")  # Set label text

        # create"algorithm"Label and set text
        self.label_algorithm = QLabel(Dialog_RAlgorithm)
        self.label_algorithm.setGeometry(10, 200, 181, 25)
        self.label_algorithm.setText("芯片层：")  # Set the label text to"algorithm"

        self.lineEdit = QLineEdit(Dialog_RAlgorithm)
        self.lineEdit.setGeometry(80, 200, 181, 28)

        self.widget = QWidget(Dialog_RAlgorithm)
        self.widget.setGeometry(78, 53, 301, 121)
        self.widget.setStyleSheet("background-color: rgb(213, 213, 213);")
        self.verticalLayout = QVBoxLayout(self.widget)

        self.radioButtons = []
        self.setStyleSheet("QRadioButton { font-family: 'Microsoft YaHei'; font-size: 14px; }")  # Set the font style for radio buttons
        self.addRadioButton("Control_off_chip_routing")  # Radio button text
        self.addRadioButton("Flipchip_routing_IBM")  # Radio button text
        self.addRadioButton("Flipchip_routing")  # Radio button text

        self.retranslateUi(Dialog_RAlgorithm)

        QMetaObject.connectSlotsByName(Dialog_RAlgorithm)

        self.loadInputs()  # Load previously saved data

    def retranslateUi(self, Dialog_RAlgorithm):
        Dialog_RAlgorithm.setWindowTitle(QCoreApplication.translate("Dialog_RAlgorithm", "选择布线算法", None))

    def addRadioButton(self, text):
        """Add radio buttons to the layout"""
        radio_btn = QRadioButton(text, self.widget)
        self.verticalLayout.addWidget(radio_btn)
        self.radioButtons.append(radio_btn)


class Dialog_RAlgorithm(QDialog, Ui_Dialog_RAlgorithm):

    designUpdated = QtCore.Signal(object)
    def __init__(self, design):
        super(Dialog_RAlgorithm, self).__init__()
        self.design = design
        self.setupUi(self)
        self.settings = QSettings("MyCompany", "MyApp")
        self.loadInputs()  # Load input data

        # Method of connecting and saving input
        self.buttonBox.accepted.connect(self.Process_RAlgorithm)
        self.buttonBox.rejected.connect(self.reject)

        # Add new variables
        self.selected_algorithm = None
        self.chip_name = None

    def loadInputs(self):
        """Loading and saving input box data display"""
        self.lineEdit.setText(self.settings.value("parameter_value", "", type=str))

        # Loading the status of radio buttons
        for radio_btn in self.radioButtons:
            radio_btn.setChecked(self.settings.value(radio_btn.text(), False, type=bool))

    def Process_RAlgorithm(self):
        """Save the text of the input box to QSettings"""
        self.settings.setValue("parameter_value", self.lineEdit.text())

        # Save the status of the radio button
        for radio_btn in self.radioButtons:
            self.settings.setValue(radio_btn.text(), radio_btn.isChecked())
            if radio_btn.isChecked():
                self.selected_algorithm = radio_btn.text()  # Save the selected algorithm name

        self.chip_name = self.lineEdit.text()  # Save the input chip name

        print(f"输入的参数: {self.chip_name}")
        print("选中的单选按钮：", self.selected_algorithm)

        self.design.routing(method=self.selected_algorithm, chip_name=self.chip_name)
        self.designUpdated.emit(self.design)  # Send design update signal
        self.accept()  # close dialog boxes

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    design = Design()
    dialog = Dialog_RAlgorithm(design=design)
    # Update the signal of the main design
    def updateMainDesign(updated_design):
        design=updated_design
        print("主窗口设计已更新")
    dialog.designUpdated.connect(updateMainDesign)

    if dialog.exec() == QDialog.Accepted:
        # clickOKAfter pressing the button, the parameters will be automatically processed and exit
        pass

    sys.exit(app.exec())