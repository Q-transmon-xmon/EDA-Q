import sys
from PyQt5 import QtCore
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QApplication, QDialog, QHBoxLayout, QVBoxLayout,
                             QLabel, QSizePolicy, QSpacerItem, QMessageBox, QComboBox, QDialogButtonBox)

from GUI.gui_modules.design_validator import design_validator
from api.design import Design

# 新增导入
import toolbox
from library.qubits import module_name_list

class Dialog_Selection(QDialog):
    designUpdated = QtCore.pyqtSignal(object)

    def __init__(self, design):
        super().__init__()

        self.design = design
        self.setWindowTitle("Select Qubit Type")
        self.setGeometry(100, 100, 400, 250)  # Set window size and initial position

        # 设置字体
        font = QFont("Arial", 10)
        self.setFont(font)

        # 创建主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 40, 20, 20)

        # 标题标签
        title_label = QLabel("Please select the type of qubit you want to generate:")
        title_label.setStyleSheet("font-size: 22px; font-weight: bold; color: black;")
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        title_label.setWordWrap(True)
        main_layout.addWidget(title_label)

        # 添加固定间隔
        main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # 创建下拉框布局
        combo_layout = QHBoxLayout()

        # 生成动态选项列表
        try:
            # 转换为驼峰命名
            class_names = [toolbox.convert_to_camel_case(name) for name in module_name_list]
            # 过滤无效值并确保非空
            valid_names = [name for name in class_names if isinstance(name, str) and name]
            if not valid_names:
                valid_names = ["DefaultQubitType"]
        except Exception as e:
            print(f"Error generating options: {str(e)}")
            valid_names = ["Xmon", "Transmon"]  # 备选选项

        # 创建下拉框
        self.type_combo = QComboBox()
        self.type_combo.addItems(valid_names)
        self.type_combo.setFixedWidth(250)  # 设置固定宽度为250px
        self.type_combo.setFixedHeight(25)  # 设置固定高度为40px
        # 将下拉框居中
        combo_layout.addStretch(1)
        combo_layout.addWidget(self.type_combo)
        combo_layout.addStretch(1)

        # 添加到主布局
        main_layout.addLayout(combo_layout)

        # 添加底部间隔
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # 添加按钮框
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.on_confirm)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

        self.setLayout(main_layout)
        self.move(400, 400)

    def on_confirm(self):
        """处理确认按钮点击事件"""
        selected_type = self.type_combo.currentText()
        print(f"You selected: {selected_type}")

        # 检查topology是否存在
        if design_validator.is_component_empty(self.design, 'topology'):
            QMessageBox.warning(self, "Warning", "Topology does not exist or is not initialized.")
            return

        try:
            # 生成量子比特
            self.design.generate_qubits(
                topology=True,
                qubits_type=selected_type
            )
            self.designUpdated.emit(self.design)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate qubits: {str(e)}")
            self.reject()

    def on_qubit_selected(self):
        """处理下拉框选项变化事件"""
        selected_type = self.type_combo.currentText()
        print(f"You selected: {selected_type}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    design = Design()
    dialog = Dialog_Selection(design)
    dialog.exec_()