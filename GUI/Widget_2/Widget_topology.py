from PyQt5 import QtCore, QtWidgets
import sys
import os

# Retrieve the directory where the current script is located
current_path = os.path.dirname(os.path.abspath(__file__))
GUI_PATH = os.path.dirname(current_path)
PROJ_PATH = os.path.dirname(GUI_PATH)

# Add path
sys.path.append(GUI_PATH)
sys.path.append(PROJ_PATH)


from PyQt5.QtGui import QFont
from api.design import Design
from GUI.Widget.Topo_Node import Dialog_Node
from GUI.Widget.Topo_RandomEdge import RandomEdge_Dialog
from GUI.Widget.Topo_CustomEdge import CustomEdge_Dialog


class Ui_Dialog_Topology(object):
    def setupUi(self, Dialog_Topology):
        Dialog_Topology.setObjectName("Dialog_topology")
        Dialog_Topology.resize(500, 300)
        # Set the font of the entire interface to Microsoft Yahei，Support floating point font size
        font = QFont("Microsoft YaHei")
        font.setPointSizeF(9)  # Set font size using floating-point numbers
        Dialog_Topology.setFont(font)
        # The remaining code remains unchanged
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
        Dialog_Topology.setWindowTitle(_translate("Dialog_topology", "自定义拓扑"))
        self.pushButton.setText(_translate("Dialog_topology", "拓扑节点生成"))
        self.pushButton_2.setText(_translate("Dialog_topology", "随机化拓扑边设计"))
        self.pushButton_3.setText(_translate("Dialog_topology", "拓扑边定制设计"))


class Dialog_Topology(QtWidgets.QDialog, Ui_Dialog_Topology):
    # PyQt5Definition of Signal in，change toQtCore.pyqtSignal
    designUpdated = QtCore.pyqtSignal(Design)  # Define custom signals

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
        node_dialog.exec_()  # PyQt5Used inexec_()

    def handleRandomEdgeDesign(self):
        random_edge_dialog = RandomEdge_Dialog(design=self.design)
        random_edge_dialog.designUpdated.connect(self.updateDesign)
        random_edge_dialog.exec_()  # PyQt5Used inexec_()

    def handleCustomEdgeDesign(self):
        custom_edge_dialog = CustomEdge_Dialog(design=self.design)
        custom_edge_dialog.designUpdated.connect(self.updateDesign)
        custom_edge_dialog.exec_()  # PyQt5Used inexec_()

    def updateDesign(self, updated_design):
        self.design = updated_design
        print("topology中的设计已更新")
        # self.design.topology.show_image()
        self.designUpdated.emit(self.design)  # emit a signal，Transfer the updated design


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    dialog = Dialog_Topology(design=Design())
    dialog.designUpdated.connect(lambda updated_design: print("主窗口接收到更新后的设计!"))
    dialog.show()
    sys.exit(app.exec_())  # PyQt5Used inexec_()