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
from .Component.Transmon_Actions import TransmonActions  # 包含 TransmonActions 的导入
from addict import Dict


class ComponentLibrary(QDockWidget):
    operation_completed = pyqtSignal(str)  # 统一操作完成信号

    def __init__(self, parent=None, current_design=None, categories=None):
        super().__init__("Component Library", parent)
        self.actions = ComponentActions(current_design, parent)  # 传递 current_design
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
        self.transmon_actions = TransmonActions(current_design, parent)  # 包含 TransmonActions 的实例
        self.xmon_actions = XmonActions(current_design, parent)
        self.categories = categories or self.DEFAULT_CATEGORIES
        self.isResizing = False
        self.setup_custom_titlebar()
        self.init_ui()
        self.setup_connections()

        # 默认分类配置（包含所有 18 个组件）

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
        # 创建自定义标题栏
        title_bar = QWidget()
        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(0, 0, 0, 0)  # 移除标题栏内部的边距
        layout.setSpacing(0)  # 将布局间距设置为0，使按钮更紧凑

        # 标题标签
        title_label = QLabel("Component Library")
        title_label.setStyleSheet("font-weight: bold;")

        # 动态获取图标路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        icons_dir = os.path.join(os.path.dirname(current_dir), "icons", "title")

        close_icon_path = os.path.join(icons_dir, "close.svg")
        float_icon_path = os.path.join(icons_dir, "split.svg")
        custom_icon_path = os.path.join(icons_dir, "loading.svg")

        # 新增自定义按钮
        custom_btn = QPushButton()
        custom_btn.setIcon(QIcon(custom_icon_path))  # 动态加载自定义图标
        custom_btn.setIconSize(QSize(15, 15))  # 调整图标大小
        custom_btn.setFixedSize(15, 20)  # 减小按钮宽度
        custom_btn.setToolTip("import gds")  # 鼠标悬停提示
        custom_btn.setStyleSheet("border: none; background-color: transparent; padding: 0;")  # 去掉边距和边框

        # 右侧窗口控制按钮（最小化、最大化、关闭）
        close_button = QPushButton()
        close_button.setIcon(QIcon(close_icon_path))  # 动态加载关闭图标
        close_button.setIconSize(QSize(15, 15))  # 调整图标大小
        close_button.setFixedSize(15, 20)  # 减小按钮宽度
        close_button.setStyleSheet("border: none; background-color: transparent; padding: 0;")  # 去掉边距

        # 浮动按钮（还原按钮）
        float_button = QPushButton()
        float_button.setIcon(QIcon(float_icon_path))  # 动态加载浮动图标
        float_button.setIconSize(QSize(15, 15))  # 调整图标大小
        float_button.setFixedSize(15, 20)  # 减小按钮宽度
        float_button.setStyleSheet("border: none; background-color: transparent; padding: 0;")  # 去掉边距


        # 连接按钮的事件
        close_button.clicked.connect(self.close)  # 关闭窗口
        float_button.clicked.connect(self.toggle_floating)  # 切换浮动状态
        custom_btn.clicked.connect(self.handle_custom_button_clicked)  # 自定义按钮事件

        # 将所有控件添加到布局中
        layout.addWidget(title_label)
        layout.addStretch()  # 拉伸将按钮推到右侧
        layout.addWidget(custom_btn)
        layout.addWidget(float_button)
        layout.addWidget(close_button)


        # 设置自定义标题栏
        self.setTitleBarWidget(title_bar)
