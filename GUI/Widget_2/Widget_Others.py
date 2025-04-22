import sys
from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QEvent
from PyQt5.QtGui import QFont
from addict import Dict
from api.design import Design

class Dialog_Others(QDialog):
    designUpdated = pyqtSignal(object)

    def __init__(self, design, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Others")
        self.setFont(QFont("Microsoft YaHei", 10))
        self.resize(400, 200)
        self.design = design
        # 更新后的默认值配置
        self.default_values = {
            "name": "In0",  # 默认线路名称
            "type": "IndiumBump",  # 默认元件类型
            "chip": "chip0"  # 默认芯片名称
        }
        self.lineEdits = {}
        self.input_types = {}

        self.mainLayout = QVBoxLayout(self)
        self.loadInputs()

        self.buttonLayout = QHBoxLayout()
        self.okButton = QPushButton("OK")
        self.cancelButton = QPushButton("Cancel")

        self.okButton.setFixedSize(80, 30)
        self.cancelButton.setFixedSize(80, 30)

        self.buttonLayout.addWidget(self.okButton)
        self.buttonLayout.addWidget(self.cancelButton)
        self.buttonLayout.setAlignment(Qt.AlignRight)
        self.mainLayout.addLayout(self.buttonLayout)

        self.okButton.clicked.connect(self.submitValues)
        self.cancelButton.clicked.connect(self.reject)

    def loadInputs(self):
        labels = {
            "name": "Name",
            "type": "Type",
            "chip": "Chip Name"
        }

        for key, value in self.default_values.items():
            layout = QHBoxLayout()
            label = QLabel(f"{labels[key]}:")
            layout.addWidget(label)

            line_edit = QLineEdit()
            line_edit.setPlaceholderText(f"{value}")  # 设置悬浮提示
            layout.addWidget(line_edit)

            self.lineEdits[key] = line_edit
            self.input_types[key] = type(value)
            self.mainLayout.addLayout(layout)

            # 安装事件过滤器以处理 Tab 键事件
            line_edit.installEventFilter(self)

    def eventFilter(self, source, event):
        """处理 Tab 键事件"""
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Tab:
            for key, line_edit in self.lineEdits.items():
                if line_edit.hasFocus():
                    # 如果输入框为空，则填充默认值
                    if line_edit.text().strip() == "":
                        line_edit.setText(line_edit.placeholderText())
                    # 跳转到下一个输入框
                    next_index = list(self.lineEdits.keys()).index(key) + 1
                    if next_index < len(self.lineEdits):
                        next_line_edit = self.lineEdits[list(self.lineEdits.keys())[next_index]]
                        next_line_edit.setFocus()
                    return True
        return super().eventFilter(source, event)

    def submitValues(self):
        options = Dict()  # 使用addict创建支持属性访问的字典
        valid_input = True

        for key, line_edit in self.lineEdits.items():
            value_str = line_edit.text().strip()
            expected_type = self.input_types[key]

            if not value_str:
                converted_value = self.default_values[key]
            else:
                try:
                    converted_value = expected_type(value_str)
                except ValueError as e:
                    QMessageBox.warning(self, "Invalid Input", f"Invalid input for {key}: {e}")
                    valid_input = False
                    break

            options[key] = converted_value  # 自动支持属性访问

        if valid_input:
            print("User input values:", options)
            self.design.gds.others.add(options)  # 确保此处add方法存在
            self.designUpdated.emit(self.design)
            self.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = Dialog_Others(design=Design())
    dialog.exec_()
    sys.exit(app.exec_())