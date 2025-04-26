import sys
import os

# Retrieve the directory where the current script is located
current_path = os.path.dirname(os.path.abspath(__file__))
GUI_PATH = os.path.dirname(current_path)
PROJ_PATH = os.path.dirname(GUI_PATH)

# Add path
sys.path.append(GUI_PATH)
sys.path.append(PROJ_PATH)

from PySide6 import QtWidgets
from PySide6.QtCore import (QCoreApplication, QMetaObject, QRect, Qt, Signal, QSettings)
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QDialog, QDialogButtonBox, QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QWidget)
from api.design import Design
from GUI.Widget.Show_Dataframe import DataFrameDisplay


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName("Dialog")
        Dialog.resize(600, 400)
        # Set the font of the entire interface to Microsoft YaHei
        Dialog.setFont(QFont("Microsoft YaHei", 10.5))
        self.label_2 = QLabel(Dialog)
        self.label_2.setObjectName("label_2")
        self.label_2.setGeometry(QRect(20, 40, 61, 31))
        self.widget_parameter = QWidget(Dialog)
        self.widget_parameter.setObjectName("widget_parameter")
        self.widget_parameter.setGeometry(QRect(90, 50, 450, 250))
        self.widget_parameter.setStyleSheet("background-color: rgb(214, 214, 214);")
        self.verticalLayout = QVBoxLayout(self.widget_parameter)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_5 = QLabel(self.widget_parameter)
        self.label_5.setObjectName("label_5")

        self.horizontalLayout_3.addWidget(self.label_5)

        self.lineEdit_3 = QLineEdit(self.widget_parameter)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.lineEdit_3.setMinimumWidth(300)

        self.horizontalLayout_3.addWidget(self.lineEdit_3)

        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_6 = QLabel(self.widget_parameter)
        self.label_6.setObjectName("label_6")

        self.horizontalLayout_4.addWidget(self.label_6)

        self.lineEdit_4 = QLineEdit(self.widget_parameter)
        self.lineEdit_4.setObjectName("lineEdit_4")
        self.lineEdit_4.setMinimumWidth(300)

        self.horizontalLayout_4.addWidget(self.lineEdit_4)

        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_8 = QLabel(self.widget_parameter)
        self.label_8.setObjectName("label_8")

        self.horizontalLayout_6.addWidget(self.label_8)

        self.lineEdit_6 = QLineEdit(self.widget_parameter)
        self.lineEdit_6.setObjectName("lineEdit_6")
        self.lineEdit_6.setMinimumWidth(300)

        self.horizontalLayout_6.addWidget(self.lineEdit_6)

        self.verticalLayout.addLayout(self.horizontalLayout_6)

        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.setGeometry(QRect(50, 330, 500, 32))
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)

        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", "Xmon", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", "Simulation Parameters:", None))
        self.label_5.setText(QCoreApplication.translate("Dialog", "Control Line Name:", None))
        self.label_6.setText(QCoreApplication.translate("Dialog", "Qubit Name:", None))
        self.label_8.setText(QCoreApplication.translate("Dialog", "Save Path:", None))


class Dialog_Xmon(QDialog, Ui_Dialog):
    designUpdated = Signal(object)

    def __init__(self, design):
        super(Dialog_Xmon, self).__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # Store incoming data design parameter
        self.design = design

        # Use QSettings to save and load input data
        self.settings = QSettings("MyCompany", "MyApp")

        # Read the last saved input content and display it
        self.loadPreviousInputs()

        # Signal for connecting button
        self.ui.buttonBox.accepted.connect(self.process_xmon)
        self.ui.buttonBox.rejected.connect(self.reject)

    def loadPreviousInputs(self):
        """Load the last saved input content"""
        self.ui.lineEdit_3.setText(self.settings.value("control_line_name", "control_lines_upper_0", type=str))
        self.ui.lineEdit_4.setText(self.settings.value("bit_name", "q0", type=str))
        self.ui.lineEdit_6.setText(self.settings.value("save_path", "C:/sim_proj/PlaneXmon_sim/Xmon_random_capacity_{}.txt", type=str))

    def process_xmon(self):
        """Save the text of the input box to QSettings, and send out designUpdated signal"""
        self.settings.setValue("control_line_name", self.ui.lineEdit_3.text())
        self.settings.setValue("bit_name", self.ui.lineEdit_4.text())
        self.settings.setValue("save_path", self.ui.lineEdit_6.text())

        ctl_name = self.settings.value("control_line_name", "", type=str)
        bit_name = self.settings.value("bit_name", "", type=str)
        save_path = self.settings.value("save_path", "", type=str)

        print(f"Control Line Name: {ctl_name}")
        print(f"Qubit Name: {bit_name}")
        print(f"Save Path: {save_path}")

        # self.design.simulation(sim_module="PlaneXmonSim", qubit_name=bit_name, gds_ops=True)
        self.designUpdated.emit(self.design)
        show_matrix = DataFrameDisplay(file_path=save_path)
        show_matrix.exec()
        self.accept()

        # Display matrix window after closing the dialog box
        self.show_matrix_display(path=save_path)

    def show_matrix_display(self, path):
        """Display Matrix Window"""
        file_path = path

        # Check if the file exists
        if not os.path.exists(file_path):
            print(f"File {file_path} does not exist, cannot display matrix window")
            return

        print('Displaying matrix...')

        # Create and display DataFrameDisplay window
        self.matrix_dialog = DataFrameDisplay(file_path=file_path)
        self.matrix_dialog.exec()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    design = Design()  # Create Design instance
    dialog = Dialog_Xmon(design=design)  # Pass design instance to Dialog_Xmon

    # Update the signal of the main design
    def updateMainDesign(updated_design):
        print("Main design has been updated")

    dialog.designUpdated.connect(updateMainDesign)

    # If the dialog box accepts, display input content
    if dialog.exec() == QDialog.Accepted:
        dialog.design.gds.show_svg()

    # Exit from application program
    sys.exit(app.exec())