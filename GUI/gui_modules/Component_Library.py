import os

from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtWidgets import (QDockWidget, QWidget, QGridLayout, QVBoxLayout,
                             QPushButton, QScrollArea, QSizePolicy, QDialog, QFormLayout, QLineEdit, QHBoxLayout,
                             QLabel)
from PyQt5.QtGui import QIcon, QFontMetrics
from .Component_Actions import ComponentActions
from .Component.Xmon_Actions import XmonActions
from .Component.AirBridge_Actions import AirBridgeActions
from .Component.AirbriageNb_Actions import AirbriageNbActions
from .Component.ChargeLine_Actions import ChargeLineActions
from .Component.ControlLineCircle_Actions import ControlLineCircleActions
from .Component.ControlLineWidthDiff_Actions import ControlLineWidthDiffActions
from .Component.CouplerBase_Actions import CouplerBaseActions
from .Component.CouplingCavity_Actions import CouplingCavityActions
from .Component.CouplingLineStraight_Actions import CouplingLineStraightActions
from .Component.IndiumBump_Actions import IndiumBumpActions
from .Component.LaunchPad_Actions import LaunchPadActions
from .Component.ReadoutArrow_Actions import ReadoutArrowActions
from .Component.ReadoutArrowPlus_Actions import ReadoutArrowPlusActions
from .Component.ReadoutCavity_Actions import ReadoutCavityActions
from .Component.ReadoutCavityFlipchip_Actions import ReadoutCavityFlipchipActions
from .Component.ReadoutCavityPlus_Actions import ReadoutCavityPlusActions
from .Component.TransmissionPath_Actions import TransmissionPathActions
from .Component.Transmon_Actions import TransmonActions  # Import containing TransmonActions
from addict import Dict


