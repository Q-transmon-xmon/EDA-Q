import sys
from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox)
from addict import Dict
from api.design import Design

class Dialog_tmls(QDialog):
    # 定义一个信号用于设计更新
    designUpdated = QtCore.Signal(object)
    def __init__(self, design,parent=None):
        super().__init__(parent)
        self.setWindowTitle("Transmission_line")
        self.setFont(QFont("Microsoft YaHei", 10.5))
        self.resize(600, 400)
        self.design = design
        # 预定义的字典模板
        self.tml_ops_template = Dict(
            name="tmls0",
            type="TransmissionPath",
            chip_name="chip0",
            pos=[(-1000, 1100), (-1000, 1250), (15000, 1250), (15000, 1000)],
            corner_radius=90
        )

        # 友好的标签映射
        self.labels = {
            "name": "名称",
            "type": "类型",
            "chip_name": "芯片层",
            "pos": "位置",
            "corner_radius": "半径"
        }

        self.process_function = self.default_process_function  # 默认处理函数
        self.lineEdits = {}  # 存储每个键对应的输入框
        self.input_types = {}  # 存储每个键的类型

        # 主布局
        self.mainLayout = QVBoxLayout(self)

        # 动态加载字典模板
        self.loadDictionary()

        # 添加按钮
        self.buttonLayout = QHBoxLayout()
        self.processButton = QPushButton("添加")
        self.cancelButton = QPushButton("取消")

        # 设置按钮大小
        self.processButton.setFixedSize(80, 30)
        self.cancelButton.setFixedSize(80, 30)

        self.buttonLayout.addWidget(self.processButton)
        self.buttonLayout.addWidget(self.cancelButton)
        self.buttonLayout.setAlignment(Qt.AlignRight)  # 右对齐
        self.mainLayout.addLayout(self.buttonLayout)

        # 连接按钮事件
        self.processButton.clicked.connect(self.processDictionary)
        self.cancelButton.clicked.connect(self.reject)

    def loadDictionary(self):
        """动态加载字典模板并生成输入框"""
        for key, value in self.tml_ops_template.items():
            # 创建水平布局
            layout = QHBoxLayout()

            # 创建标签
            label = QLabel(f"{self.labels[key]}：")  # 使用友好的标签
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

    def processDictionary(self):
        """处理用户输入并调用处理函数"""
        valid_input = True
        updated_dict = Dict()

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

                updated_dict[key] = converted_value  # 保存到更新后的字典
            except (ValueError, SyntaxError) as e:
                QMessageBox.warning(self, "无效输入", f"{self.labels[key]} 的输入无效: {e}")
                valid_input = False
                break

        if valid_input:
            # 调用处理函数
            self.process_function(updated_dict)
            self.accept()  # 关闭对话框

    def default_process_function(self, tml_ops):
        """
        默认处理函数，接收用户输入的字典作为参数
        :param tml_ops: 用户输入的字典
        """
        print("处理后的字典：", tml_ops)
        self.design.gds.transmission_lines.add(options=tml_ops)
        self.designUpdated.emit(self.design)  # 发出设计更新信号

        # 在这里添加你的处理逻辑
        # QMessageBox.information(None, "处理完成", f"字典已处理：\n{tml_ops}")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    design = Design()
    design.generate_topology(topo_col=4, topo_row=4)
    design.generate_qubits(topology=True, qubits_type='Xmon')
    # 创建并显示对话框
    dialog = Dialog_tmls(design=design)
    dialog.exec()

    sys.exit(app.exec())