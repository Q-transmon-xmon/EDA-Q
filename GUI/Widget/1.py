import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMenuBar, QToolBar,
    QAction, QStatusBar, QWidget, QVBoxLayout, QLabel, QFrame, QListWidget, QSplitter
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("EDA Tool")
        self.setGeometry(100, 100, 1200, 800)

        # Create a menu bar
        self.menu_bar = self.create_menu_bar()
        self.setMenuBar(self.menu_bar)

        # Create toolbar
        self.tool_bar = self.create_tool_bar()
        self.addToolBar(self.tool_bar)

        # Set central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()

        # Create a splitter to place the project manager on the left and the main workspace on the right
        splitter = QSplitter()

        # Project manager
        self.project_manager = QListWidget()
        self.project_manager.addItems(["Project1", "Project2", "Project3"])
        splitter.addWidget(self.project_manager)

        # Main workspace
        self.main_frame = QFrame()
        self.main_frame.setStyleSheet("background-color: lightgrey;")
        splitter.addWidget(self.main_frame)

        self.layout.addWidget(splitter)
        self.central_widget.setLayout(self.layout)

        # Attribute Panel
        self.properties_widget = QListWidget()
        self.properties_widget.addItems(["Name", "Value", "Unit", "Evaluation"])
        self.layout.addWidget(self.properties_widget)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def create_menu_bar(self):
        menu_bar = QMenuBar()

        # FILE
        file_menu = menu_bar.addMenu("File")
        new_action = QAction("New", self)
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        # EDIT
        edit_menu = menu_bar.addMenu("Edit")
        undo_action = QAction("Undo", self)
        edit_menu.addAction(undo_action)

        return menu_bar

    def create_tool_bar(self):
        tool_bar = QToolBar("Toolbar")

        run_action = QAction("Run", self)
        run_action.triggered.connect(self.run_simulation)
        tool_bar.addAction(run_action)

        stop_action = QAction("Stop", self)
        stop_action.triggered.connect(self.stop_simulation)
        tool_bar.addAction(stop_action)

        return tool_bar

    def new_file(self):
        print("New file")

    def open_file(self):
        print("Open file")

    def save_file(self):
        print("Save file")

    def run_simulation(self):
        print("Run simulation")

    def stop_simulation(self):
        print("Stop simulation")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())