class ComponentLibrary(QDockWidget):
    operation_completed = pyqtSignal(str)  # Unified operation completion signal

    def __init__(self, parent=None, current_design=None, categories=None):
        super().__init__("Component Library", parent)
        self.actions = ComponentActions(current_design, parent)  # Pass current_design
        self.airbridge_actions = AirBridgeActions(current_design, parent)
        self.airbriage_nb_actions = AirbriageNbActions(current_design, parent)
        self.charge_line_actions = ChargeLineActions(current_design, parent)
        self.control_line_circle_actions = ControlLineCircleActions(current_design, parent)
        self.control_line_width_diff_actions = ControlLineWidthDiffActions(current_design, parent)
        self.coupler_base_actions = CouplerBaseActions(current_design, parent)
        self.coupling_cavity_actions = CouplingCavityActions(current_design, parent)
        self.coupling_line_straight_actions = CouplingLineStraightActions(current_design, parent)
        self.indium_bump_actions = IndiumBumpActions(current_design, parent)
        self.launch_pad_actions = LaunchPadActions(current_design, parent)
        self.readout_arrow_actions = ReadoutArrowActions(current_design, parent)
        self.readout_arrow_plus_actions = ReadoutArrowPlusActions(current_design, parent)
        self.readout_cavity_actions = ReadoutCavityActions(current_design, parent)
        self.readout_cavity_flipchip_actions = ReadoutCavityFlipchipActions(current_design, parent)
        self.readout_cavity_plus_actions = ReadoutCavityPlusActions(current_design, parent)
        self.transmission_path_actions = TransmissionPathActions(current_design, parent)
        self.transmon_actions = TransmonActions(current_design, parent)  # Instance containing TransmonActions
        self.xmon_actions = XmonActions(current_design, parent)
        self.categories = categories or self.DEFAULT_CATEGORIES
        self.isResizing = False
        self.setup_custom_titlebar()
        self.init_ui()
        self.setup_connections()

        # Default category configuration (includes all 18 components)

    DEFAULT_CATEGORIES = [
        {
            "name": "Qubit Structures",
            "components": [
                {"name": "Transmon", "icon": "icons/transmon.png", "command": "transmon"},
                {"name": "Xmon", "icon": "icons/xmon.png", "command": "xmon"}
            ]
        },
        {
            "name": "Qubit Coupling Structures",
            "components": [
                {"name": "Coupling Cavity", "icon": "icons/coupling_cavity.png", "command": "coupling_cavity"},
                {"name": "Coupling Line Straight", "icon": "icons/coupling_line.png",
                 "command": "coupling_line_straight"}
            ]
        },
        {
            "name": "Readout and Measurement Structures",
            "components": [
                {"name": "Readout Cavity", "icon": "icons/readout_cavity.png", "command": "readout_cavity"},
                {"name": "Readout Cavity Plus", "icon": "icons/readout_cavity_plus.png",
                 "command": "readout_cavity_plus"},
                {"name": "Readout Cavity Flipchip", "icon": "icons/readout_cavity_flipchip.png",
                 "command": "readout_cavity_flipchip"},
                {"name": "Readout Arrow", "icon": "icons/readout_arrow.png", "command": "readout_arrow"},
                {"name": "Readout Arrow Plus", "icon": "icons/readout_arrow_plus.png", "command": "readout_arrow_plus"},
                {"name": "Launch Pad", "icon": "icons/launch_pad.png", "command": "launch_pad"}
            ]
        },
        {
            "name": "Control Lines and Signal Transmission Structures",
            "components": [
                {"name": "Control Line Circle", "icon": "icons/control_line_circle.png",
                 "command": "control_line_circle"},
                {"name": "Control Line Width Diff", "icon": "icons/control_line_width_diff.png",
                 "command": "control_line_width_diff"},
                {"name": "Transmission Path", "icon": "icons/transmission_path.png", "command": "transmission_path"},
                {"name": "Charge Line", "icon": "icons/charge_line.png", "command": "charge_line"}
            ]
        },
        {
            "name": "Packaging and Interconnect Structures",
            "components": [
                {"name": "AirBridge", "icon": "icons/airbridge.png", "command": "airbridge"},
                {"name": "AirbriageNb", "icon": "icons/airbriage_nb.png", "command": "airbriage_nb"},
                {"name": "Indium Bump", "icon": "icons/indium_bump.png", "command": "indium_bump"}
            ]
        },
        {
            "name": "Auxiliary Structures",
            "components": [
                {"name": "Coupler Base", "icon": "icons/coupler_base.png", "command": "coupler_base"}
            ]
        }
    ]

    def setup_custom_titlebar(self):
        # Create a custom title bar
        title_bar = QWidget()
        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove title bar margins
        layout.setSpacing(0)  # Set layout spacing to 0 for more compact buttons

        # Title label
        title_label = QLabel("Component Library")
        title_label.setStyleSheet("font-weight: bold;")

        # Dynamically get icon path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        icons_dir = os.path.join(os.path.dirname(current_dir), "icons", "title")

        close_icon_path = os.path.join(icons_dir, "close.svg")
        float_icon_path = os.path.join(icons_dir, "split.svg")
        custom_icon_path = os.path.join(icons_dir, "loading.svg")

        # Add custom button
        custom_btn = QPushButton()
        custom_btn.setIcon(QIcon(custom_icon_path))  # Dynamically load custom icon
        custom_btn.setIconSize(QSize(15, 15))  # Adjust icon size
        custom_btn.setFixedSize(15, 20)  # Reduce button width
        custom_btn.setToolTip("import gds")  # Mouse hover tooltip
        custom_btn.setStyleSheet("border: none; background-color: transparent; padding: 0;")  # Remove margins and borders

        # Window control buttons (minimize, maximize, close)
        close_button = QPushButton()
        close_button.setIcon(QIcon(close_icon_path))  # Dynamically load close icon
        close_button.setIconSize(QSize(15, 15))  # Adjust icon size
        close_button.setFixedSize(15, 20)  # Reduce button width
        close_button.setStyleSheet("border: none; background-color: transparent; padding: 0;")  # Remove margins

        # Float button (restore button)
        float_button = QPushButton()
        float_button.setIcon(QIcon(float_icon_path))  # Dynamically load float icon
        float_button.setIconSize(QSize(15, 15))  # Adjust icon size
        float_button.setFixedSize(15, 20)  # Reduce button width
        float_button.setStyleSheet("border: none; background-color: transparent; padding: 0;")  # Remove margins


        # Connect button events
        close_button.clicked.connect(self.close)  # Close window
        float_button.clicked.connect(self.toggle_floating)  # Toggle floating state
        custom_btn.clicked.connect(self.handle_custom_button_clicked)  # Custom button events

        # Add all controls to layout
        layout.addWidget(title_label)
        layout.addStretch()  # Push buttons to the right
        layout.addWidget(custom_btn)
        layout.addWidget(float_button)
        layout.addWidget(close_button)


        # Set custom title bar
        self.setTitleBarWidget(title_bar)
