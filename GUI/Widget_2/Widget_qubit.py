# -*- coding: utf-8 -*-  
import sys
import os

# Retrieve the directory where the current script is located
current_path = os.path.dirname(os.path.abspath(__file__))
GUI_PATH = os.path.dirname(current_path)
PROJ_PATH = os.path.dirname(GUI_PATH)

# Add path
sys.path.append(GUI_PATH)
sys.path.append(PROJ_PATH)

from PySide6 import QtCore, QtWidgets, QtGui
import sys
from api.design import Design  # import Design class
from GUI.Widget.Qubit_Custom import Dialog_Qubit_Custom
from GUI.Widget.Qubit_type import SelectionDialog
class Ui_Dialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Ui_Dialog, self).__init__(parent)
        self.setupUi()

    def setupUi(self):
        self.setObjectName("Dialog")
        self.resize(336, 147)

        # Create vertical layout
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setAlignment(QtCore.Qt.AlignCenter)  # Set layout centered
        self.layout.setSpacing(20)  # Set the layout spacing to20

        self.label = QtWidgets.QLabel(self)
        self.label.setObjectName("label")
        self.label.setFont(QtGui.QFont("微软雅黑", 12))  # Set the font to Microsoft Yahei，The size is12
        self.layout.addWidget(self.label, alignment=QtCore.Qt.AlignCenter)  # Add tags and center them

        self.widget = QtWidgets.QWidget(self)
        self.widget.setObjectName("widget")

        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.pushButton = QtWidgets.QPushButton(self.widget)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)

        self.label_2 = QtWidgets.QLabel(self.widget)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)

        self.pushButton_2 = QtWidgets.QPushButton(self.widget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout.addWidget(self.pushButton_2)

        self.layout.addWidget(self.widget, alignment=QtCore.Qt.AlignCenter)  # Add button container and center it

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Dialog", "生成量子比特"))
        self.label.setText(_translate("Dialog", "Topology"))
        self.pushButton.setText(_translate("Dialog", "True"))
        self.label_2.setText(_translate("Dialog", "or"))
        self.pushButton_2.setText(_translate("Dialog", "False"))


class Dialog_Qubit(Ui_Dialog):
    # Define a signal for design updates
    designUpdated = QtCore.Signal(object)

    def __init__(self, design, parent=None):
        super(Dialog_Qubit, self).__init__(parent)
        self.design = design  # Store the passed design parameter

        # Connect button click signal
        self.pushButton.clicked.connect(self.handleTrue)
        self.pushButton_2.clicked.connect(self.handleFalse)

    def handleTrue(self):
        """handle True Button click event"""
        print("User selected: True")
        # self.design.generate_topology(topo_col=4, topo_row=4)
        # self.design.gds.show_svg(width=300)
        Qubit_type_dialog = SelectionDialog(design=self.design)
        Qubit_type_dialog.designUpdated.connect(self.updateDesign)
        Qubit_type_dialog.exec_()
        self.designUpdated.emit(self.design)  # Send design update signal
        self.accept()  # close dialog boxes

    def handleFalse(self):
        """handle False Button click event"""
        print("User selected: False")
        Qubit_Custom_dialog = Dialog_Qubit_Custom(design=self.design)
        Qubit_Custom_dialog.designUpdated.connect(self.updateDesign)
        Qubit_Custom_dialog.exec()
        self.designUpdated.emit(self.design)  # Send design update signal
        self.accept()  # close dialog boxes

    def updateDesign(self, updated_design):
        self.design = updated_design
        print("Qubit中的设计已更新")
        # self.design.topology.show_image()
        # self.designUpdated.emit(self.design)  # emit a signal，Transfer the updated design

if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)

    # Set the global font to Microsoft Yahei
    app.setFont(QtGui.QFont("微软雅黑", 10))  # Set the global font to Microsoft Yahei，The size is10

    design = Design()  # create Design example
    dialog = Dialog_Qubit(design=design)  # support design Instance passed to Dialog_Qubit

    # Connect the design update signal to the processing function
    dialog.designUpdated.connect(lambda updated_design: print("Design updated:", updated_design))

    dialog.exec()
    sys.exit(app.exec())