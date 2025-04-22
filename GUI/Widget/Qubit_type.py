import sys
from PySide6 import QtCore
from PySide6.QtWidgets import QApplication, QDialog, QHBoxLayout, QPushButton, QVBoxLayout
from api.design import Design

class SelectionDialog(QDialog):
    designUpdated = QtCore.Signal(object)

    def __init__(self, design):
        super().__init__()
        self.design = design
        self.setWindowTitle("选择量子比特类型")
        self.setGeometry(100, 100, 300, 100)  # 设置窗口大小和初始位置

        # 创建主垂直布局
        main_layout = QVBoxLayout()

        # 创建水平布局
        button_layout = QHBoxLayout()

        # 创建按钮
        self.xmon_button = QPushButton("Xmon")
        self.transmon_button = QPushButton("Transmon")

        # 设置按钮样式为方框型
        self.xmon_button.setStyleSheet("border: 2px solid black; border-radius: 0px; padding: 10px;")
        self.transmon_button.setStyleSheet("border: 2px solid black; border-radius: 0px; padding: 10px;")

        # 连接按钮点击事件
        self.xmon_button.clicked.connect(self.select_xmon)
        self.transmon_button.clicked.connect(self.select_transmon)

        # 将按钮添加到水平布局
        button_layout.addWidget(self.xmon_button)
        button_layout.addWidget(self.transmon_button)

        # 将水平布局添加到主布局
        main_layout.addLayout(button_layout)

        # 设置主布局
        self.setLayout(main_layout)

        # 设置窗口显示位置
        self.move(400, 400)  # 设置窗口左上角位置为 (200, 200)

    def select_xmon(self):
        print("您选择了 Xmon")
        self.design.generate_qubits(topology=True, qubits_type='Xmon')
        self.designUpdated.emit(self.design)  # 发出设计更新信号
        self.accept()  # 关闭对话框

    def select_transmon(self):
        print("您选择了 Transmon")
        self.design.generate_qubits(topology=True, qubits_type='Transmon')
        self.designUpdated.emit(self.design)
        self.accept()  # 关闭对话框

if __name__ == "__main__":
    app = QApplication(sys.argv)
    design = Design()  # 创建 Design 实例
    dialog = SelectionDialog(design)  # 将 design 实例传递给 SelectionDialog
    dialog.exec()