import os
import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QDialog, QLabel, QLineEdit, QGridLayout,
                             QPushButton, QMessageBox, QVBoxLayout, QHBoxLayout, QWidget, QDialogButtonBox)
from PyQt5.QtCore import Qt, QSettings, pyqtSignal
from api.design import Design


class Ui_Dialog:
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setMinimumSize(850, 420)  # 设置对话框的最小大小
        Dialog.setFont(QFont("Microsoft YaHei", 10))

        # 主布局
        self.mainLayout = QVBoxLayout(Dialog)
        self.mainLayout.addStretch(1)

        # 标题标签
        titleLabel = QLabel("Xmon Parameter Configuration")
        titleLabel.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        titleLabel.setAlignment(Qt.AlignCenter)
        self.mainLayout.addWidget(titleLabel)

        # 指导信息标签
        instructionsLabel = QLabel("Please enter the simulation parameters below:")
        instructionsLabel.setAlignment(Qt.AlignCenter)
        self.mainLayout.addWidget(instructionsLabel)

        # 输入部分
        self.layoutWidget = QWidget(Dialog)
        self.verticalLayout = QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setSpacing(20)
        self.verticalLayout.setContentsMargins(20, 20, 20, 20)

        self.defaults = ["control_lines_upper_0", "q0", "C:/sim_proj/PlaneXmon_sim/Xmon_random_capacity_{}.txt"]  # 默认值
        self.lineEdits = []

        self.createLabeledInput("Control Line Name:", self.defaults[0])
        self.createLabeledInput("Qubit Name:", self.defaults[1])
        self.createLabeledInput("Save Path:", self.defaults[2])

        self.mainLayout.addWidget(self.layoutWidget)

        # 按钮框
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(self.buttonBox.button(QDialogButtonBox.Ok))
        buttonLayout.addWidget(self.buttonBox.button(QDialogButtonBox.Cancel))

        self.mainLayout.addLayout(buttonLayout)
        self.mainLayout.addStretch(1)

    def createLabeledInput(self, label_text, default_value):
        """创建带标签的输入框"""
        layout = QHBoxLayout()  # 为每个输入项创建布局
        label = QLabel(label_text)
        label.setFixedWidth(180)  # 设置标签宽度
        line_edit = QLineEdit()
        line_edit.setMinimumWidth(300)

        # 设置默认值
        line_edit.setPlaceholderText(default_value)
        layout.addWidget(label)
        layout.addWidget(line_edit)
        self.verticalLayout.addLayout(layout)  # 添加到垂直布局
        self.lineEdits.append(line_edit)  # 保存输入框

    def get_line_edits(self):
        return self.lineEdits


class Dialog_Xmon(QDialog):
    designUpdated = pyqtSignal(object)  # 定义信号以通知设计更新

    def __init__(self, design):
        super().__init__()
        self.design = design
        self.settings = QSettings("MyCompany", "MyApp")

        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # 连接信号
        self.ui.buttonBox.accepted.connect(self.checkInputs)  # OK按钮
        self.ui.buttonBox.rejected.connect(self.reject)  # 取消按钮

        # 为输入框设置事件过滤器
        for line_edit in self.ui.get_line_edits():
            line_edit.installEventFilter(self)

    def eventFilter(self, source, event):
        """处理Tab键事件以设置默认值"""
        if event.type() == QtCore.QEvent.KeyPress and event.key() == Qt.Key_Tab:
            for line_edit in self.ui.get_line_edits():
                if line_edit.hasFocus():
                    # 如果输入框为空，则设置为默认值
                    if line_edit.text().strip() == "":
                        line_edit.setText(line_edit.placeholderText())
                        # 转到下一个输入框
                    next_index = self.ui.get_line_edits().index(line_edit) + 1
                    if next_index < len(self.ui.get_line_edits()):
                        self.ui.get_line_edits()[next_index].setFocus()
                    return True  # 阻止进一步处理
        return super().eventFilter(source, event)

    def checkInputs(self):
        inputs = []
        for i, line_edit in enumerate(self.ui.get_line_edits()):
            # 如果为空，使用默认值
            value = line_edit.text().strip() or self.ui.defaults[i]
            # 检查值
            if not value:
                QMessageBox.critical(self, "Input Error", "All fields must be filled out. Please enter valid values.")
                return

                # 尝试转换为字符串
            inputs.append(value)

            # 处理节点输入
        self.processNode(inputs)

    def processNode(self, inputs):
        self.settings.setValue("control_line_name", inputs[0])
        self.settings.setValue("Qubit_name", inputs[1])
        self.settings.setValue("save_path", inputs[2])

        print(f"Control Line Name: {inputs[0]}")
        print(f"Qubit Name: {inputs[1]}")
        print(f"Save Path: {inputs[2]}")

        # 生成拓扑并发出更新信号
        self.design.simulation(sim_module="PlaneXmonSim", qubit_name=inputs[1], gds_ops=True)
        # self.design.generate_topology(control_line=inputs[0], bit_name=inputs[1], save_path=inputs[2])
        self.designUpdated.emit(self.design)  # 发出设计更新信号
        self.accept()  # 关闭对话框


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    design = Design()  # 实例化设计对象
    dialog = Dialog_Xmon(design=design)  # 创建对话框

    dialog.designUpdated.connect(
        lambda updated_design: print("Design Updated Back to Main Window!"))  # 连接信号
    dialog.exec_()  # 显示对话框

    sys.exit(app.exec_())