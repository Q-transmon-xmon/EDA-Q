import sys
from functools import partial
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout,
    QTreeWidget, QTreeWidgetItem, QMessageBox,
    QApplication, QMenu, QInputDialog
)
from api.design import Design
from .global_state import global_state  # Only import global_state

class DesignManager(QDockWidget):
    """Design Manager - Fully integrated with GlobalState"""
    design_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__("Design Manager", parent)
        self.design_data = {'children': {}}
        self.current_item = None

        self.init_ui()
        self.refresh_data()
        self.setMinimumWidth(320)
        sys.excepthook = self.handle_exception
        # Allow docking areas (key configuration)
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        # Enable floating and closing features
        self.setFeatures(
            self.DockWidgetMovable |
            self.DockWidgetClosable |
            self.DockWidgetFloatable  # Must include this
        )
        # Connect global state signals
        global_state.design_created.connect(self.refresh_data)
        global_state.design_renamed.connect(self.handle_design_renamed)
        global_state.design_removed.connect(lambda _: self.refresh_data())
        global_state.current_design_changed.connect(self.update_current_item_highlight)
        global_state.design_updated.connect(self.refresh_data)

    def init_ui(self):
        """Initialize UI components"""
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)  # ✅ Parent is central_widget
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setStyleSheet("""
            QTreeWidget { border: none; background: white; }
            QTreeWidget::item { height: 28px; }
        """)
        main_layout.addWidget(self.tree)

        self.setWidget(central_widget)  # ✅ Key correction

        self.tree.itemClicked.connect(self.handle_item_click)
        self.tree.itemDoubleClicked.connect(self.show_design_details)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)

    def refresh_data(self, _=None):
        """Unified full refresh method"""
        self.current_item = None
        self.design_data['children'].clear()

        # Directly get the latest design list from global_state
        for name in global_state.get_all_design_names():
            design = global_state.get_design(name)
            if design:  # Add None value protection
                self.design_data['children'][name] = self.convert_design_to_dict(design)

        # Rebuild the tree structure completely
        self.tree.clear()
        self.populate_tree()

        # Update the highlight display
        current_name = global_state.get_current_design_name()
        self.update_current_item_highlight(current_name)

    def _update_tree_item(self, design_name):
        """Update a single design node"""
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            if item.text(0) == design_name:
                self.tree.takeTopLevelItem(i)
                break
        new_item = QTreeWidgetItem(self.tree, [design_name])
        self.add_tree_children(new_item, self.design_data['children'][design_name]['children'])

    def convert_design_to_dict(self, design):
        """Convert design to nested dictionary structure"""
        def convert_node(obj):
            node = {'children': {}, 'is_leaf': False}
            if isinstance(obj, dict):
                for k, v in obj.items():
                    node['children'][k] = convert_node(v)
            elif hasattr(obj, '__dict__'):
                for attr, val in vars(obj).items():
                    if not attr.startswith('_') and val is not None:
                        node['children'][attr] = convert_node(val)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    node['children'][f"Item {i}"] = convert_node(item)
            else:
                node.update({'value': obj, 'is_leaf': True})
            return node
        return convert_node(design)

    def populate_tree(self):
        """Repaired tree construction method"""
        self.tree.clear()
        # Only display designs that exist in global_state
        valid_names = global_state.get_all_design_names()
        for design_name in list(self.design_data['children'].keys()):
            if design_name not in valid_names:
                del self.design_data['children'][design_name]

        # Rebuild all nodes
        for design_name, design_node in self.design_data['children'].items():
            top_item = QTreeWidgetItem(self.tree, [design_name])
            self.add_tree_children(top_item, design_node['children'])

    def add_tree_children(self, parent_item, children_dict):
        for key, node in children_dict.items():
            child_item = QTreeWidgetItem(parent_item, [key])
            if not node['is_leaf']:
                self.add_tree_children(child_item, node['children'])
            else:
                child_item.setText(1, str(node.get('value', '')))
                child_item.setData(1, Qt.UserRole, node.get('value'))

    def handle_item_click(self, item):
        """Handle item selection"""
        if item.parent() is None:
            design_name = item.text(0)
            try:
                global_state.update_current_design_name(design_name)
                self.design_selected.emit(design_name)
                self.highlight_item(item)
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))

    def highlight_item(self, item):
        """Highlight selected item"""
        if self.current_item:
            self.current_item.setForeground(0, QColor('black'))
            self.current_item.setFont(0, QFont())
        item.setForeground(0, QColor('blue'))
        item.setFont(0, QFont('Arial', 10, QFont.Bold))
        self.current_item = item

    def update_current_item_highlight(self, new_name):
        """Update highlight based on current design"""
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            if item.text(0) == new_name:
                self.highlight_item(item)
                break
        else:
            self.current_item = None

    def handle_design_renamed(self, old_name, new_name):
        """Handle design rename event"""
        self.refresh_data()
        if global_state.get_current_design_name() == new_name:
            self.update_current_item_highlight(new_name)

    def show_context_menu(self, pos):
        """Show context menu for design operations"""
        item = self.tree.itemAt(pos)
        menu = QMenu(self)

        if item and not item.parent():
            delete_action = menu.addAction("Delete Design")
            delete_action.triggered.connect(partial(self.delete_design, item))

            rename_action = menu.addAction("Rename Design")
            rename_action.triggered.connect(partial(self.rename_design, item))

        new_action = menu.addAction("New Design")
        new_action.triggered.connect(self.create_design)
        menu.exec_(self.tree.viewport().mapToGlobal(pos))

    # Add a confirmation dialog in the delete_design method
    def delete_design(self, item):
        """Add delete confirmation"""
        design_name = item.text(0)
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete the design '{design_name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                global_state.delete_design(design_name)
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def rename_design(self, item):
        """Rename design using GlobalState API"""
        old_name = item.text(0)
        new_name, ok = QInputDialog.getText(self, "Rename", "New name:", text=old_name)
        if ok and new_name != old_name:
            try:
                global_state.rename_design(old_name, new_name)
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))

    def create_design(self):
        """Create new design using GlobalState API"""
        name, ok = QInputDialog.getText(self, "New Design", "Design name:")
        if ok and name:
            try:
                global_state.create_design(name)
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))

    def show_design_details(self, item):
        """Show design details using GlobalState API"""
        if item.parent() is None:
            design_name = item.text(0)
            metadata = global_state.get_design_metadata(design_name)
            if metadata:
                details = f"Design: {design_name}\nPath: {metadata[1]}"
                QMessageBox.information(self, "Design Details", details)
        else:
            self.show_property_value(item)

    def show_property_value(self, item):
        """Show property value"""
        property_name = item.text(0)
        property_value = item.data(1, Qt.UserRole)
        QMessageBox.information(
            self, "Property Value",
            f"Property: {property_name}\nValue: {property_value}"
        )

    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """Handle uncaught exceptions"""
        QMessageBox.critical(
            self, "Error",
            f"Unhandled Exception:\nType: {exc_type}\nValue: {exc_value}"
        )
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    manager = DesignManager()
    manager.show()
    sys.exit(app.exec_())