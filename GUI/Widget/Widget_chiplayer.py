# -*- coding: utf-8 -*-
import sys
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import QCoreApplication, QSettings
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QDialog, QDialogButtonBox, QHBoxLayout,
                               QLabel, QLineEdit, QRadioButton,
                               QVBoxLayout, QWidget)
from api.design import Design

class Ui_Dialog_ChipLayer:
    def setupUi(self, Dialog_ChipLayer):
        if not Dialog_ChipLayer.objectName():
            Dialog_ChipLayer.setObjectName("Dialog_ChipLayer")
        Dialog_ChipLayer.resize(450, 350)
        # 设置整个界面的字体为微软雅黑
        Dialog_ChipLayer.setFont(QFont("Microsoft YaHei", 10.5))

        # 创建按钮框
        self.buttonBox = QDialogButtonBox(Dialog_ChipLayer)
        self.buttonBox.setGeometry(30, 300, 341, 32)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.buttonBox.button(QDialogButtonBox.Ok).setText("Add")  # 将 Ok 按钮改为 Add

        # 创建 Delete 按钮
        self.deleteButton = QtWidgets.QPushButton("Delete", Dialog_ChipLayer)
        self.deleteButton.setGeometry(380, 300, 60, 32)  # 设置 Delete 按钮的位置和大小

        # 创建主布局
        self.layoutWidget = QWidget(Dialog_ChipLayer)
        self.layoutWidget.setGeometry(40, 20, 331, 251)
        self.verticalLayout = QVBoxLayout(self.layoutWidget)

        # 创建芯片层名称输入框
        layout_h = QHBoxLayout()
        self.chip_name_label = QLabel("芯片层名称：")
        self.chip_name_input = QLineEdit()
        layout_h.addWidget(self.chip_name_label)
        layout_h.addWidget(self.chip_name_input)
        self.verticalLayout.addLayout(layout_h)

        # 创建单选按钮
        layout_h = QHBoxLayout()
        label = QLabel("芯片层参数：")
        self.radioButton_define = QRadioButton("自定义")
        self.radioButton_adapt = QRadioButton("自适应距离参数")
        layout_h.addWidget(label)
        layout_h.addWidget(self.radioButton_define)
        layout_h.addWidget(self.radioButton_adapt)
        self.verticalLayout.addLayout(layout_h)

        # 创建参数输入框
        layout_h = QHBoxLayout()
        self.left_param_label = QLabel("左上角参数：")
        self.left_param_input = QLineEdit()
        layout_h.addWidget(self.left_param_label)
        layout_h.addWidget(self.left_param_input)
        self.verticalLayout.addLayout(layout_h)

        layout_h = QHBoxLayout()
        self.right_param_label = QLabel("右上角参数：")
        self.right_param_input = QLineEdit()
        layout_h.addWidget(self.right_param_label)
        layout_h.addWidget(self.right_param_input)
        self.verticalLayout.addLayout(layout_h)

        layout_h = QHBoxLayout()
        self.distance_label = QLabel("距离：")
        self.distance_input = QLineEdit()
        layout_h.addWidget(self.distance_label)
        layout_h.addWidget(self.distance_input)
        self.verticalLayout.addLayout(layout_h)

        # 隐藏左上角、右上角和距离输入框和标签
        self.left_param_label.setVisible(False)
        self.left_param_input.setVisible(False)
        self.right_param_label.setVisible(False)
        self.right_param_input.setVisible(False)
        self.distance_label.setVisible(False)
        self.distance_input.setVisible(False)

        self.retranslateUi(Dialog_ChipLayer)

        # 连接信号与槽
        self.buttonBox.accepted.connect(Dialog_ChipLayer.accept)
        self.buttonBox.rejected.connect(Dialog_ChipLayer.reject)

        # 连接自定义单选按钮的状态变化信号
        self.radioButton_define.toggled.connect(self.toggleInputs)
        self.radioButton_adapt.toggled.connect(self.toggleInputs)

    def toggleInputs(self):
        if self.radioButton_define.isChecked():
            self.left_param_label.setVisible(True)
            self.left_param_input.setVisible(True)
            self.right_param_label.setVisible(True)
            self.right_param_input.setVisible(True)
            self.distance_label.setVisible(False)
            self.distance_input.setVisible(False)
        elif self.radioButton_adapt.isChecked():
            self.left_param_label.setVisible(False)
            self.left_param_input.setVisible(False)
            self.right_param_label.setVisible(False)
            self.right_param_input.setVisible(False)
            self.distance_label.setVisible(True)
            self.distance_input.setVisible(True)
        else:
            self.left_param_label.setVisible(False)
            self.left_param_input.setVisible(False)
            self.right_param_label.setVisible(False)
            self.right_param_input.setVisible(False)
            self.distance_label.setVisible(False)
            self.distance_input.setVisible(False)

    def retranslateUi(self, Dialog_ChipLayer):
        Dialog_ChipLayer.setWindowTitle(QCoreApplication.translate("Dialog_ChipLayer", "生成芯片层"))

