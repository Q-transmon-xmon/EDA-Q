# File: gui_modules/display_area.py
from PyQt5.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QSizePolicy
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import os


class DisplayArea(QTabWidget):
    """集成Tab管理功能，直接继承QTabWidget"""

    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window  # 直接持有主窗口引用
        self.topo_tab = None
        self.gds_tab = None
        self.init_ui()

    def init_ui(self):
        """初始化Tab界面"""
        self.setTabsClosable(False)
        self.setStyleSheet("""
            QTabWidget::pane { border: 1px solid black; border-top-left-radius: 5px; border-top-right-radius: 5px; }
            QTabBar::tab { background: #f7f7f7; padding: 10px; margin-right: 1px; border: 1px solid black; border-bottom: none; }
            QTabBar::tab:selected { background: white; font-weight: bold; }
        """)

        # 创建Topo和GDS标签页
        self.topo_tab = self.DisplayTab("Topo", self.main_window)
        self.gds_tab = self.DisplayTab("GDS", self.main_window)
        self.addTab(self.topo_tab, "Topo")
        self.addTab(self.gds_tab, "GDS")

    class DisplayTab(QWidget):
        """单个标签页的内容"""

        def __init__(self, tab_name, main_window):
            super().__init__()
            self.tab_name = tab_name
            self.main_window = main_window  # 主窗口引用
            self.image_label = None
            self.init_ui()

        def init_ui(self):
            """初始化标签页界面（保留原有DisplayArea功能）"""
            layout = QVBoxLayout(self)

            # 显示标签
            display_label = QLabel(f"{self.tab_name} Interface")
            display_label.setMaximumHeight(50)
            layout.addWidget(display_label, alignment=Qt.AlignCenter)

            # 图片显示区域
            self.image_label = QLabel()
            self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            layout.addWidget(self.image_label)

            # 缩放按钮
            zoom_button = QPushButton("🔍")
            zoom_button.setToolTip("Zoom In")
            zoom_button.clicked.connect(self.zoom_in)
            button_layout = QHBoxLayout()
            button_layout.addStretch()
            button_layout.addWidget(zoom_button)
            layout.addLayout(button_layout)

        def zoom_in(self):
            """缩放功能（通过主窗口访问design）"""
            print(f"放大{self.tab_name}")
            try:
                if self.main_window and hasattr(self.main_window, "design"):
                    if self.tab_name == "GDS":
                        self.main_window.design.gds.show_gds()
                        print(self.main_window.design.gds.chips["chip0"].position())
                    elif self.tab_name == "Topo":
                        self.main_window.design.topology.show_image()
            except Exception as e:
                print(f"Error in zoom_in: {str(e)}")

        def load_image(self, image_path):
            """加载并显示图片（保留原有逻辑）"""
            if os.path.exists(image_path):
                pixmap = QPixmap(image_path)
                self.image_label.setPixmap(pixmap.scaled(
                    self.image_label.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                ))
                print(f"Loaded image: {image_path}")
            else:
                print(f"Image not found: {image_path}")

        def show_image(self, image_path, show=True):
            """显示图片（保留原有逻辑）"""
            try:
                if show and os.path.exists(image_path):
                    print(f"Displaying {self.tab_name} image")
                    self.show_picture(image_path)
            except Exception as e:
                print(f"Failed to save or display {self.tab_name} image: {e}")

        def show_picture(self, picture_path):
            """显示图片并居中（保留原有逻辑）"""
            try:
                if not os.path.exists(picture_path):
                    print(f"Error: Image file not found at {picture_path}")
                    return

                self.image_label.clear()
                pixmap = QPixmap(picture_path)
                if pixmap.isNull():
                    print(f"Error: Failed to load image from {picture_path}")
                    return

                scaled_pixmap = pixmap.scaled(
                    self.image_label.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.image_label.setPixmap(scaled_pixmap)
                self.image_label.setAlignment(Qt.AlignCenter)
                print(f"Displayed image: {picture_path}")
            except Exception as e:
                print(f"Failed to display image: {e}")

        def clear_display(self):
            """清屏功能（保留原有逻辑）"""
            self.image_label.clear()
            print(f"{self.tab_name} 显示已清除")