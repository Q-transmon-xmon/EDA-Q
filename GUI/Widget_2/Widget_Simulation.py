import sys
import os

# Retrieve the directory where the current script is located
current_path = os.path.dirname(os.path.abspath(__file__))
GUI_PATH = os.path.dirname(current_path)
PROJ_PATH = os.path.dirname(GUI_PATH)

# Add path
sys.path.append(GUI_PATH)
sys.path.append(PROJ_PATH)

from functools import partial
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout, QWidget, QRadioButton
from PySide6.QtCore import QSettings, Signal, Qt, QRect, QMetaObject, QCoreApplication

# Assuming these modules are custom modules in your project
from api.design import Design
from GUI.Widget.Sim_Trans import Dialog_Transmon
from GUI.Widget.Sim_Xmon import Dialog_Xmon
from GUI.Widget.Sim_Readout import Dialog_s21
from GUI.Widget.Show_Dataframe import DataFrameDisplay

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(400, 300)
        # Set the font for the entire interface
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei")
        font.setPointSize(11)
        Dialog.setFont(font)
        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(30, 240, 341, 32))
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.label = QLabel(Dialog)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(20, 50, 100, 20))  # Adjust label size
        self.label.setText("仿真类型：")
        self.widget_type = QWidget(Dialog)
        self.widget_type.setObjectName(u"widget_type")
        self.widget_type.setGeometry(QRect(100, 50, 251, 141))
        self.widget_type.setStyleSheet(u"background-color: rgb(211, 211, 211);")
        self.verticalLayout = QVBoxLayout(self.widget_type)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.radioButton_Transmon = QRadioButton(self.widget_type)
        self.radioButton_Transmon.setObjectName(u"radioButton_Transmon")
        self.radioButton_Transmon.setText("Transmon Sim")

        self.verticalLayout.addWidget(self.radioButton_Transmon)

        self.radioButton_Xmon = QRadioButton(self.widget_type)
        self.radioButton_Xmon.setObjectName(u"radioButton_Xmon")
        self.radioButton_Xmon.setText("Xmon Sim")

        self.verticalLayout.addWidget(self.radioButton_Xmon)

        self.radioButton_Readout = QRadioButton(self.widget_type)
        self.radioButton_Readout.setObjectName(u"radioButton_Readout")
        self.radioButton_Readout.setText("Readout Sim")

        self.verticalLayout.addWidget(self.radioButton_Readout)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"仿真", None))


class Dialog_Simulation(QDialog, Ui_Dialog):
    designUpdated = Signal(object)

    def __init__(self, design):
        super(Dialog_Simulation, self).__init__()
        self.setupUi(self)
        self.design = design
        self.resize(400, 300)
        self.settings = QSettings("MyCompany", "MyApp")

        # Method of connecting and saving input
        self.buttonBox.accepted.connect(self.Process_Simulation)
        self.buttonBox.rejected.connect(self.reject)

    def Process_Simulation(self):
        # Output the selected options
        if self.radioButton_Transmon.isChecked():
            print("选择了 Transmon Sim")
            # perform Transmon Simulation processing
            dialog_transmon = Dialog_Transmon(self.design)
            dialog_transmon.designUpdated.connect(self.updateDesign)
            dialog_transmon.exec()  # Blocking display

        elif self.radioButton_Xmon.isChecked():
            print("选择了 Xmon Sim")
            # perform Xmon Simulation processing
            dialog_Xmon = Dialog_Xmon(self.design)
            dialog_Xmon.designUpdated.connect(self.updateDesign)
            dialog_Xmon.exec()  # Blocking display

        elif self.radioButton_Readout.isChecked():
            print("选择了 Readout Sim")
            # perform Readout Simulation processing
            dialog_s21 = Dialog_s21(self.design)
            dialog_s21.designUpdated.connect(self.updateDesign)
            dialog_s21.exec()  # Blocking display


    def updateDesign(self, updated_design):
        self.design = updated_design
        print("simulation中的设计已更新")
        self.designUpdated.emit(self.design)  # emit a signal，Transfer the updated design



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    design = Design()
    widget = Dialog_Simulation(design=design)
    widget.show()
    sys.exit(app.exec())