#######-------------------------ADD GDS ----------------------------------#####
    def handle_custom_button_clicked(self):
        print("Custom button clicked!")  # Replace with your desired logic

    def toggle_floating(self):
        if self.isFloating():
            self.setFloating(False)  # Cancel floating
        else:
            self.setFloating(True)  # Set as floating window

    def init_ui(self):
        # Scroll area settings
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        scroll.setWidget(content)

        # Main layout
        main_layout = QVBoxLayout(content)
        main_layout.setAlignment(Qt.AlignTop)
        main_layout.setContentsMargins(8, 12, 8, 12)
        main_layout.setSpacing(8)

        # Create category blocks
        for category in self.categories:
            self.create_category(main_layout, category)

        self.setWidget(scroll)

    def get_styles(self):
        """Return style dictionary"""
        return {
            "category_header": """  
                QPushButton {  
                    text-align: left;  
                    padding: 5px;  
                    font-weight: bold;  
                    font-size: 14px;  
                    background-color: #f0f0f0;  
                }  
            """,
            "component_button": """  
                QPushButton {  
                    padding: 4.096px;  /* 5.12px * 0.8 */
                    text-align: center;  
                    border-radius: 2.048px;  /* 2.56px * 0.8 */
                    min-width: 61.44px;  /* 76.8px * 0.8 */
                    min-height: 30.72px;  /* 38.4px * 0.8 */
                    font-size: 6.144px;  /* 7.68px * 0.8 */
                }  
                QPushButton:hover {  
                    background-color: #e0e0e0;  
                }  
            """,
            "container_layout": {
                "margins": (10, 5, 10, 10),
                "spacing": (10, 10)  # (horizontal, vertical)
            }
        }

    def create_category(self, layout, category):
        """Create a category block (includes expand/collapse functionality)"""
        # CATEGORY TITLE
        header = QPushButton(f"▶ {category['name']}")
        header.setCheckable(True)
        header.setStyleSheet(self.get_styles()["category_header"])

        # Fix using closures to reference header
        header.toggled.connect(lambda checked, h=header: self.toggle_category(h, checked))

        # Component container
        container = QWidget()
        container.setVisible(False)
        grid = QGridLayout(container)

        # Apply container styles
        style = self.get_styles()["container_layout"]
        grid.setContentsMargins(*style["margins"])
        grid.setHorizontalSpacing(style["spacing"][0])
        grid.setVerticalSpacing(style["spacing"][1])

        # Add component buttons
        row, col = 0, 0
        for comp in category["components"]:
            btn = self.create_component_button(comp)
            grid.addWidget(btn, row, col)
            col = 1 - col  # Two column layout
            if col == 0:
                row += 1

                # Store container reference
        container.setMinimumWidth(380)
        container.setMaximumWidth(500)
        header.container = container
        layout.addWidget(header)
        layout.addWidget(container)

    def create_component_button(self, comp):
        """Create a single component button"""
        btn = QPushButton(comp["name"])
        btn.setIcon(QIcon(comp["icon"]))
        btn.setIconSize(QSize(16, 16))  # Set icon size
        text_width = QFontMetrics(btn.font()).boundingRect(btn.text()).width()
        btn.setFixedSize(text_width + 200, 40)
        btn.setStyleSheet(self.get_styles()["component_button"])
        btn.setProperty("command", comp["command"])
        btn.clicked.connect(lambda: self.handle_component_click(comp["command"]))
        btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # Fixed size policy
        return btn

    def toggle_category(self, header, expanded):
        """Handle expand/collapse state"""
        header.setText(f"▼ {header.text()[2:]}" if expanded else f"▶ {header.text()[2:]}")
        header.container.setVisible(expanded)

        # Ensure button width is not less than name width
        if expanded:
            # Get text width
            text_width = header.fontMetrics().boundingRect(header.text()).width()
            # Set button minimum width
            header.setMinimumWidth(text_width + 60)  # Add extra space (30px) for icons and margins
        else:
            # When collapsed, can set smaller width but still consider text width
            text_width = header.fontMetrics().boundingRect(header.text()).width()
            header.setMinimumWidth(text_width + 60)  # Also consider extra space

    def setup_connections(self):
        """Connect business logic signals"""
        self.actions.operation_completed.connect(self.handle_operation_completed)

    def handle_operation_completed(self, message):
        """Callback for handling operation completion signal"""
        print(message)  # Print operation completion message to console

    def handle_component_click(self, command):
        """Route component click events"""
        handler_map = {
            "transmon": self.transmon_actions.transmon,
            "xmon": self.xmon_actions.xmon,
            "coupling_cavity": self.coupling_cavity_actions.coupling_cavity,
            "coupling_line_straight": self.coupling_line_straight_actions.coupling_line_straight,
            "readout_cavity": self.readout_cavity_actions.readout_cavity,
            "readout_cavity_plus": self.readout_cavity_plus_actions.readout_cavity_plus,
            "readout_cavity_flipchip": self.readout_cavity_flipchip_actions.readout_cavity_flipchip,
            "readout_arrow": self.readout_arrow_actions.readout_arrow,
            "readout_arrow_plus": self.readout_arrow_plus_actions.readout_arrow_plus,
            "launch_pad": self.launch_pad_actions.launch_pad,
            "control_line_circle": self.control_line_circle_actions.control_line_circle,
            "control_line_width_diff": self.control_line_width_diff_actions.control_line_width_diff,
            "transmission_path": self.transmission_path_actions.transmission_path,
            "charge_line": self.charge_line_actions.charge_line,
            "airbridge": self.airbridge_actions.airbridge,
            "airbriage_nb": self.airbriage_nb_actions.airbriage_nb,
            "indium_bump": self.indium_bump_actions.indium_bump,
            "coupler_base": self.coupler_base_actions.coupler_base
        }

        if handler := handler_map.get(command):
            try:
                handler()  # Directly call specific operation
            except Exception as e:
                self.operation_completed.emit(f"Operation exception: {str(e)}")
        else:
            self.operation_completed.emit(f"Undefined operation: {command}")

    def mousePressEvent(self, event):
        """Record starting position when beginning drag"""
        if event.button() == Qt.LeftButton:
            self.isResizing = True
            self.startPos = event.pos()  # Record mouse click position

    def mouseMoveEvent(self, event):
        """Handle drag events"""
        if self.isResizing:
            # Calculate new width
            newWidth = self.width() + (event.x() - self.startPos.x())
            # Set minimum width
            if newWidth >= 380 and newWidth <= 550:
                self.setFixedWidth(newWidth)  # Update width

    def mouseReleaseEvent(self, event):
        """End drag"""
        if event.button() == Qt.LeftButton:
            self.isResizing = False