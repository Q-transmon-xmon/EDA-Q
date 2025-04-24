import sys
import os

# Retrieve the directory where the current script is located
current_path = os.path.dirname(os.path.abspath(__file__))
GUI_PATH = os.path.dirname(current_path)
PROJ_PATH = os.path.dirname(GUI_PATH)

# Add path
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
from api.design import Design  # Ensure citation Design


class DesignManager(QDockWidget):
    """Design Manager Class。"""
    component_clicked = pyqtSignal(str)

    def __init__(self, design, parent=None):
        super().__init__("Design Manager", parent)
        self.setFeatures(
            QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetClosable)
        self.design = design  # Store original dataDesignobject reference
        self.Design_data = {'children': {}}

        # Initialized Data
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
        """Initialize interface layout"""
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
        """followDesignObject refresh data"""
        self.Design_data['children'].clear()
        if self.design is not None:
            design_dict = self._convert_design_to_dict()
            self.Design_data['children'].update(design_dict)

    def update_display(self):
        """Update interface display"""
        self._populate_tree()

    def _convert_design_to_dict(self):
        """supportDesignRecursive conversion of objects to a fully nested dictionary structure"""

        def convert(obj):
            node = {'children': {}, 'is_leaf': False}  # newly added is_leaf sign
            if isinstance(obj, dict):
                for k, v in obj.items():
                    node['children'][k] = convert(v)
            elif hasattr(obj, '__dict__'):
                for attr_name, attr_value in vars(obj).items():
                    if attr_name.startswith('_'):
                        continue
                    node['children'][attr_name] = convert(attr_value)
                node['is_leaf'] = False  # Non leaf node
            elif isinstance(obj, list):
                for index, value in enumerate(obj):
                    node['children'][f"Item {index}"] = convert(value)
                node['is_leaf'] = False  # Non leaf node
            else:
                node['value'] = obj  # The value of leaf nodes
                node['is_leaf'] = True  # leaf node
            return node

        return {self.design.__class__.__name__: convert(self.design)}

    def _create_design_tree(self):
        """Create project tree components"""
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
        """Fill the tree structure and process the display logic"""
        self.tree.clear()
        root = self.tree.invisibleRootItem()

        def populate_items(parent_item, data):
            for name, details in data['children'].items():
                item_text = name
                item = QTreeWidgetItem(parent_item, [item_text])
                populate_items(item, details)

                # Set according to the type of child node item Expand or not
                if details.get('is_leaf', False):
                    item.setData(0, Qt.UserRole, {'name': name, 'is_leaf': True, 'value': details['value']})
                else:
                    item.setData(0, Qt.UserRole, {'name': name, 'is_leaf': False})  # Set non leaf node information

        populate_items(root, self.Design_data)  # Fill tree structure

    def update_design(self, new_design=None):
        """Update ManagementDesignObject and refresh display"""
        if new_design is not None:
            self.design = new_design
        self.refresh_data()
        self.update_display()

    def _update_selected_design(self, item):
        """Update the selected design project path"""
        path = []
        current = item
        while current:
            path.insert(0, current.text(0))
            current = current.parent()

        self.current_path = path
        self.current_Design = " → ".join(path) if path else "No Design Selected"

    def _show_design_details(self, item):
        """Double click to view design details"""
        if item:
            item_data = item.data(0, Qt.UserRole)
            if item_data:
                if item_data['is_leaf']:  # Determine whether it is a leaf node
                    QMessageBox.information(self, "Design Details", f"Value: {item_data['value']}", QMessageBox.Ok)
                else:
                    QMessageBox.information(self, "Design Details", "This is a non-leaf node.", QMessageBox.Ok)

    def close_manager(self):
        """Close the Design Manager panel"""
        self.setVisible(False)

    def add_item(self, parent_item, name):
        """add item"""
        if name in self.Design_data['children']:
            QMessageBox.warning(self, "Duplicate Name", f"Design '{name}' already exists!")
            return
        self.Design_data['children'][name] = {'children': {}}
        self._populate_tree()
        self.current_Design = name

    def delete_item(self, item):
        """delete item"""
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
        """Display right-click menu"""
        item = self.tree.itemAt(pos)
        menu = QMenu(self)

        if item:
            # Add and delete design options
            delete_action = menu.addAction("Delete Design")
            delete_action.triggered.connect(partial(self.delete_item, item))

            # Add New Design Options
        new_action = menu.addAction("New Design")
        new_action.triggered.connect(self.new_design)

        menu.exec_(self.tree.viewport().mapToGlobal(pos))

    def new_design(self):
        """new design"""
        text, ok = QInputDialog.getText(self, "New Design", "Enter design name:")
        if ok and text:
            self.add_item(self.tree.invisibleRootItem(), text)

    def _navigate_to_path(self, path):
        """Navigate to the data node of the specified path"""
        current = self.Design_data
        for level in path:
            current = current['children'].get(level, {'children': {}})
        return current

    def _get_item_path(self, item):
        """Obtain the complete path of the tree node"""
        path = []
        while item is not None:
            path.insert(0, item.text(0))
            item = item.parent()
        return path


class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.design_manager = DesignManager(Design())  # Example：Actually, we should use your design object

    def updateMainDesign(self, updated_design):
        """Update the main design content and refresh the display"""
        # Update design object
        self.design = updated_design

        # update DesignManager Design objects in and refresh the interface
        self.design_manager.update_design(updated_design)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))

    main_window = MyMainWindow()
    main_window.show()
    sys.exit(app.exec_())