class Dialog_ChipLayer(QDialog, Ui_Dialog_ChipLayer):
    # 定义一个信号用于设计更新
    designUpdated = QtCore.Signal(object)
    def __init__(self, design):
        super(Dialog_ChipLayer, self).__init__()
        self.setupUi(self)
        self.design = design
        self.settings = QSettings("MyCompany", "MyApp")
        self.loadInputs()

        # 连接按钮信号
        self.buttonBox.accepted.connect(self.Process_Chiplayer)
        self.deleteButton.clicked.connect(self.deleteChipLayer)  # 连接 Delete 按钮

    def loadInputs(self):
        """加载默认参数值并显示在界面上"""
        # 设置默认值
        default_values = {
            "layer_name": "DefaultLayer",  # 默认芯片层名称
            "param_top_left": "10",  # 默认左上角参数
            "param_top_right": "20",  # 默认右上角参数
            "distance": "2000",  # 默认距离
            "is_custom": True  # 默认选择自定义模式
        }

        # 从 QSettings 加载参数值，如果没有保存过，则使用默认值
        self.chip_name_input.setText(self.settings.value("layer_name", default_values["layer_name"], type=str))
        self.left_param_input.setText(self.settings.value("param_top_left", default_values["param_top_left"], type=str))
        self.right_param_input.setText(
            self.settings.value("param_top_right", default_values["param_top_right"], type=str))
        self.distance_input.setText(self.settings.value("distance", default_values["distance"], type=str))

        # 根据保存的值或默认值设置单选按钮状态
        is_custom = self.settings.value("is_custom", default_values["is_custom"], type=bool)
        if is_custom:
            self.radioButton_define.setChecked(True)
        else:
            self.radioButton_adapt.setChecked(True)

            # 根据单选按钮的状态显示或隐藏相关输入框
        self.toggleInputs()

    def processCustomSettings(self):
        # 自定义
        param_top_left = self.left_param_input.text()
        param_top_right = self.right_param_input.text()
        layer_name = self.chip_name_input.text()
        print(f"自定义模式: 左上角参数: {param_top_left}, 右上角参数: {param_top_right}, 芯片层名称: {layer_name}")
        # self.design.  #  需要添加实际的design操作

    def processAdaptiveSettings(self):
        # 自适应
        layer_name = self.chip_name_input.text()
        distance = self.distance_input.text()
        distance = int(distance)
        print(f"自适应模式: 芯片层名称: {layer_name}, 距离: {distance}")
        self.design.generate_chip(chip_name=layer_name, dist=distance, qubits=True)

    def Process_Chiplayer(self):
        self.settings.setValue("layer_name", self.chip_name_input.text())
        self.settings.setValue("param_top_left", self.left_param_input.text())
        self.settings.setValue("param_top_right", self.right_param_input.text())
        self.settings.setValue("distance", self.distance_input.text())
        self.settings.setValue("is_custom", self.radioButton_define.isChecked())

        if self.radioButton_define.isChecked():
            self.processCustomSettings()
        elif self.radioButton_adapt.isChecked():
            self.processAdaptiveSettings()

        self.designUpdated.emit(self.design)  # 发出设计更新信号
        self.accept()

    def deleteChipLayer(self):
        """处理删除按钮的逻辑"""
        layer_name = self.chip_name_input.text()
        print(f"删除 {layer_name}")  # 输出删除的芯片层名称
        self.design.gds.chips.clear()
        self.designUpdated.emit(self.design)  # 发出设计更新信号
        self.reject()  # 关闭对话框

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    design = Design()
    dialog = Dialog_ChipLayer(design=design)
    dialog.designUpdated.connect(lambda updated_design: print("chiplayer设计已更新"))
    dialog.exec()
    sys.exit(app.exec())