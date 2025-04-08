import sys
import os
import logging

# 获取当前脚本所在的目录
current_path = os.path.dirname(os.path.abspath(__file__))
GUI_PATH = os.path.dirname(current_path)
PROJ_PATH = os.path.dirname(GUI_PATH)

# 添加路径
sys.path.append(GUI_PATH)
sys.path.append(PROJ_PATH)

from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout,
    QWidget, QSplitter
)
from PyQt5.QtCore import Qt
from api.design import Design
from GUI_3_4_6.gui_modules import DesignManager, MenuBarManager, ComponentLibrary, ToolBarManager
from GUI_3_4_6.gui_modules.display_area import DisplayArea
from GUI_3_4_6.gui_modules.styles import set_stylesheet
from GUI_3_4_6.gui_modules.Design_options import DesignOptions
from GUI_3_4_6.gui_modules.global_state import global_state  # 导入全局状态管理器

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class MyMainWindow(QMainWindow):
    """主窗口类，负责应用程序的主界面和逻辑。"""

    def __init__(self):
        super(MyMainWindow, self).__init__()
        self.node_dialog = None

        # 创建初始设计并通过 GlobalState 管理
        initial_design = Design()
        # 使用 create_design 方法代替直接操作 global_designs
        global_state.create_design("Initial Design", path=None)
        global_state.update_design("Initial Design", initial_design)

        # 初始化设计操作对象
        self.design_options = DesignOptions(self)

        # 设置窗口图标
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../icons/logo/logo_2.png")
        self.setWindowIcon(QIcon(icon_path))

        # 初始化DesignManager和组件库
        self.design_manager = DesignManager(parent=self)
        self.component_library = ComponentLibrary(self)

        # 连接信号
        global_state.current_design_changed.connect(self._handle_design_change)
        global_state.design_updated.connect(self._update_main_design)

        # 初始化用户界面
        self.init_ui()

        # 初始化菜单栏管理器
        self.menu_manager = MenuBarManager(parent=self)
        self.setMenuBar(self.menu_manager.menu_bar)

    def init_ui(self):
        """初始化用户界面，包括窗口标题、布局、工具栏和样式设置。"""
        self.setWindowTitle("EDA-Q")
        self.setup_window_geometry()
        self.setup_main_layout()
        self.setup_toolbar()
        self.setup_splitter()
        set_stylesheet(self)

    def setup_window_geometry(self):
        """设置窗口大小和位置。"""
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        window_width = int(screen_geometry.width() * 0.8)
        window_height = int(screen_geometry.height() * 0.8)
        self.resize(window_width, window_height)
        self.move(
            int((screen_geometry.width() - window_width) / 2),
            int((screen_geometry.height() - window_height) / 2)
        )

    def setup_main_layout(self):
        """设置主布局。"""
        self.main_layout = QVBoxLayout()
        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)

    def setup_toolbar(self):
        """设置工具栏。"""
        self.toolbar_manager = ToolBarManager(self)
        self.addToolBar(self.toolbar_manager)

    def setup_splitter(self):
        """设置分割器，包含设计管理器和显示区域。"""
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

        left_splitter = QSplitter(Qt.Vertical)
        left_splitter.addWidget(self.design_manager)
        left_splitter.addWidget(self.component_library)

        self.display_area = DisplayArea(main_window=self)
        splitter.addWidget(left_splitter)
        splitter.addWidget(self.display_area)

        self.main_layout.addWidget(splitter)
        splitter.setSizes([250, 800])

    def _handle_design_change(self, design_name: str) -> None:
        """处理全局设计变更事件"""
        if design_name:
            self._update_main_design()

    def _update_main_design(self):
        """通过 GlobalState 获取当前设计实例"""
        current_name = global_state.get_current_design_name()  # 使用封装的获取方法
        design_instance = global_state.get_design(current_name)  # 通过接口获取设计实例

        if design_instance:
            # 更新组件库的当前设计
            # self.component_library.set_current_design(design_instance)
            # 更新显示区域
            self._update_display_area(design_instance)
        else:
            logging.warning(f"当前设计 '{current_name}' 不存在")

    def _update_display_area(self, design_instance: Design) -> None:
        """更新显示区域内容"""
        try:
            # 保存并显示拓扑图
            design_instance.topology.save_image(path='./picture/topology.png')
            self.display_area.topo_tab.show_image('./picture/topology.png', show=True)

            # 保存并显示GDS图像
            design_instance.gds.save_svg(path='./picture/gds.svg')
            self.display_area.gds_tab.show_image('./picture/gds.svg', show=True)
        except Exception as e:
            logging.error(f"显示图像失败: {e}")

    def update_design_instance(self, design_name: str, updated_design: Design) -> None:
        """通过 GlobalState 更新设计实例"""
        if global_state.design_exists(design_name):  # 使用封装的检查方法
            global_state.update_design(design_name, updated_design)
            logging.info(f"设计 '{design_name}' 已更新。")
        else:
            logging.warning(f"设计 '{design_name}' 不存在，无法更新。")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))

    window = MyMainWindow()
    window.show()

    sys.exit(app.exec_())