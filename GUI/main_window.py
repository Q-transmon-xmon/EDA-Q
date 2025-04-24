import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from ui_components import MenuBar, ToolBar, ProjectManager, ImageTabs
from dialogs import *


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.design = Design()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("QEDA")
        self.setGeometry(100, 100, 800, 600)

        # Initialize each component
        self.menu_bar = MenuBar(self)
        self.tool_bar = ToolBar(self)
        self.image_tabs = ImageTabs(self)
        self.project_manager = ProjectManager(self)

        # Create main layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tool_bar)
        main_layout.addWidget(self.create_main_splitter())
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def create_main_splitter(self):
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.project_manager)
        splitter.addWidget(self.image_tabs)
        return splitter

    def update_design(self, new_design):
        self.design = new_design
        self.image_tabs.update_images()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())