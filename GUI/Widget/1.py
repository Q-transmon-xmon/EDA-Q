import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMenuBar, QToolBar,
    QAction, QStatusBar, QWidget, QVBoxLayout, QLabel, QFrame, QListWidget, QSplitter
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("EDA 工具")
        self.setGeometry(100, 100, 1200, 800)

        # 创建菜单栏
        self.menu_bar = self.create_menu_bar()
        self.setMenuBar(self.menu_bar)

        # 创建工具栏
        self.tool_bar = self.create_tool_bar()
        self.addToolBar(self.tool_bar)

        # 设置中央小部件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()

        # 创建一个分割器来放置左侧的项目管理器和右侧的主要工作区域
        splitter = QSplitter()

        # 项目管理器
        self.project_manager = QListWidget()
        self.project_manager.addItems(["Project1", "Project2", "Project3"])
        splitter.addWidget(self.project_manager)

        # 主工作区
        self.main_frame = QFrame()
        self.main_frame.setStyleSheet("background-color: lightgrey;")
        splitter.addWidget(self.main_frame)

        self.layout.addWidget(splitter)
        self.central_widget.setLayout(self.layout)

        # 属性面板
        self.properties_widget = QListWidget()
        self.properties_widget.addItems(["Name", "Value", "Unit", "Evaluation"])
        self.layout.addWidget(self.properties_widget)

        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def create_menu_bar(self):
        menu_bar = QMenuBar()

        # 文件菜单
        file_menu = menu_bar.addMenu("文件")
        new_action = QAction("新建", self)
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        open_action = QAction("打开", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction("保存", self)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        # 编辑菜单
        edit_menu = menu_bar.addMenu("编辑")
        undo_action = QAction("撤销", self)
        edit_menu.addAction(undo_action)

        return menu_bar

    def create_tool_bar(self):
        tool_bar = QToolBar("工具栏")

        run_action = QAction("运行", self)
        run_action.triggered.connect(self.run_simulation)
        tool_bar.addAction(run_action)

        stop_action = QAction("停止", self)
        stop_action.triggered.connect(self.stop_simulation)
        tool_bar.addAction(stop_action)

        return tool_bar

    def new_file(self):
        print("新建文件")

    def open_file(self):
        print("打开文件")

    def save_file(self):
        print("保存文件")

    def run_simulation(self):
        print("运行仿真")

    def stop_simulation(self):
        print("停止仿真")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())