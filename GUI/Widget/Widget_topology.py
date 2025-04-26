from PySide6 import QtCore, QtWidgets
import sys
import os

# Retrieve the directory where the current script is located
current_path = os.path.dirname(os.path.abspath(__file__))
GUI_PATH = os.path.dirname(current_path)
PROJ_PATH = os.path.dirname(GUI_PATH)

# Add path
sys.path.append(GUI_PATH)
sys.path.append(PROJ_PATH)

from PySide6.QtGui import QFont
from api.design import Design
from GUI.Widget.Topo_Node import Dialog_Node
from GUI.Widget.Topo_RandomEdge import RandomEdge_Dialog
from GUI.Widget.Topo_CustomEdge import CustomEdge_Dialog


class Ui_Dialog_Topology(object):
    def setupUi(self, Dialog_Topology):
        Dialog_Topology.setObjectName("Dialog_topology")
        Dialog_Topology.resize(500, 300)
        # Set the font of the entire interface to Microsoft YaHei
        Dialog_Topology.setFont(QFont("Microsoft YaHei", 10.5))
        # Create a main layout
        self.mainLayout = QtWidgets.QVBoxLayout(Dialog_Topology)
        self.mainLayout.setObjectName("mainLayout")

        # Create a horizontal layout for centering buttons
        self.centerLayout = QtWidgets.QHBoxLayout()
        self.centerLayout.setObjectName("centerLayout")

        # Create a vertical layout for buttons
        self.buttonLayout = QtWidgets.QVBoxLayout()
        self.buttonLayout.setObjectName("buttonLayout")
        self.buttonLayout.setSpacing(20)  # Set the interval between buttons

        # Add buttons to vertical layout
        self.pushButton = QtWidgets.QPushButton(Dialog_Topology)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setMinimumSize(150, 50)  # Set the minimum size of the button
        self.buttonLayout.addWidget(self.pushButton)

        self.pushButton_2 = QtWidgets.QPushButton(Dialog_Topology)
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.setMinimumSize(150, 50)  # Set the minimum size of the button
        self.buttonLayout.addWidget(self.pushButton_2)

        self.pushButton_3 = QtWidgets.QPushButton(Dialog_Topology)
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_3.setMinimumSize(150, 50)  # Set the minimum size of the button
        self.buttonLayout.addWidget(self.pushButton_3)

        # Add button layout to the central layout
        self.centerLayout.addStretch()
        self.centerLayout.addLayout(self.buttonLayout)
        self.centerLayout.addStretch()

        # Add the central layout to the main layout
        self.mainLayout.addLayout(self.centerLayout)

        self.retranslateUi(Dialog_Topology)
        QtCore.QMetaObject.connectSlotsByName(Dialog_Topology)

    def retranslateUi(self, Dialog_Topology):
        _translate = QtCore.QCoreApplication.translate
        Dialog_Topology.setWindowTitle(_translate("Dialog_topology", "Custom Topology"))
        self.pushButton.setText(_translate("Dialog_topology", "Generate Topology Nodes"))
        self.pushButton_2.setText(_translate("Dialog_topology", "Randomize Topology Edges"))
        self.pushButton_3.setText(_translate("Dialog_topology", "Customize Topology Edges"))


class Dialog_Topology(QtWidgets.QDialog, Ui_Dialog_Topology):
    designUpdated = QtCore.Signal(Design)  # Define custom signals

    def __init__(self, parent=None, design=None):
        super(Dialog_Topology, self).__init__(parent)
        self.design = design
        self.setupUi(self)

        self.pushButton.clicked.connect(self.handleTopologyNodeGeneration)
        self.pushButton_2.clicked.connect(self.handleRandomEdgeDesign)
        self.pushButton_3.clicked.connect(self.handleCustomEdgeDesign)

    def handleTopologyNodeGeneration(self):
        node_dialog = Dialog_Node(design=self.design)
        node_dialog.designUpdated.connect(self.updateDesign)
        node_dialog.exec()

    def handleRandomEdgeDesign(self):
        random_edge_dialog = RandomEdge_Dialog(design=self.design)
        random_edge_dialog.designUpdated.connect(self.updateDesign)
        random_edge_dialog.exec()

    def handleCustomEdgeDesign(self):
        custom_edge_dialog = CustomEdge_Dialog(design=self.design)
        custom_edge_dialog.designUpdated.connect(self.updateDesign)
        custom_edge_dialog.exec()

    def updateDesign(self, updated_design):
        self.design = updated_design
        print("Design updated in topology")
        # self.design.topology.show_image()
        self.designUpdated.emit(self.design)  # Emit a signal, transfer the updated design


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    dialog = Dialog_Topology(design=Design())
    dialog.designUpdated.connect(lambda updated_design: print("Main window received the updated design!"))
    dialog.show()
    sys.exit(app.exec())