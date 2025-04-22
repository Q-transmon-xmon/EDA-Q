import sys
import os

# 获取当前脚本所在的目录
current_path = os.path.dirname(os.path.abspath(__file__))
GUI_PATH = os.path.dirname(current_path)
PROJ_PATH = os.path.dirname(GUI_PATH)

# 添加路径
sys.path.append(GUI_PATH)
sys.path.append(PROJ_PATH)

from functools import partial
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout,
    QTreeWidget, QTreeWidgetItem, QMessageBox,
    QApplication, QMenu, QInputDialog, QPushButton, QMainWindow
)
from api.design import Design  # 确保引用 Design


class DesignManager(QDockWidget):
    """设计管理器类。"""
    component_clicked = pyqtSignal(str)

    def __init__(self, design, parent=None):
        super().__init__("Design Manager", parent)
        self.setFeatures(
            QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetClosable)
        self.design = design  # 存储原始Design对象引用
        self.Design_data = {'children': {}}

        # 初始化数据
        self.refresh_data()

        if self.Design_data['children']:
            self.current_Design = next(iter(self.Design_data['children'].keys()))
        else:
            self.current_Design = 'No Design Selected'
        self.current_path = []

        self.is_pinned = False
        self.init_ui()
        self.setMinimumWidth(320)

    def init_ui(self):
        """初始化界面布局"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self._create_design_tree()
        main_layout.addWidget(self.tree)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setWidget(central_widget)

        self.tree.itemClicked.connect(self._update_selected_design)
        self.tree.itemDoubleClicked.connect(self._show_design_details)

        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._show_context_menu)

    def refresh_data(self):
        """从Design对象刷新数据"""
        self.Design_data['children'].clear()
        if self.design is not None:
            design_dict = self._convert_design_to_dict()
            self.Design_data['children'].update(design_dict)

    def update_display(self):
        """更新界面显示"""
        self._populate_tree()

    def _convert_design_to_dict(self):
        """将Design对象递归转换为完整嵌套字典结构"""

        def convert(obj):
            node = {'children': {}, 'is_leaf': False}  # 新增 is_leaf 标识
            if isinstance(obj, dict):
                for k, v in obj.items():
                    node['children'][k] = convert(v)
            elif hasattr(obj, '__dict__'):
                for attr_name, attr_value in vars(obj).items():
                    if attr_name.startswith('_'):
                        continue
                    node['children'][attr_name] = convert(attr_value)
                node['is_leaf'] = False  # 非叶节点
            elif isinstance(obj, list):
                for index, value in enumerate(obj):
                    node['children'][f"Item {index}"] = convert(value)
                node['is_leaf'] = False  # 非叶节点
            else:
                node['value'] = obj  # 叶节点的值
                node['is_leaf'] = True  # 叶节点
            return node

        return {self.design.__class__.__name__: convert(self.design)}

    def _create_design_tree(self):
        """创建项目树组件"""
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setStyleSheet("""  
            QTreeWidget {  
                border: none;  
                background: white;  
            }  
            QTreeWidget::item {  
                height: 28px;  
            }  
        """)
        self._populate_tree()

    def _populate_tree(self):
        """填充树结构并处理显示逻辑"""
        self.tree.clear()
        root = self.tree.invisibleRootItem()

        def populate_items(parent_item, data):
            for name, details in data['children'].items():
                item_text = name
                item = QTreeWidgetItem(parent_item, [item_text])
                populate_items(item, details)

                # 根据子节点类型设置 item 是否展开
                if details.get('is_leaf', False):
                    item.setData(0, Qt.UserRole, {'name': name, 'is_leaf': True, 'value': details['value']})
                else:
                    item.setData(0, Qt.UserRole, {'name': name, 'is_leaf': False})  # 设置非叶节点信息

        populate_items(root, self.Design_data)  # 填充树结构

    def update_design(self, new_design=None):
        """更新管理的Design对象并刷新显示"""
        if new_design is not None:
            self.design = new_design
        self.refresh_data()
        self.update_display()

    def _update_selected_design(self, item):
        """更新选中的设计项目路径"""
        path = []
        current = item
        while current:
            path.insert(0, current.text(0))
            current = current.parent()

        self.current_path = path
        self.current_Design = " → ".join(path) if path else "No Design Selected"

    def _show_design_details(self, item):
        """双击查看设计详细信息"""
        if item:
            item_data = item.data(0, Qt.UserRole)
            if item_data:
                if item_data['is_leaf']:  # 判断是否为叶节点
                    QMessageBox.information(self, "Design Details", f"Value: {item_data['value']}", QMessageBox.Ok)
                else:
                    QMessageBox.information(self, "Design Details", "This is a non-leaf node.", QMessageBox.Ok)

    def close_manager(self):
        """关闭设计管理器面板"""
        self.setVisible(False)

    def add_item(self, parent_item, name):
        """添加项目"""
        if name in self.Design_data['children']:
            QMessageBox.warning(self, "Duplicate Name", f"Design '{name}' already exists!")
            return
        self.Design_data['children'][name] = {'children': {}}
        self._populate_tree()
        self.current_Design = name

    def delete_item(self, item):
        """删除项目"""
        if item is None:
            QMessageBox.warning(self, "Error", "No item selected!")
            return

        path = self._get_item_path(item)
        confirm = QMessageBox.question(
            self, "Confirm Delete", f"Delete '{path[-1]}' and all its children?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            parent_data = self._navigate_to_path(path[:-1])
            del parent_data['children'][path[-1]]
            (item.parent() or self.tree.invisibleRootItem()).removeChild(item)
            if len(path) > 0 and path[0] == self.current_Design:
                self.current_Design = "No Design Selected"

    def _show_context_menu(self, pos):
        """显示右键菜单"""
        item = self.tree.itemAt(pos)
        menu = QMenu(self)

        if item:
            # 添加删除设计选项
            delete_action = menu.addAction("Delete Design")
            delete_action.triggered.connect(partial(self.delete_item, item))

            # 添加新建设计选项
        new_action = menu.addAction("New Design")
        new_action.triggered.connect(self.new_design)

        menu.exec_(self.tree.viewport().mapToGlobal(pos))

    def new_design(self):
        """新建设计"""
        text, ok = QInputDialog.getText(self, "New Design", "Enter design name:")
        if ok and text:
            self.add_item(self.tree.invisibleRootItem(), text)

    def _navigate_to_path(self, path):
        """导航到指定路径的数据节点"""
        current = self.Design_data
        for level in path:
            current = current['children'].get(level, {'children': {}})
        return current

    def _get_item_path(self, item):
        """获取树节点的完整路径"""
        path = []
        while item is not None:
            path.insert(0, item.text(0))
            item = item.parent()
        return path


class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.design_manager = DesignManager(Design())  # 示例：实际应该用你的设计对象

    def updateMainDesign(self, updated_design):
        """更新主设计内容并刷新显示"""
        # 更新设计对象
        self.design = updated_design

        # 更新 DesignManager 中的设计对象并刷新界面
        self.design_manager.update_design(updated_design)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))

    main_window = MyMainWindow()
    main_window.show()
    sys.exit(app.exec_())