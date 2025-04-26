from PySide6.QtCore import (QCoreApplication, QMetaObject, QRect, Signal, QSettings, Qt)
from PySide6.QtWidgets import (QDialog, QDialogButtonBox, QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QGroupBox,
                               QApplication)
from api.design import Design

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName("Dialog")
        Dialog.resize(500, 400)  # Increase the height of the dialog box

        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.setGeometry(QRect(50, 340, 400, 32))  # Adjust the position of the button box
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)

        self.groupBox = QGroupBox("Simulation Parameters", Dialog)  # Use QGroupBox as a parameter box
        self.groupBox.setObjectName("groupBox")
        self.groupBox.setGeometry(QRect(20, 70, 460, 260))  # Adjust the position and size of the parameter box
        self.groupBox.setStyleSheet("QGroupBox { border: 1px solid black; border-radius: 5px; padding: 10px; }")  # Set border style

        self.verticalLayout = QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setSpacing(15)  # Increase the spacing of vertical layout
        self.verticalLayout.setContentsMargins(10, 10, 10, 10)  # Set content margins

        # Add labels and input boxes for patterns
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout.addWidget(self.label_3)

        self.lineEdit = QLineEdit(self.groupBox)
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit.setMinimumHeight(30)  # Set the minimum height of the input box
        self.horizontalLayout.addWidget(self.lineEdit)
        self.verticalLayout.addLayout(self.horizontalLayout)

        # Add pin0 Label and input box for the name
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_5 = QLabel(self.groupBox)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_3.addWidget(self.label_5)

        self.lineEdit_3 = QLineEdit(self.groupBox)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.lineEdit_3.setMinimumHeight(30)  # Set the minimum height of the input box
        self.horizontalLayout_3.addWidget(self.lineEdit_3)
        self.verticalLayout.addLayout(self.horizontalLayout_3)

        # Add pin1 Label and input box for the name
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_7 = QLabel(self.groupBox)
        self.label_7.setObjectName("label_7")
        self.horizontalLayout_5.addWidget(self.label_7)

        self.lineEdit_5 = QLineEdit(self.groupBox)
        self.lineEdit_5.setObjectName("lineEdit_5")
        self.lineEdit_5.setMinimumHeight(30)  # Set the minimum height of the input box
        self.horizontalLayout_5.addWidget(self.lineEdit_5)
        self.verticalLayout.addLayout(self.horizontalLayout_5)

        # Add labels and input boxes for readout line names
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_4 = QLabel(self.groupBox)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_2.addWidget(self.label_4)

        self.lineEdit_2 = QLineEdit(self.groupBox)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.lineEdit_2.setMinimumHeight(30)  # Set the minimum height of the input box
        self.horizontalLayout_2.addWidget(self.lineEdit_2)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        # Add labels and input boxes for transmission line names
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_8 = QLabel(self.groupBox)
        self.label_8.setObjectName("label_8")
        self.horizontalLayout_6.addWidget(self.label_8)

        self.lineEdit_6 = QLineEdit(self.groupBox)
        self.lineEdit_6.setObjectName("lineEdit_6")
        self.lineEdit_6.setMinimumHeight(30)  # Set the minimum height of the input box
        self.horizontalLayout_6.addWidget(self.lineEdit_6)
        self.verticalLayout.addLayout(self.horizontalLayout_6)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", "ReadoutSim", None))
        self.label_3.setText(QCoreApplication.translate("Dialog", "Mode:", None))
        self.label_5.setText(QCoreApplication.translate("Dialog", "pin0 Name:", None))
        self.label_7.setText(QCoreApplication.translate("Dialog", "pin1 Name:", None))
        self.label_4.setText(QCoreApplication.translate("Dialog", "Readout Line Name:", None))
        self.label_8.setText(QCoreApplication.translate("Dialog", "Transmission Line Name:", None))


class Dialog_s21(QDialog):
    designUpdated = Signal(object)

    def __init__(self, design):
        super(Dialog_s21, self).__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # Setting Styles
        self.setStyleSheet("""
            QWidget {  
                background-color: #f0f0f0;  
                border-radius: 5px;  
                font-family: 'Microsoft YaHei';  
                font-size: 14px;  
                color: #333333;  
            }  
            QLineEdit {  
                background: white;  /* White background */  
                border: none;  /* no border */  
                border-radius: 4px;  
                padding: 6px 6px;  
            }  
            QPushButton {  
                background-color: #4CAF50;  
                color: white;  
                padding: 8px 16px;  
                border: 1px solid #45a49;   
                border-radius: 4px;  
            }  
            QPushButton:hover {  
                background-color: #45a049;  
            }  
        """)

        # Store incoming design parameters
        self.design = design

        # Use QSettings to save and load input data
        self.settings = QSettings("MyCompany", "MyApp")

        # Read the last saved input content and display it
        self.loadPreviousInputs()

        # Signal for connecting button
        self.ui.buttonBox.accepted.connect(self.process_inputs)
        self.ui.buttonBox.rejected.connect(self.reject)

    def loadPreviousInputs(self):
        """Load the last saved input content"""
        self.ui.lineEdit.setText(self.settings.value("model_param", "", type=str))
        self.ui.lineEdit_3.setText(self.settings.value("pin0_name", "", type=str))
        self.ui.lineEdit_5.setText(self.settings.value("pin1_name", "", type=str))
        self.ui.lineEdit_2.setText(self.settings.value("read_line_name", "", type=str))
        self.ui.lineEdit_6.setText(self.settings.value("tml_name", "", type=str))

    def process_inputs(self):
        """Save the text of the input box to QSettings, and send out designUpdated signal"""
        self.settings.setValue("model_param", self.ui.lineEdit.text())
        self.settings.setValue("pin0_name", self.ui.lineEdit_3.text())
        self.settings.setValue("pin1_name", self.ui.lineEdit_5.text())
        self.settings.setValue("read_line_name", self.ui.lineEdit_2.text())
        self.settings.setValue("tml_name", self.ui.lineEdit_6.text())

        # Example parameter processing
        model_param = self.settings.value("model_param", "", type=str)
        pin0_name = self.settings.value("pin0_name", "", type=str)
        pin1_name = self.settings.value("pin1_name", "", type=str)
        read_line_name = self.settings.value("read_line_name", "", type=str)
        tml_name = self.settings.value("tml_name", "", type=str)

        print(f"Model Parameter: {model_param}")
        print(f"pin0 Name: {pin0_name}")
        print(f"pin1 Name: {pin1_name}")
        print(f"Readout Line Name: {read_line_name}")
        print(f"Transmission Line Name: {tml_name}")

        self.design.simulation(sim_module="s21", mode=model_param, pin0_name=pin0_name, pin1_name=pin1_name, rdl_name=read_line_name, tml_name=tml_name)
        # Send design update signal
        self.designUpdated.emit(self.design)
        self.accept()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    design = Design()  # Assuming here design is a dictionary or corresponding object
    dialog = Dialog_s21(design)  # Create Dialog_s21 instance and input design parameters

    def updateMainDesign(updated_design):
        print("Main design has been updated")

    dialog.designUpdated.connect(updateMainDesign)

    if dialog.exec() == QDialog.Accepted:
        print("Dialog accepted, inputs have been processed")

    sys.exit(app.exec())