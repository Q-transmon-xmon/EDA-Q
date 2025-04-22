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
from GUI.Widget.Show_Dataframe import DataFrameDisplay
class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(600, 400)
        # 设置整个界面的字体为微软雅黑
        Dialog.setFont(QFont("Microsoft YaHei", 10.5))
        self.label_2 = QLabel(Dialog)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(20, 40, 61, 31))
        self.widget_parameter = QWidget(Dialog)
        self.widget_parameter.setObjectName(u"widget_parameter")
        self.widget_parameter.setGeometry(QRect(90, 50, 450, 250))
        self.widget_parameter.setStyleSheet(u"background-color: rgb(214, 214, 214);")
        self.verticalLayout = QVBoxLayout(self.widget_parameter)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_5 = QLabel(self.widget_parameter)
        self.label_5.setObjectName(u"label_5")

        self.horizontalLayout_3.addWidget(self.label_5)

        self.lineEdit_3 = QLineEdit(self.widget_parameter)
        self.lineEdit_3.setObjectName(u"lineEdit_3")
        self.lineEdit_3.setMinimumWidth(300)

        self.horizontalLayout_3.addWidget(self.lineEdit_3)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_6 = QLabel(self.widget_parameter)
        self.label_6.setObjectName(u"label_6")

        self.horizontalLayout_4.addWidget(self.label_6)

        self.lineEdit_4 = QLineEdit(self.widget_parameter)
        self.lineEdit_4.setObjectName(u"lineEdit_4")
        self.lineEdit_4.setMinimumWidth(300)

        self.horizontalLayout_4.addWidget(self.lineEdit_4)


        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label_8 = QLabel(self.widget_parameter)
        self.label_8.setObjectName(u"label_8")

        self.horizontalLayout_6.addWidget(self.label_8)

        self.lineEdit_6 = QLineEdit(self.widget_parameter)
        self.lineEdit_6.setObjectName(u"lineEdit_6")
        self.lineEdit_6.setMinimumWidth(300)

        self.horizontalLayout_6.addWidget(self.lineEdit_6)


        self.verticalLayout.addLayout(self.horizontalLayout_6)

        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(50, 330, 500, 32))
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", "Xmon", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", "仿真参数：", None))
        self.label_5.setText(QCoreApplication.translate("Dialog", "控制线名称：", None))
        self.label_6.setText(QCoreApplication.translate("Dialog", "比特名称：", None))
        self.label_8.setText(QCoreApplication.translate("Dialog", "保存路径：", None))
    # retranslateUi

class Dialog_Xmon(QDialog, Ui_Dialog):
    designUpdated = Signal(object)

    def __init__(self, design):
        super(Dialog_Xmon, self).__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # 存储传入的 design 参数
        self.design = design

        # 使用 QSettings 保存和加载输入的数据
        self.settings = QSettings("MyCompany", "MyApp")

        # 读取上一次保存的输入内容并显示
        self.loadPreviousInputs()

        # 连接按钮的信号
        self.ui.buttonBox.accepted.connect(self.process_xmon)
        self.ui.buttonBox.rejected.connect(self.reject)

    def loadPreviousInputs(self):
        """加载上一次保存的输入内容"""
        self.ui.lineEdit_3.setText(self.settings.value("control_line_name", "control_lines_upper_0", type=str))
        self.ui.lineEdit_4.setText(self.settings.value("bit_name", "q0", type=str))
        self.ui.lineEdit_6.setText(self.settings.value("save_path", "C:/sim_proj/PlaneXmon_sim/Xmon_random_capacity_{}.txt", type=str))

    def process_xmon(self):
        """保存输入框的文本到 QSettings,并发出 designUpdated 信号"""
        self.settings.setValue("control_line_name", self.ui.lineEdit_3.text())
        self.settings.setValue("bit_name", self.ui.lineEdit_4.text())
        self.settings.setValue("save_path", self.ui.lineEdit_6.text())

        ctl_name = self.settings.value("control_line_name","", type=str)
        bit_name = self.settings.value("bit_name","", type=str)
        save_path = self.settings.value("save_path", "", type=str)

        print(f"控制线名称: {ctl_name}")
        print(f"比特名称: {bit_name}")
        print(f"save_path: {save_path}")

        # self.design.simulation(sim_module="PlaneXmonSim",qubit_name=bit_name,gds_ops=True)
        self.designUpdated.emit(self.design)
        show_matrix = DataFrameDisplay(file_path=save_path)
        show_matrix.exec()
        self.accept()

        # 在对话框关闭后显示矩阵窗口
        self.show_matrix_display(path=save_path)
    def show_matrix_display(self,path):
        """显示矩阵窗口"""
        file_path = path

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
    dialog = Dialog_Xmon(design=design)  # 将 design 实例传递给 Dialog_Qubit_Custom

    # 更新主设计的信号
    def updateMainDesign(updated_design):
        print("主窗口设计已更新")
    dialog.designUpdated.connect(updateMainDesign)

    # 如果对话框接受，显示输入内容
    if dialog.exec() == QDialog.Accepted:
        dialog.design.gds.show_svg()

    # 退出应用程序
    sys.exit(app.exec())