import sys
import copy

from PySide6 import QtCore, QtGui
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QTreeWidget,
                               QTreeWidgetItem, QHBoxLayout, QVBoxLayout,
                               QLabel, QLineEdit, QScrollArea, QFormLayout, QPushButton)
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
        self.tree.setMinimumWidth(150)  # 设置左侧导航栏宽度
        self.tree.setFont(font)  # 设置导航栏字体

        # 设置左侧导航栏的背景颜色
        # self.tree.setStyleSheet("background-color: #f0f0f0;")

        # 创建右侧内容区域
        self.content_widget = QWidget()
        self.content_layout = QFormLayout(self.content_widget)
        self.content_layout.setVerticalSpacing(12)  # 设置输入框间距

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
        # 保持左侧导航栏宽度不变
        self.tree.setMinimumWidth(150)
        # 调整右侧内容区域的宽度,最大不超过中央窗口宽度减去150像素
        self.scroll.setMaximumWidth(self.central_widget.width() - 150)
        self.scroll.setMinimumWidth(300)

class Window_Gds(QtCore.QObject):
    # 定义一个信号用于设计更新
    designUpdated = QtCore.Signal(object)

    def __init__(self, design, tree, content_layout):
        super().__init__()
        self.design = design
        self.tree = tree
        self.content_layout = content_layout
        self.data = copy.deepcopy(design.options)

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
                if any(isinstance(v, dict) for v in value.values()):  # 如果还有嵌套字典
                    self.populate_tree(value, item)
                    item.setExpanded(True)  # 展开节点
                else:  # 如果是最后一层字典
                    self.display_dict(value, item)

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
        for key in path:
            if key in current_dict:
                current_dict = current_dict[key]

        self.display_dict(current_dict, item)

    def display_dict(self, dict_data, item):
        self.current_path = [item.text(0) for item in self.get_path(item)]  # 保存当前路径以供更新使用
        for key, value in dict_data.items():
            # 创建标签和输入框
            line_edit = QLineEdit(str(value))
            line_edit.setMinimumWidth(300)  # 设置输入框最小宽度
            line_edit.textChanged.connect(lambda text, k=key: self.update_value(k, text))
            self.content_layout.addRow(QLabel(key + ":"), line_edit)

        # 添加保存按钮
        if dict_data:  # 如果字典不为空
            save_button = QPushButton("保存")
            save_button.clicked.connect(self.save_changes)
            self.content_layout.addRow(QLabel(), save_button)
            self.content_layout.setAlignment(save_button, Qt.AlignRight)  # 将保存按钮放到右下角

    def get_path(self, item):
        path = []
        current = item
        while current:
            path.insert(0, current)
            current = current.parent()
        return path

    def update_value(self, key, new_value):
        # 更新数据
        current_dict = self.data
        for path_key in self.current_path[:-1]:  # 导航到正确的字典
            current_dict = current_dict[path_key]
        current_dict[key] = new_value

    def save_changes(self):
        # 发出设计更新信号
        # 更新原始设计对象
        self.design.inject_options(options=copy.deepcopy(self.data))
        self.designUpdated.emit(self.design)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    design = Design()
    design.generate_topology(qubits_num=16, topo_col=4)
    design.generate_qubits(chip_name='Chip_0', dist=2000, qubits_type='Xmon',
                           topo_positions=design.topology.positions)
    viewer = NestedDictViewer(design)
    viewer.window_gds.designUpdated.connect(lambda design: print("Design updated:", design))
    viewer.show()
    sys.exit(app.exec())