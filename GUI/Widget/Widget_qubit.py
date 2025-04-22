# -*- coding: utf-8 -*-  

from PySide6 import QtCore, QtWidgets, QtGui
import sys
import os

# 获取当前脚本所在的目录
current_path = os.path.dirname(os.path.abspath(__file__))
GUI_PATH = os.path.dirname(current_path)
PROJ_PATH = os.path.dirname(GUI_PATH)

# 添加路径
sys.path.append(GUI_PATH)
sys.path.append(PROJ_PATH)

from api.design import Design  # 导入 Design 类
from GUI.Widget.Qubit_Custom import Dialog_Qubit_Custom
from GUI.Widget.Qubit_type import SelectionDialog
class Ui_Dialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Ui_Dialog, self).__init__(parent)
        self.setupUi()

    def setupUi(self):
        self.setObjectName("Dialog")
        self.resize(336, 147)

        # 创建垂直布局
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setAlignment(QtCore.Qt.AlignCenter)  # 设置布局居中
        self.layout.setSpacing(20)  # 设置布局间距为20

        self.label = QtWidgets.QLabel(self)
        self.label.setObjectName("label")
        self.label.setFont(QtGui.QFont("微软雅黑", 12))  # 设置字体为微软雅黑，大小为12
        self.layout.addWidget(self.label, alignment=QtCore.Qt.AlignCenter)  # 添加标签并居中

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

        self.layout.addWidget(self.widget, alignment=QtCore.Qt.AlignCenter)  # 添加按钮容器并居中

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
    # 定义一个信号用于设计更新
    designUpdated = QtCore.Signal(object)

    def __init__(self, design, parent=None):
        super(Dialog_Qubit, self).__init__(parent)
        self.design = design  # Store the passed design parameter

        # 连接按钮点击信号
        self.pushButton.clicked.connect(self.handleTrue)
        self.pushButton_2.clicked.connect(self.handleFalse)

    def handleTrue(self):
        """处理 True 按钮点击事件"""
        print("User selected: True")
        # self.design.generate_topology(topo_col=4, topo_row=4)
        # self.design.gds.show_svg(width=300)
        Qubit_type_dialog = SelectionDialog(design=self.design)
        Qubit_type_dialog.designUpdated.connect(self.updateDesign)
        Qubit_type_dialog.exec_()
        self.designUpdated.emit(self.design)  # 发出设计更新信号
        self.accept()  # 关闭对话框

    def handleFalse(self):
        """处理 False 按钮点击事件"""
        print("User selected: False")
        Qubit_Custom_dialog = Dialog_Qubit_Custom(design=self.design)
        Qubit_Custom_dialog.designUpdated.connect(self.updateDesign)
        Qubit_Custom_dialog.exec()
        self.designUpdated.emit(self.design)  # 发出设计更新信号
        self.accept()  # 关闭对话框

    def updateDesign(self, updated_design):
        self.design = updated_design
        print("Qubit中的设计已更新")
        # self.design.topology.show_image()
        # self.designUpdated.emit(self.design)  # 发出信号，传递更新后的设计

if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)

    # 设置全局字体为微软雅黑
    app.setFont(QtGui.QFont("微软雅黑", 10))  # 设置全局字体为微软雅黑，大小为10

    design = Design()  # 创建 Design 实例
    dialog = Dialog_Qubit(design=design)  # 将 design 实例传递给 Dialog_Qubit

    # 连接设计更新信号到处理函数
    dialog.designUpdated.connect(lambda updated_design: print("Design updated:", updated_design))

    dialog.exec()
    sys.exit(app.exec())