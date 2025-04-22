import sys
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import QCoreApplication, QMetaObject, QSettings
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QDialog, QDialogButtonBox, QLabel, QLineEdit,
                               QRadioButton, QVBoxLayout, QWidget)

from api.design import Design

class Ui_Dialog_RAlgorithm(object):
    def setupUi(self, Dialog_RAlgorithm):
        Dialog_RAlgorithm.setObjectName("Dialog_RAlgorithm")
        Dialog_RAlgorithm.resize(419, 332)
        # 设置整个界面的字体为微软雅黑
        Dialog_RAlgorithm.setFont(QFont("Microsoft YaHei", 10.5))
        self.settings = QSettings("MyCompany", "MyApp")  # 初始化 QSettings

        self.buttonBox = QDialogButtonBox(Dialog_RAlgorithm)
        self.buttonBox.setGeometry(30, 280, 341, 32)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)

        self.label = QLabel(Dialog_RAlgorithm)
        self.label.setGeometry(10, 60, 51, 25)
        self.label.setText("算法：")  # 设置标签文本

        # 创建"算法"标签并设置文本
        self.label_algorithm = QLabel(Dialog_RAlgorithm)
        self.label_algorithm.setGeometry(10, 200, 181, 25)
        self.label_algorithm.setText("芯片层：")  # 设置标签文本为"算法"

        self.lineEdit = QLineEdit(Dialog_RAlgorithm)
        self.lineEdit.setGeometry(80, 200, 181, 28)

        self.widget = QWidget(Dialog_RAlgorithm)
        self.widget.setGeometry(78, 53, 301, 121)
        self.widget.setStyleSheet("background-color: rgb(213, 213, 213);")
        self.verticalLayout = QVBoxLayout(self.widget)

        self.radioButtons = []
        self.setStyleSheet("QRadioButton { font-family: 'Microsoft YaHei'; font-size: 14px; }")  # 设置单选按钮的字体样式
        self.addRadioButton("Control_off_chip_routing")  # 单选按钮文本
        self.addRadioButton("Flipchip_routing_IBM")  # 单选按钮文本
        self.addRadioButton("Flipchip_routing")  # 单选按钮文本

        self.retranslateUi(Dialog_RAlgorithm)

        QMetaObject.connectSlotsByName(Dialog_RAlgorithm)

        self.loadInputs()  # 载入先前保存的数据

    def retranslateUi(self, Dialog_RAlgorithm):
        Dialog_RAlgorithm.setWindowTitle(QCoreApplication.translate("Dialog_RAlgorithm", "选择布线算法", None))

    def addRadioButton(self, text):
        """添加单选按钮到布局中"""
        radio_btn = QRadioButton(text, self.widget)
        self.verticalLayout.addWidget(radio_btn)
        self.radioButtons.append(radio_btn)


class Dialog_RAlgorithm(QDialog, Ui_Dialog_RAlgorithm):

    designUpdated = QtCore.Signal(object)
    def __init__(self, design):
        super(Dialog_RAlgorithm, self).__init__()
        self.design = design
        self.setupUi(self)
        self.settings = QSettings("MyCompany", "MyApp")
        self.loadInputs()  # 加载输入数据

        # 连接保存输入的方法
        self.buttonBox.accepted.connect(self.Process_RAlgorithm)
        self.buttonBox.rejected.connect(self.reject)

        # 新增变量
        self.selected_algorithm = None
        self.chip_name = None

    def loadInputs(self):
        """加载保存的输入框数据显示"""
        self.lineEdit.setText(self.settings.value("parameter_value", "", type=str))

        # 加载单选按钮的状态
        for radio_btn in self.radioButtons:
            radio_btn.setChecked(self.settings.value(radio_btn.text(), False, type=bool))

    def Process_RAlgorithm(self):
        """保存输入框的文本到 QSettings"""
        self.settings.setValue("parameter_value", self.lineEdit.text())

        # 保存单选按钮的状态
        for radio_btn in self.radioButtons:
            self.settings.setValue(radio_btn.text(), radio_btn.isChecked())
            if radio_btn.isChecked():
                self.selected_algorithm = radio_btn.text()  # 保存选择的算法名称

        self.chip_name = self.lineEdit.text()  # 保存输入的芯片名称

        print(f"输入的参数: {self.chip_name}")
        print("选中的单选按钮：", self.selected_algorithm)

        self.design.routing(method=self.selected_algorithm, chip_name=self.chip_name)
        self.designUpdated.emit(self.design)  # 发送设计更新信号
        self.accept()  # 关闭对话框

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    design = Design()
    dialog = Dialog_RAlgorithm(design=design)
    # 更新主设计的信号
    def updateMainDesign(updated_design):
        design=updated_design
        print("主窗口设计已更新")
    dialog.designUpdated.connect(updateMainDesign)

    if dialog.exec() == QDialog.Accepted:
        # 点击OK按钮后会自动处理参数并退出
        pass

    sys.exit(app.exec())