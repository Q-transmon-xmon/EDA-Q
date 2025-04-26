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
        Dialog.resize(400, 300)
        # Set the font of the entire interface to Microsoft YaHei
        Dialog.setFont(QFont("Microsoft YaHei", 10.5))
        self.widget_parameter = QWidget(Dialog)
        self.widget_parameter.setObjectName("widget_parameter")
        self.widget_parameter.setGeometry(QRect(90, 60, 281, 131))
        self.widget_parameter.setStyleSheet("background-color: rgb(214, 214, 214);")
        self.verticalLayout_2 = QVBoxLayout(self.widget_parameter)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_3 = QLabel(self.widget_parameter)
        self.label_3.setObjectName("label_3")

        self.horizontalLayout.addWidget(self.label_3)

        self.lineEdit = QLineEdit(self.widget_parameter)
        self.lineEdit.setObjectName("lineEdit")

        self.horizontalLayout.addWidget(self.lineEdit)

        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_4 = QLabel(self.widget_parameter)
        self.label_4.setObjectName("label_4")

        self.horizontalLayout_2.addWidget(self.label_4)

        self.lineEdit_2 = QLineEdit(self.widget_parameter)
        self.lineEdit_2.setObjectName("lineEdit_2")

        self.horizontalLayout_2.addWidget(self.lineEdit_2)

        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.label_2 = QLabel(Dialog)
        self.label_2.setObjectName("label_2")
        self.label_2.setGeometry(QRect(10, 50, 61, 31))
        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.setGeometry(QRect(20, 240, 341, 32))
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)

        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", "Transmon", None))
        self.label_3.setText(QCoreApplication.translate("Dialog", "Qubit Name:", None))
        self.label_4.setText(QCoreApplication.translate("Dialog", "Qubit Frequency:", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", "Simulation Parameters:", None))


class Dialog_Transmon(QDialog, Ui_Dialog):
    designUpdated = Signal(object)

    def __init__(self, design):
        super(Dialog_Transmon, self).__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # Store incoming data design parameter
        self.design = design

        # Use QSettings to save and load input data
        self.settings = QSettings("MyCompany", "MyApp")

        # Read the last saved input content and display it
        self.loadPreviousInputs()

        # Signal for connecting button
        self.ui.buttonBox.accepted.connect(self.process_transmon)
        self.ui.buttonBox.rejected.connect(self.reject)

        # The initialization matrix dialog box is None
        self.matrix_dialog = None

    def loadPreviousInputs(self):
        """Load the last saved input content"""
        self.ui.lineEdit.setText(self.settings.value("bit_name", "q0", type=str))
        self.ui.lineEdit_2.setText(self.settings.value("bit_freq", "5.6", type=str))

    def process_transmon(self):
        """Save the text of the input box to QSettings, and send out designUpdated signal"""
        # Save input content
        self.settings.setValue("bit_name", self.ui.lineEdit.text())
        self.settings.setValue("bit_freq", self.ui.lineEdit_2.text())

        # Retrieve input content
        bit_name = self.settings.value("bit_name", "", type=str)
        bit_freq = self.settings.value("bit_freq", "", type=float)

        # Print input content
        print(f"Qubit Name: {bit_name}")
        print(f"Qubit Frequency: {bit_freq}")

        # Call the simulation method of design
        self.design.simulation(sim_module="TransmonSim", frequency=bit_freq, qubit_name=bit_name)

        # Send design update signal
        self.designUpdated.emit(self.design)

        # Accept dialog box
        self.accept()

        # Display matrix window after closing the dialog box
        self.show_matrix_display()

    def show_matrix_display(self):
        """Display Matrix Window"""
        file_path = 'C:/sim_proj/transmon_sim/capacitance_matrix.txt'

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
    dialog = Dialog_Transmon(design=design)  # Pass design instance to Dialog_Transmon

    # Update the signal of the main design
    def updateMainDesign(updated_design):
        print("Main design has been updated")

    dialog.designUpdated.connect(updateMainDesign)

    # Display a dialog box
    if dialog.exec() == QDialog.Accepted:
        pass

    # Exit from application program
    sys.exit(app.exec())