#######-------------------------ADD GDS ----------------------------------#####
    def handle_custom_button_clicked(self):
        print("自定义按钮点击了！")  # 替换为你想执行的逻辑

    def toggle_floating(self):
        if self.isFloating():
            self.setFloating(False)  # 取消浮动
        else:
            self.setFloating(True)  # 设置为浮动窗口

    def init_ui(self):
        # 滚动区域设置
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        scroll.setWidget(content)

        # 主布局
        main_layout = QVBoxLayout(content)
        main_layout.setAlignment(Qt.AlignTop)
        main_layout.setContentsMargins(8, 12, 8, 12)
        main_layout.setSpacing(8)

        # 创建分类区块
        for category in self.categories:
            self.create_category(main_layout, category)

        self.setWidget(scroll)

    def get_styles(self):
        """返回样式字典"""
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
        """创建分类区块（包含展开/折叠功能）"""
        # 分类标题
        header = QPushButton(f"▶ {category['name']}")
        header.setCheckable(True)
        header.setStyleSheet(self.get_styles()["category_header"])

        # 使用闭包固定header引用
        header.toggled.connect(lambda checked, h=header: self.toggle_category(h, checked))

        # 组件容器
        container = QWidget()
        container.setVisible(False)
        grid = QGridLayout(container)

        # 绑定鼠标事件
        # header.setMouseTracking(True)
        # header.mousePressEvent = self.mousePressEvent
        # header.mouseMoveEvent = self.mouseMoveEvent
        # header.mouseReleaseEvent = self.mouseReleaseEvent

        # 应用容器样式
        style = self.get_styles()["container_layout"]
        grid.setContentsMargins(*style["margins"])
        grid.setHorizontalSpacing(style["spacing"][0])
        grid.setVerticalSpacing(style["spacing"][1])

        # 添加组件按钮
        row, col = 0, 0
        for comp in category["components"]:
            btn = self.create_component_button(comp)
            grid.addWidget(btn, row, col)
            col = 1 - col  # 两列布局
            if col == 0:
                row += 1

                # 存储容器引用
        container.setMinimumWidth(380)
        container.setMaximumWidth(500)
        header.container = container
        layout.addWidget(header)
        layout.addWidget(container)

    def create_component_button(self, comp):
        """创建单个组件按钮"""
        btn = QPushButton(comp["name"])
        btn.setIcon(QIcon(comp["icon"]))
        btn.setIconSize(QSize(16, 16))  # 设置图标大小
        text_width = QFontMetrics(btn.font()).boundingRect(btn.text()).width()
        # print(text_width)
        # btn.setFixedSize(170, 40)  # 确保最小宽度为100，或文本宽度+20
        btn.setFixedSize(text_width + 200, 40)
        btn.setStyleSheet(self.get_styles()["component_button"])
        btn.setProperty("command", comp["command"])
        btn.clicked.connect(lambda: self.handle_component_click(comp["command"]))
        btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # 固定大小策略
        return btn

    def toggle_category(self, header, expanded):
        """处理展开/折叠状态"""
        header.setText(f"▼ {header.text()[2:]}" if expanded else f"▶ {header.text()[2:]}")
        header.container.setVisible(expanded)

        # 切换文本
        # header.setText(f"▼ {header.text()[2:]}" if expanded else f"▶ {header.text()[2:]}")

        # 显示或隐藏组件容器
        # header.container.setVisible(expanded)

        # 确保按钮宽度不会小于名称的宽度
        if expanded:
            # 获取文本宽度
            text_width = header.fontMetrics().boundingRect(header.text()).width()
            # 设置按钮的最小宽度
            header.setMinimumWidth(text_width + 60)  # 加一些额外的空间（如 30px）以适应图标和边距
        else:
            # 收起时可设置为更小的宽度，但仍然要考虑文本宽度
            text_width = header.fontMetrics().boundingRect(header.text()).width()
            header.setMinimumWidth(text_width + 60)  # 同样考虑额外的空间

    def setup_connections(self):
        """连接业务逻辑信号"""
        self.actions.operation_completed.connect(self.handle_operation_completed)

    def handle_operation_completed(self, message):
        """处理操作完成信号的回调"""
        print(message)  # 在控制台打印操作完成的消息

    def handle_component_click(self, command):
        """路由组件点击事件"""
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
                handler()  # 直接调用具体的操作
            except Exception as e:
                self.operation_completed.emit(f"操作异常: {str(e)}")
        else:
            self.operation_completed.emit(f"未定义操作: {command}")

    def mousePressEvent(self, event):
        """开始拖动时记录起始位置"""
        if event.button() == Qt.LeftButton:
            self.isResizing = True
            self.startPos = event.pos()  # 记录鼠标点击位置

    def mouseMoveEvent(self, event):
        """处理拖动事件"""
        if self.isResizing:
            # 计算新的宽度
            newWidth = self.width() + (event.x() - self.startPos.x())
            # 设置最小宽度
            if newWidth >= 380 and newWidth <= 550:
                self.setFixedWidth(newWidth)  # 更新宽度

    def mouseReleaseEvent(self, event):
        """结束拖动"""
        if event.button() == Qt.LeftButton:
            self.isResizing = False