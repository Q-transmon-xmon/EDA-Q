from PyQt5 import QtCore, QtWidgets
import sys
import os

# 获取当前脚本所在的目录
current_path = os.path.dirname(os.path.abspath(__file__))
GUI_PATH = os.path.dirname(current_path)
PROJ_PATH = os.path.dirname(GUI_PATH)

# 添加路径
sys.path.append(GUI_PATH)
sys.path.append(PROJ_PATH)


from PyQt5.QtGui import QFont
from api.design import Design
from GUI_3_4_6.Widget.Topo_Node import Dialog_Node
from GUI_3_4_6.Widget.Topo_RandomEdge import RandomEdge_Dialog
from GUI_3_4_6.Widget.Topo_CustomEdge import CustomEdge_Dialog


class Ui_Dialog_Topology(object):
    def setupUi(self, Dialog_Topology):
        Dialog_Topology.setObjectName("Dialog_topology")
        Dialog_Topology.resize(500, 300)
        # 设置整个界面的字体为微软雅黑，支持浮点字号
        font = QFont("Microsoft YaHei")
        font.setPointSizeF(9)  # 使用浮点数设置字体大小
        Dialog_Topology.setFont(font)
        # 剩余代码保持不变
        self.mainLayout = QtWidgets.QVBoxLayout(Dialog_Topology)
        self.mainLayout.setObjectName("mainLayout")

        # 创建一个水平布局用于居中按钮
        self.centerLayout = QtWidgets.QHBoxLayout()
        self.centerLayout.setObjectName("centerLayout")

        # 创建一个垂直布局用于按钮
        self.buttonLayout = QtWidgets.QVBoxLayout()
        self.buttonLayout.setObjectName("buttonLayout")
        self.buttonLayout.setSpacing(20)  # 设置按钮之间的间隔

        # 将按钮添加到垂直布局中
        self.pushButton = QtWidgets.QPushButton(Dialog_Topology)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setMinimumSize(150, 50)  # 设置按钮的最小尺寸
        self.buttonLayout.addWidget(self.pushButton)

        self.pushButton_2 = QtWidgets.QPushButton(Dialog_Topology)
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.setMinimumSize(150, 50)  # 设置按钮的最小尺寸
        self.buttonLayout.addWidget(self.pushButton_2)

        self.pushButton_3 = QtWidgets.QPushButton(Dialog_Topology)
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_3.setMinimumSize(150, 50)  # 设置按钮的最小尺寸
        self.buttonLayout.addWidget(self.pushButton_3)

        # 将按钮布局添加到中心布局中
        self.centerLayout.addStretch()
        self.centerLayout.addLayout(self.buttonLayout)
        self.centerLayout.addStretch()

        # 将中心布局添加到主布局中
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
    # PyQt5中的信号定义，改为QtCore.pyqtSignal
    designUpdated = QtCore.pyqtSignal(Design)  # 定义自定义信号

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
        node_dialog.exec_()  # PyQt5中使用exec_()

    def handleRandomEdgeDesign(self):
        random_edge_dialog = RandomEdge_Dialog(design=self.design)
        random_edge_dialog.designUpdated.connect(self.updateDesign)
        random_edge_dialog.exec_()  # PyQt5中使用exec_()

    def handleCustomEdgeDesign(self):
        custom_edge_dialog = CustomEdge_Dialog(design=self.design)
        custom_edge_dialog.designUpdated.connect(self.updateDesign)
        custom_edge_dialog.exec_()  # PyQt5中使用exec_()

    def updateDesign(self, updated_design):
        self.design = updated_design
        print("topology中的设计已更新")
        # self.design.topology.show_image()
        self.designUpdated.emit(self.design)  # 发出信号，传递更新后的设计


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    dialog = Dialog_Topology(design=Design())
    dialog.designUpdated.connect(lambda updated_design: print("主窗口接收到更新后的设计!"))
    dialog.show()
    sys.exit(app.exec_())  # PyQt5中使用exec_()