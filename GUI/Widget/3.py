import sys
from copy import copy

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QTreeWidget,
                               QTreeWidgetItem, QHBoxLayout, QVBoxLayout,
                               QLabel, QLineEdit, QScrollArea, QFormLayout)
from PySide6.QtCore import Qt
from api.design import Design

class MainWindow(QMainWindow):
    def __init__(self,design):
        super().__init__()
        self.design = design
        self.setWindowTitle("嵌套字典查看器")
        self.setGeometry(100, 100, 800, 600)
        design_ops = copy().deepcopy(design.options)
        # 示例数据
        self.data = {
            "设备1": {
                "通道1": {
                    "qubits": {
                        "频率": "5.5 GHz",
                        "相位": "0.5 rad",
                        "幅度": "0.8"
                    }
                },
                "通道2": {
                    "qubits": {
                        "频率": "4.8 GHz",
                        "相位": "0.3 rad",
                        "幅度": "0.7"
                    }
                }
            },
            "设备2": {
                "通道1": {
                    "qubits": {
                        "频率": "6.0 GHz",
                        "相位": "0.4 rad",
                        "幅度": "0.9"
                    }
                }
            }
        }

        # 创建主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建水平布局
        layout = QHBoxLayout(central_widget)

        # 创建树形控件
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("导航")
        self.tree.setMinimumWidth(200)
        self.tree.itemClicked.connect(self.on_item_clicked)

        # 创建右侧内容区域
        self.content_widget = QWidget()
        self.content_layout = QFormLayout(self.content_widget)

        # 创建滚动区域
        scroll = QScrollArea()
        scroll.setWidget(self.content_widget)
        scroll.setWidgetResizable(True)

        # 添加部件到布局
        layout.addWidget(self.tree)
        layout.addWidget(scroll)

        # 填充树形控件
        self.populate_tree(self.data)

    def populate_tree(self, data, parent=None):
        for key, value in data.items():
            if parent is None:
                item = QTreeWidgetItem(self.tree)
            else:
                item = QTreeWidgetItem(parent)

            item.setText(0, str(key))
            if isinstance(value, dict):
                self.populate_tree(value, item)

    def on_item_clicked(self, item, column):
        # 清除右侧内容
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # 获取完整路径
        path = []
        current = item
        while current:
            path.insert(0, current.text(0))
            current = current.parent()

        # 查找对应的字典
        current_dict = self.data
        for key in path[:-1]:  # 除了最后一个键
            if key in current_dict:
                current_dict = current_dict[key]

        # 如果最后一个项是 qubits，显示其键值对
        if path[-1] == "qubits":
            qubits_dict = current_dict["qubits"]
            self.display_qubits(qubits_dict, path)

    def display_qubits(self, qubits_dict, path):
        self.current_path = path  # 保存当前路径以供更新使用
        for key, value in qubits_dict.items():
            # 创建标签和输入框
            line_edit = QLineEdit(str(value))
            line_edit.textChanged.connect(lambda text, k=key: self.update_value(k, text))
            self.content_layout.addRow(QLabel(key + ":"), line_edit)

    def update_value(self, key, new_value):
        # 更新数据
        current_dict = self.data
        for path_key in self.current_path[:-1]:  # 导航到正确的字典
            current_dict = current_dict[path_key]
        current_dict["qubits"][key] = new_value


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())