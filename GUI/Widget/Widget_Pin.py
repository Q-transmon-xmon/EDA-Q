import sys

from PySide6 import QtCore
from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from addict import Dict
from api.design import Design

class Dialog_pins(QDialog):
    # 定义一个信号用于设计更新
    designUpdated = QtCore.Signal(object)
    def __init__(self, design,parent=None):
        super().__init__(parent)
        self.setWindowTitle("生成引脚")
        self.setFont(QFont("Microsoft YaHei", 10.5))
        self.resize(500, 300)
        self.design = design
        # 默认值
        self.default_values = Dict(
            name="pin0",
            type="LaunchPad",
            chip="chip0",
            pos=(0, 0),
            outline=[]
        )

        # 存储输入框和类型
        self.lineEdits = {}
        self.input_types = {}

        # 主布局
        self.mainLayout = QVBoxLayout(self)

        # 动态生成输入框
        self.loadInputs()

        # 按钮布局
        self.buttonLayout = QHBoxLayout()
        self.okButton = QPushButton("OK")
        self.cancelButton = QPushButton("Cancel")

        # 设置按钮大小
        self.okButton.setFixedSize(80, 30)
        self.cancelButton.setFixedSize(80, 30)

        # 添加按钮到布局
        self.buttonLayout.addWidget(self.okButton)
        self.buttonLayout.addWidget(self.cancelButton)
        self.buttonLayout.setAlignment(Qt.AlignRight)  # 按钮右对齐
        self.mainLayout.addLayout(self.buttonLayout)

        # 连接按钮事件
        self.okButton.clicked.connect(self.submitValues)
        self.cancelButton.clicked.connect(self.reject)

    def loadInputs(self):
        """动态生成输入框"""
        labels = {
            "name": "名称",
            "type": "类型",
            "chip": "芯片",
            "pos": "位置",
            "outline": "轮廓"
        }

        for key, value in self.default_values.items():
            # 创建水平布局
            layout = QHBoxLayout()

            # 创建标签
            label = QLabel(f"{labels[key]}：")
            layout.addWidget(label)

            # 创建输入框
            line_edit = QLineEdit()
            line_edit.setText(str(value))  # 设置默认值
            layout.addWidget(line_edit)

            # 保存输入框和类型
            self.lineEdits[key] = line_edit
            self.input_types[key] = type(value)

            # 添加到主布局
            self.mainLayout.addLayout(layout)

    def submitValues(self):
        """处理用户输入并打印结果"""
        pin_ops = Dict()
        valid_input = True

        for key, line_edit in self.lineEdits.items():
            value_str = line_edit.text()
            expected_type = self.input_types[key]

            try:
                # 根据类型转换输入值
                if expected_type == list:
                    # 如果是列表类型，尝试解析为 Python 列表
                    converted_value = eval(value_str)
                    if not isinstance(converted_value, list):
                        raise ValueError("输入值不是有效的列表")
                elif expected_type == tuple:
                    # 如果是元组类型，尝试解析为 Python 元组
                    converted_value = eval(value_str)
                    if not isinstance(converted_value, tuple):
                        raise ValueError("输入值不是有效的元组")
                else:
                    converted_value = expected_type(value_str)

                pin_ops[key] = converted_value  # 保存到更新后的字典
            except (ValueError, SyntaxError) as e:
                QMessageBox.warning(self, "无效输入", f"{key} 的输入无效: {e}")
                valid_input = False
                break

        if valid_input:
            # 打印结果
            print("用户输入的值：", pin_ops)
            self.design.gds.pins.add(options=pin_ops)
            self.designUpdated.emit(self.design)  # 发出设计更新信号
            # QMessageBox.information(self, "提交成功", f"输入的值已提交：\n{pin_ops}")
            self.accept()  # 关闭窗口


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 创建并显示对话框
    dialog = Dialog_pins(design=Design())
    dialog.exec()

    sys.exit(app.exec())