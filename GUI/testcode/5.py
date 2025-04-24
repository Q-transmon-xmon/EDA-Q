# File: gui_modules/display_area.py
from PyQt5.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QSizePolicy
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import os


class DisplayArea(QTabWidget):
    """integrationTabmanagement function，direct inheritanceQTabWidget"""

    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window  # Directly holding the main window reference
        self.topo_tab = None
        self.gds_tab = None
        self.init_ui()

    def init_ui(self):
        """initializationTabinterface"""
        self.setTabsClosable(False)
        self.setStyleSheet("""
            QTabWidget::pane { border: 1px solid black; border-top-left-radius: 5px; border-top-right-radius: 5px; }
            QTabBar::tab { background: #f7f7f7; padding: 10px; margin-right: 1px; border: 1px solid black; border-bottom: none; }
            QTabBar::tab:selected { background: white; font-weight: bold; }
        """)

        # createTopoandGDSTag Page
        self.topo_tab = self.DisplayTab("Topo", self.main_window)
        self.gds_tab = self.DisplayTab("GDS", self.main_window)
        self.addTab(self.topo_tab, "Topo")
        self.addTab(self.gds_tab, "GDS")

    class DisplayTab(QWidget):
        """The content of a single tab"""

        def __init__(self, tab_name, main_window):
            super().__init__()
            self.tab_name = tab_name
            self.main_window = main_window  # Main window reference
            self.image_label = None
            self.init_ui()

        def init_ui(self):
            """Initialize tab interface（Keep the originalDisplayAreafunction）"""
            layout = QVBoxLayout(self)

            # Display Label
            display_label = QLabel(f"{self.tab_name} Interface")
            display_label.setMaximumHeight(50)
            layout.addWidget(display_label, alignment=Qt.AlignCenter)

            # Image display area
            self.image_label = QLabel()
            self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            layout.addWidget(self.image_label)

            # Zoom button
            zoom_button = QPushButton("🔍")
            zoom_button.setToolTip("Zoom In")
            zoom_button.clicked.connect(self.zoom_in)
            button_layout = QHBoxLayout()
            button_layout.addStretch()
            button_layout.addWidget(zoom_button)
            layout.addLayout(button_layout)

        def zoom_in(self):
            """zoom function（Accessing through the main windowdesign）"""
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
            """Load and display images（Keep the original logic）"""
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
            """display picture（Keep the original logic）"""
            try:
                if show and os.path.exists(image_path):
                    print(f"Displaying {self.tab_name} image")
                    self.show_picture(image_path)
            except Exception as e:
                print(f"Failed to save or display {self.tab_name} image: {e}")

        def show_picture(self, picture_path):
            """Display the image and center it（Keep the original logic）"""
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
            """Clear screen function（Keep the original logic）"""
            self.image_label.clear()
            print(f"{self.tab_name} 显示已清除")