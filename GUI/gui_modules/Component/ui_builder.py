from PyQt5.QtWidgets import (QWidget, QGridLayout, QPushButton, QHBoxLayout,
                             QLabel, QSizePolicy)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize

from .styles import get_component_styles
from ...icons.path_manager import get_icon_path


class UIBuilder:
    """Handles all UI construction for the component library"""

    @staticmethod
    def setup_custom_titlebar(widget):
        """Create and set a custom title bar for the dock widget"""
        title_bar = QWidget()
        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        title_label = QLabel("Component Library")
        title_label.setStyleSheet("font-weight: bold;")

        # Create buttons
        buttons = [
            ("custom", "title/loading.svg", "import gds", widget.handle_custom_button_clicked),
            ("float", "title/split.svg", "toggle floating", widget.toggle_floating),
            ("close", "title/close.svg", "close", widget.close)
        ]

        # Add buttons to layout
        layout.addWidget(title_label)
        layout.addStretch()

        for name, icon_path, tooltip, slot in buttons:
            btn = QPushButton()
            btn.setIcon(QIcon(str(get_icon_path(icon_path))))
            btn.setIconSize(QSize(15, 15))
            btn.setFixedSize(15, 20)
            btn.setToolTip(tooltip)
            btn.setStyleSheet("border: none; background-color: transparent; padding: 0;")
            btn.clicked.connect(slot)
            layout.addWidget(btn)

        widget.setTitleBarWidget(title_bar)

    @staticmethod
    def create_category(main_layout, category, click_handler):
        """Create a collapsible category section"""
        header = QPushButton(f"▶ {category['name']}")
        header.setCheckable(True)
        header.setStyleSheet(get_component_styles()["category_header"])
        header.toggled.connect(lambda checked: UIBuilder._toggle_category(header, checked))

        container = QWidget()
        container.setVisible(False)
        grid = QGridLayout(container)

        style = get_component_styles()["container_layout"]
        # 修改这部分代码：
        grid.setContentsMargins(*style["margins"])
        grid.setHorizontalSpacing(style["spacing"][0])
        grid.setVerticalSpacing(style["spacing"][1])

        # Add component buttons
        row, col = 0, 0
        for comp in category["components"]:
            btn = UIBuilder.create_component_button(comp, click_handler)
            grid.addWidget(btn, row, col)
            col = 1 - col  # Two column layout
            if col == 0:
                row += 1

        container.setMinimumWidth(380)
        container.setMaximumWidth(500)
        header.container = container
        main_layout.addWidget(header)
        main_layout.addWidget(container)

    @staticmethod
    def _toggle_category(header, expanded):
        """Toggle category expand/collapse state"""
        header.setText(f"▼ {header.text()[2:]}" if expanded else f"▶ {header.text()[2:]}")
        header.container.setVisible(expanded)

        # Adjust header width based on content
        text_width = header.fontMetrics().boundingRect(header.text()).width()
        header.setMinimumWidth(text_width + 60)

    @staticmethod
    def create_component_button(comp, click_handler):
        """Create a button for a component"""
        btn = QPushButton(comp["name"])
        text_width = btn.fontMetrics().boundingRect(btn.text()).width()
        btn.setFixedSize(text_width + 20, 40)  # Add padding to text width
        btn.setStyleSheet(get_component_styles()["component_button"])
        btn.setProperty("command", comp["command"])
        btn.clicked.connect(lambda: click_handler(comp["command"]))
        btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        return btn