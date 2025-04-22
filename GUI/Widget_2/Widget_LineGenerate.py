import sys
import os

# 获取当前脚本所在的目录
current_path = os.path.dirname(os.path.abspath(__file__))
GUI_PATH = os.path.dirname(current_path)
PROJ_PATH = os.path.dirname(GUI_PATH)

# 添加路径
sys.path.append(GUI_PATH)
sys.path.append(PROJ_PATH)

from PySide6 import QtWidgets, QtCore
from PySide6.QtGui import QFont
from api.design import Design
from GUI.Widget.Generate_Ctls import Dialog_ctls
from GUI.Widget.Generate_Cpls import Dialog_cpls
from GUI.Widget.Generate_Crosvs import Dialog_crosvs
from GUI.Widget.Generate_Tmls import Dialog_tmls
class Dialog_Line(QtWidgets.QDialog):
    # 定义一个信号用于设计更新
    designUpdated = QtCore.Signal(object)

    def __init__(self, design):
        super().__init__()
        self.setWindowTitle("Line Options")
        self.design = design
        # 设置窗口大小和位置
        self.setGeometry(500, 300, 380, 320)  # 调整高度以适应新按钮
        # 设置整个界面的字体为微软雅黑
        self.setFont(QFont("Microsoft YaHei", 11))
        # 创建主网格布局
        layout = QtWidgets.QGridLayout()

        # 创建按钮
        self.control_lines_button = QtWidgets.QPushButton("Control_lines")
        self.coupling_lines_button = QtWidgets.QPushButton("Coupling_lines")
        self.cross_overs_button = QtWidgets.QPushButton("Cross_Overs")
        self.transmission_lines_button = QtWidgets.QPushButton("Transmission_lines")  # 新增按钮

        # 设置按钮颜色为浅灰色
        self.control_lines_button.setStyleSheet("background-color: lightgray;")
        self.coupling_lines_button.setStyleSheet("background-color: lightgray;")
        self.cross_overs_button.setStyleSheet("background-color: lightgray;")
        self.transmission_lines_button.setStyleSheet("background-color: lightgray;")  # 设置新按钮颜色

        # 设置按钮大小
        self.control_lines_button.setFixedSize(200, 40)
        self.coupling_lines_button.setFixedSize(200, 40)
        self.cross_overs_button.setFixedSize(200, 40)
        self.transmission_lines_button.setFixedSize(200, 40)  # 设置新按钮大小


        # 将按钮添加到布局中并居中
        layout.addWidget(self.control_lines_button, 0, 0, alignment=QtCore.Qt.AlignCenter)
        layout.addWidget(self.coupling_lines_button, 1, 0, alignment=QtCore.Qt.AlignCenter)
        layout.addWidget(self.cross_overs_button, 2, 0, alignment=QtCore.Qt.AlignCenter)
        layout.addWidget(self.transmission_lines_button, 3, 0, alignment=QtCore.Qt.AlignCenter)  # 添加新按钮到布局

        # 设置布局的水平和垂直间距
        layout.setVerticalSpacing(15)

        # 设置主布局
        self.setLayout(layout)

        # 连接按钮点击事件到处理函数
        self.control_lines_button.clicked.connect(self.handle_control_lines)
        self.coupling_lines_button.clicked.connect(self.handle_coupling_lines)
        self.cross_overs_button.clicked.connect(self.handle_cross_overs)
        self.transmission_lines_button.clicked.connect(self.handle_transmission_lines)  # 连接新按钮到处理函数

    def handle_control_lines(self):
        print("Handling Control Lines")
        Dialog_control = Dialog_ctls(self.design)
        Dialog_control.designUpdated.connect(self.updateDesign)
        Dialog_control.exec()
        self.designUpdated.emit(self.design)  # 发出设计更新信号


    def handle_coupling_lines(self):
        print("Handling Coupling Lines")
        Dialog_coupling = Dialog_cpls(self.design)
        Dialog_coupling.designUpdated.connect(self.updateDesign)
        Dialog_coupling.exec()
        self.designUpdated.emit(self.design)


    def handle_cross_overs(self):
        print("Handling Cross Overs")
        Dialog_cross = Dialog_crosvs(self.design)
        Dialog_cross.designUpdated.connect(self.updateDesign)
        Dialog_cross.exec()
        self.designUpdated.emit(self.design)


    def handle_transmission_lines(self):  # 新增处理函数
        print("Handling Transmission Lines")
        Dialog_transmission = Dialog_tmls(self.design)
        Dialog_transmission.designUpdated.connect(self.updateDesign)
        Dialog_transmission.exec()
        self.designUpdated.emit(self.design)  # 发出设计更新信号


    def updateDesign(self, updated_design):
        self.design = updated_design
        print("LineGenerate中的设计已更新")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    design = Design()
    # 创建并显示对话框
    dialog = Dialog_Line(design=design)
    # 连接设计更新信号到处理函数
    dialog.designUpdated.connect(lambda updated_design: print("Design updated:", updated_design))
    dialog.show()

    sys.exit(app.exec())