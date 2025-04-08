import sys
import copy
import numpy as np

from PySide6 import QtCore, QtGui
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QTreeWidget,
                               QTreeWidgetItem, QHBoxLayout, QVBoxLayout,
                               QLabel, QLineEdit, QScrollArea, QFormLayout, QPushButton,
                               QMessageBox)
from PySide6.QtCore import Qt
from api.design import Design


class NestedDictViewer(QMainWindow):
    def __init__(self, design):
        super().__init__()
        self.setWindowTitle("GDS版图修改")
        self.setGeometry(100, 100, 800, 600)

        # 设置整个界面的字体
        font = QtGui.QFont("Microsoft YaHei", 10)
        self.setFont(font)

        # 创建主窗口部件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # 创建水平布局
        self.layout = QHBoxLayout(self.central_widget)

        # 创建树形控件
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Design")
        self.tree.setMinimumWidth(150)
        self.tree.setFont(font)

        # 创建右侧内容区域
        self.content_widget = QWidget()
        self.content_layout = QFormLayout(self.content_widget)
        self.content_layout.setVerticalSpacing(12)

        # 创建滚动区域
        self.scroll = QScrollArea()
        self.scroll.setWidget(self.content_widget)
        self.scroll.setWidgetResizable(True)

        # 添加部件到布局
        self.layout.addWidget(self.tree)
        self.layout.addWidget(self.scroll)

        # 创建 Window_Gds 实例
        self.window_gds = Window_Gds(design, self.tree, self.content_layout)

        # 连接窗口大小变化信号
        self.central_widget.resizeEvent = self.on_resize

    def on_resize(self, event):
        self.tree.setMinimumWidth(150)
        self.scroll.setMaximumWidth(self.central_widget.width() - 150)
        self.scroll.setMinimumWidth(300)


class Window_Gds(QtCore.QObject):
    designUpdated = QtCore.Signal(object)

    def __init__(self, design, tree, content_layout):
        super().__init__()
        self.design = design
        self.tree = tree
        self.content_layout = content_layout
        self.data = copy.deepcopy(design.options)
        self.current_item = None
        self.original_values = {}  # 存储原始值和类型信息

        # 填充树形控件
        self.populate_tree(self.data)

        # 连接信号
        self.tree.itemClicked.connect(self.on_item_clicked)

    def populate_tree(self, data, parent=None):
        for key, value in data.items():
            if parent is None:
                item = QTreeWidgetItem(self.tree)
            else:
                item = QTreeWidgetItem(parent)

            item.setText(0, str(key))
            if isinstance(value, dict):
                if any(isinstance(v, dict) for v in value.values()):
                    self.populate_tree(value, item)
                    item.setExpanded(True)
                else:
                    self.display_dict(value, item)

    def on_item_clicked(self, item, column):
        self.current_item = item
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
        for key in path:
            if key in current_dict:
                current_dict = current_dict[key]

        self.display_dict(current_dict, item)

    def display_dict(self, dict_data, item):
        if not isinstance(dict_data, dict):
            return

        self.current_path = [item.text(0) for item in self.get_path(item)]
        for key, value in dict_data.items():
            if isinstance(value, dict):
                continue

            # 存储原始值和类型信息
            path_key = '.'.join(self.current_path + [str(key)])
            self.original_values[path_key] = {
                'value': value,
                'type': type(value),
                'is_numpy': isinstance(value, np.ndarray)
            }

            # 创建标签和输入框
            line_edit = QLineEdit(str(value))
            line_edit.setMinimumWidth(300)
            line_edit.setProperty("path_key", path_key)
            line_edit.textChanged.connect(self.on_text_changed)
            self.content_layout.addRow(QLabel(f"{key} ({type(value).__name__}):"), line_edit)

        # 添加保存按钮
        if dict_data:
            save_button = QPushButton("保存")
            save_button.clicked.connect(self.save_changes)
            self.content_layout.addRow(QLabel(), save_button)
            self.content_layout.setAlignment(save_button, Qt.AlignRight)

    def get_path(self, item):
        path = []
        current = item
        while current:
            path.insert(0, current)
            current = current.parent()
        return path

    def parse_value(self, text, original_info):
        """根据原始类型解析输入值"""
        try:
            if original_info['is_numpy']:
                # 处理numpy数组
                try:
                    # 尝试评估字符串为Python表达式
                    value = eval(text)
                    return np.array(value, dtype=original_info['value'].dtype)
                except:
                    return original_info['value']  # 保持原值
            elif original_info['type'] == bool:
                return text.lower() in ('true', '1', 'yes', 'y', 't')
            elif original_info['type'] == int:
                return int(float(text))  # 允许输入小数点，但转换为整数
            elif original_info['type'] == float:
                return float(text)
            elif original_info['type'] == str:
                return text
            else:
                # 对于其他类型，尝试使用eval
                try:
                    return eval(text)
                except:
                    return text
        except:
            return None

    def on_text_changed(self, text):
        line_edit = self.sender()
        path_key = line_edit.property("path_key")
        original_info = self.original_values.get(path_key)

        if not original_info:
            return

        # 解析新值
        new_value = self.parse_value(text, original_info)

        if new_value is not None:
            # 更新数据
            current_dict = self.data
            path_parts = path_key.split('.')
            for part in path_parts[:-1]:
                current_dict = current_dict[part]
            current_dict[path_parts[-1]] = new_value
            line_edit.setStyleSheet("")
        else:
            # 解析失败时设置红色边框
            line_edit.setStyleSheet("border: 1px solid red;")

    def save_changes(self):
        try:
            # 更新原始设计对象
            self.design.inject_options(self.data)
            # 发出更新信号
            self.designUpdated.emit(self.design)

            if self.current_item:
                self.on_item_clicked(self.current_item, 0)

            # 显示成功消息
            QMessageBox.information(None, "成功", "更改已保存")
        except Exception as e:
            QMessageBox.critical(None, "错误", f"保存失败: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    design = Design()
    design.generate_topology(qubits_num=16, topo_col=4)
    design.generate_qubits(chip_name='Chip_0', dist=2000, qubits_type='Xmon',
                           topo_positions=design.topology.positions)
    viewer = NestedDictViewer(design)


    def updateMainDesign(updated_design):
        design = updated_design
        design.topology.show_image()
        print("主窗口设计已更新")


    viewer.window_gds.designUpdated.connect(updateMainDesign)
    viewer.show()

    sys.exit(app.exec())