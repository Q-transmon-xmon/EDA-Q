import sys
import os

# 获取当前脚本所在的目录
current_path = os.path.dirname(os.path.abspath(__file__))
GUI_PATH = os.path.dirname(current_path)
PROJ_PATH = os.path.dirname(GUI_PATH)

# 添加路径
sys.path.append(GUI_PATH)
sys.path.append(PROJ_PATH)

from PySide6 import QtWidgets
from PySide6.QtCore import (QCoreApplication, QMetaObject, QRect, Qt, Signal, QSettings)
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QDialog, QDialogButtonBox, QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QWidget)
from api.design import Design
from GUI_3_4_6.Widget.Show_Dataframe import DataFrameDisplay


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(400, 300)
        # 设置整个界面的字体为微软雅黑
        Dialog.setFont(QFont("Microsoft YaHei", 10.5))
        self.widget_parameter = QWidget(Dialog)
        self.widget_parameter.setObjectName(u"widget_parameter")
        self.widget_parameter.setGeometry(QRect(90, 60, 281, 131))
        self.widget_parameter.setStyleSheet(u"background-color: rgb(214, 214, 214);")
        self.verticalLayout_2 = QVBoxLayout(self.widget_parameter)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_3 = QLabel(self.widget_parameter)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout.addWidget(self.label_3)

        self.lineEdit = QLineEdit(self.widget_parameter)
        self.lineEdit.setObjectName(u"lineEdit")

        self.horizontalLayout.addWidget(self.lineEdit)

        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_4 = QLabel(self.widget_parameter)
        self.label_4.setObjectName(u"label_4")

        self.horizontalLayout_2.addWidget(self.label_4)

        self.lineEdit_2 = QLineEdit(self.widget_parameter)
        self.lineEdit_2.setObjectName(u"lineEdit_2")

        self.horizontalLayout_2.addWidget(self.lineEdit_2)

        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.label_2 = QLabel(Dialog)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(10, 50, 61, 31))
        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(20, 240, 341, 32))
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)

        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", "Transmon", None))
        self.label_3.setText(QCoreApplication.translate("Dialog", "比特名称：", None))
        self.label_4.setText(QCoreApplication.translate("Dialog", "比特频率：", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", "仿真参数：", None))


class Dialog_Transmon(QDialog, Ui_Dialog):
    designUpdated = Signal(object)

    def __init__(self, design):
        super(Dialog_Transmon, self).__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # 存储传入的 design 参数
        self.design = design

        # 使用 QSettings 保存和加载输入的数据
        self.settings = QSettings("MyCompany", "MyApp")

        # 读取上一次保存的输入内容并显示
        self.loadPreviousInputs()

        # 连接按钮的信号
        self.ui.buttonBox.accepted.connect(self.process_transmon)
        self.ui.buttonBox.rejected.connect(self.reject)

        # 初始化矩阵对话框为 None
        self.matrix_dialog = None

    def loadPreviousInputs(self):
        """加载上一次保存的输入内容"""
        self.ui.lineEdit.setText(self.settings.value("bit_name", "q0", type=str))
        self.ui.lineEdit_2.setText(self.settings.value("bit_freq", "5.6", type=str))

    def process_transmon(self):
        """保存输入框的文本到 QSettings,并发出 designUpdated 信号"""
        # 保存输入内容
        self.settings.setValue("bit_name", self.ui.lineEdit.text())
        self.settings.setValue("bit_freq", self.ui.lineEdit_2.text())

        # 获取输入内容
        bit_name = self.settings.value("bit_name", "", type=str)
        bit_freq = self.settings.value("bit_freq", "", type=float)

        # 打印输入内容
        print(f"比特名称: {bit_name}")
        print(f"比特频率: {bit_freq}")

        # 调用设计的仿真方法
        self.design.simulation(sim_module="TransmonSim", frequency=bit_freq, qubit_name=bit_name)

        # 发出设计更新信号
        self.designUpdated.emit(self.design)

        # 接受对话框
        self.accept()

        # 在对话框关闭后显示矩阵窗口
        self.show_matrix_display()

    def show_matrix_display(self):
        """显示矩阵窗口"""
        file_path = 'C:/sim_proj/transmon_sim/capacitance_matrix.txt'

        # 检查文件是否存在
        if not os.path.exists(file_path):
            print(f"文件 {file_path} 不存在，无法显示矩阵窗口")
            return

        print('xianshi')

            # 创建并显示 DataFrameDisplay 窗口
        self.matrix_dialog = DataFrameDisplay(file_path=file_path)
        self.matrix_dialog.exec()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    design = Design()  # 创建 Design 实例
    dialog = Dialog_Transmon(design=design)  # 将 design 实例传递给 Dialog_Transmon


    # 更新主设计的信号
    def updateMainDesign(updated_design):
        print("主窗口设计已更新")


    dialog.designUpdated.connect(updateMainDesign)

    # 显示对话框
    if dialog.exec() == QDialog.Accepted:
        pass

        # 退出应用程序
    sys.exit(app.exec())