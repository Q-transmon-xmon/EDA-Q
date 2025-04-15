import os
import sys
# 获取当前脚本所在的目录
current_path = os.path.dirname(os.path.abspath(__file__))
GUI_PATH = os.path.dirname(current_path)
PROJ_PATH = os.path.dirname(GUI_PATH)

# 添加路径
sys.path.append(GUI_PATH)
sys.path.append(PROJ_PATH)

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMenuBar, QVBoxLayout,
    QHBoxLayout, QWidget, QToolBar, QAction, QLabel,
    QTreeWidget, QTreeWidgetItem, QMenu, QPushButton, QFrame, QSplitter, QMessageBox, QStackedWidget, QSizePolicy,
    QTabWidget, QFileDialog, QDialog
)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.uic.properties import QtWidgets
from GUI_3_4_6.Widget_2.Widget_chiplayer import Dialog_ChipLayer
from GUI_3_4_6.Widget_2.Widget_RAlgorithm import Dialog_RAlgorithm
from GUI_3_4_6.Widget_2.Widget_RCavity import Dialog_RCavity
from GUI_3_4_6.Widget_2.Widget_Gds import NestedDictViewer, Window_Gds
from GUI_3_4_6.Widget_2.Widget_Pin import Dialog_pins
from GUI_3_4_6.Widget_2.Widget_Others import Dialog_Others
from GUI_3_4_6.Widget_2.Topo_Node import Dialog_Node
from GUI_3_4_6.Widget_2.Topo_RandomEdge import RandomEdge_Dialog
from GUI_3_4_6.Widget_2.Topo_CustomEdge import CustomEdge_Dialog
from GUI_3_4_6.Widget_2.Qubit_type import SelectionDialog
from GUI_3_4_6.Widget_2.Qubit_Custom import Dialog_Qubit_Custom
from GUI_3_4_6.Widget_2.Generate_Tmls import Dialog_tmls
from GUI_3_4_6.Widget_2.Generate_Cpls import Dialog_cpls
from GUI_3_4_6.Widget_2.Generate_Ctls import Dialog_ctls
from GUI_3_4_6.Widget_2.Generate_Crosvs import Dialog_crosvs
from GUI_3_4_6.Widget_2.Sim_Xmon import Dialog_Xmon
from GUI_3_4_6.Widget_2.Sim_Trans import Dialog_Transmon
from GUI_3_4_6.Widget_2.Sim_Readout import Dialog_s21
from api.design import Design


class MyMainWindow(QMainWindow):
    def __init__(self):
        super(MyMainWindow, self).__init__()  # 明确指定父类
        self.node_dialog = None
        self.init_ui()  # Initialize UI
        self.design = Design()

    def init_ui(self):
        self.setWindowTitle("QEDA")

        # 获取主屏幕的可用尺寸（减去任务栏等区域）
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()

        # 将计算结果转换为整数（例如 1024.0 → 1024）
        window_width = int(screen_geometry.width() * 0.8)
        window_height = int(screen_geometry.height() * 0.8)

        # 设置窗口大小
        self.resize(window_width, window_height)  # 参数是整数

        # 将窗口移动到屏幕中央（坐标也必须是整数）
        self.move(
            int((screen_geometry.width() - window_width) / 2),
            int((screen_geometry.height() - window_height) / 2)
        )

        self.create_menu_bar()  # Create menu bar
        self.create_tool_bar()  # Create tool bar

        # Create main layout
        self.main_layout = QVBoxLayout()
        self.splitter = self.create_splitter()  # Create main splitter

        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)

        self.main_layout.addWidget(self.splitter)  # Add splitter to main layout
        self.splitter.setSizes([250, 800])  # 250 for project manager, 800 for content area

    def create_menu_bar(self):
        """Create menu bar and set style"""
        self.menu_bar = self.menuBar()
        self.set_menu_style()

        # Create menu items
        self.file_menu = self.menu_bar.addMenu("File")
        self.edit_menu = self.menu_bar.addMenu("Edit")
        self.view_menu = self.menu_bar.addMenu("View")
        self.project_menu = self.menu_bar.addMenu("Project")
        self.tools_menu = self.menu_bar.addMenu("Tools")
        self.window_menu = self.menu_bar.addMenu("Window")
        self.help_menu = self.menu_bar.addMenu("Help")

        # Add menu actions
        self.add_menu_actions()

    def add_menu_actions(self):
        """Add actions to menus"""
        file_actions = {
            "New": "Create a new file",
            "Open": "Open an existing file",
            "Save": "Save the current file",
        }

        edit_actions = {
            "Cut": "Cut the selected text",
            "Copy": "Copy the selected text",
            "Paste": "Paste the copied text",
        }

        view_actions = {
            "Zoom In": "Zoom in the view",
            "Zoom Out": "Zoom out the view",
        }

        project_actions = {
            "Add Project": "Add a new project",
            "Remove Project": "Remove the selected project",
        }

        tools_actions = {
            "Settings": "Open settings",
            "Options": "Open options",
        }

        help_actions = {
            "Documentation": "Open documentation",
            "About": "About this application",
        }

        # Add actions to File menu
        for name, description in file_actions.items():
            action = QAction(name, self)
            action.triggered.connect(lambda checked, action_name=name: self.handle_menu_action(action_name))
            self.file_menu.addAction(action)

        # Add actions to Edit menu
        for name, description in edit_actions.items():
            action = QAction(name, self)
            action.triggered.connect(lambda checked, action_name=name: self.handle_menu_action(action_name))
            self.edit_menu.addAction(action)

        # Add actions to View menu
        for name, description in view_actions.items():
            action = QAction(name, self)
            action.triggered.connect(lambda checked, action_name=name: self.handle_menu_action(action_name))
            self.view_menu.addAction(action)

        # Add actions to Project menu
        for name, description in project_actions.items():
            action = QAction(name, self)
            action.triggered.connect(lambda checked, action_name=name: self.handle_menu_action(action_name))
            self.project_menu.addAction(action)

        # Add actions to Tools menu
        for name, description in tools_actions.items():
            action = QAction(name, self)
            action.triggered.connect(lambda checked, action_name=name: self.handle_menu_action(action_name))
            self.tools_menu.addAction(action)

        # Add actions to Help menu
        for name, description in help_actions.items():
            action = QAction(name, self)
            action.triggered.connect(lambda checked, action_name=name: self.handle_menu_action(action_name))
            self.help_menu.addAction(action)

    def handle_menu_action(self, action_name):
        """Handle menu actions"""
        actions = {
            "New": self.new_action,
            "Open": self.open_file,
            "Save": self.save_file,
            "Cut": self.cut_action,
            "Copy": self.copy_action,
            "Paste": self.paste_action,
            "Zoom In": self.zoom_in_action,
            "Zoom Out": self.zoom_out_action,
            "Add Project": self.add_project_action,
            "Remove Project": self.remove_project_action,
            "Settings": self.settings_action,
            "Options": self.options_action,
            "Documentation": self.documentation_action,
            "About": self.about_action,
        }

        action_method = actions.get(action_name)
        if action_method:
            action_method()  # Call the corresponding action method

    def set_menu_style(self):
        """Set menu bar style"""
        self.menu_bar.setStyleSheet("""  
            QMenuBar {  
                background-color: #f0f0f0;  
            }  
            QMenuBar::item {  
                background: transparent;   
                padding: 10px;  
            }  
            QMenuBar::item:selected {  
                background: #d9d9d9;   
            }  
            QMenu {  
                background-color: #f0f0f0;  
                border: 1px solid #cccccc;  
            }  
            QMenu::item:selected {  
                background-color: #b3b3b3;  
            }  
        """)

    def create_tool_bar(self):
        """创建功能区的工具栏按钮"""
        self.toolbar = self.addToolBar("功能区")

        # 按钮的文本和对象名称映射
        buttons = [
            ("🔧 Import topology", "Algorithm"),
            ("🔩 Custom Topology", "Topology"),
            ("🔌 Equivalent Circuit", "Circuit"),
            ("🌀 Generate Qubits", "Qubit"),
            ("📐 Generate ChipLayer", "ChipLayer"),
            ("📡 Readout Cavity", "ReadingCavity"),
            ("🔘 Generate Pin", "GeneratePin"),
            ("🔗 Generate Lines", "GenerateLine"),
            ("📑 Routing Algorithm", "RoutingAlgorithm"),
            ("🗺️ Modify GDS", "GDS"),
            ("⚙️ Simulation", "Simulation"),
            ("🔍 Others", "Others"),
            ("🗑️ Clear", "Clear"),
        ]

        # 遍历按钮配置，创建工具栏按钮
        for button_text, object_name in buttons:
            if object_name == "Topology":
                # 为 Topology 按钮添加下拉菜单
                menu = QMenu(self)
                topology_options = ["Generate Topo Node", "Random-Generate Topo Edge", "Custom-Generate Topo Edge"]  # Topology 的选项
                for option_name in topology_options:
                    action = menu.addAction(option_name)
                    action.triggered.connect(lambda checked, name=option_name: self.topology_option_handler(name))

                action = QAction(button_text, self)
                action.setMenu(menu)  # 设置下拉菜单
                self.toolbar.addAction(action)

            elif object_name == "Qubit":
                # 为 Qubit 按钮添加下拉菜单
                menu = QMenu(self)
                qubit_options = ["Based on the existing topology", "Custom-generate qubits"]  # Qubit 的选项
                for option_name in qubit_options:
                    action = menu.addAction(option_name)
                    action.triggered.connect(lambda checked, name=option_name: self.qubit_option_handler(name))

                action = QAction(button_text, self)
                action.setMenu(menu)  # 设置下拉菜单
                self.toolbar.addAction(action)

            elif object_name == "GenerateLine":
                # 为 GenerateLine 按钮添加下拉菜单
                menu = QMenu(self)
                line_options = ["Coupling_line", "Control_line", "Crossover_line", "Transmission_line"]  # 线生成选项
                for option_name in line_options:
                    action = menu.addAction(option_name)
                    action.triggered.connect(lambda checked, name=option_name: self.line_option_handler(name))

                action = QAction(button_text, self)
                action.setMenu(menu)  # 设置下拉菜单
                self.toolbar.addAction(action)

            elif object_name == "Simulation":
                # 为 Simulation 按钮添加下拉菜单
                menu = QMenu(self)
                simulation_options = ["Xmon", "Transmon", "Readout"]  # 仿真选项
                for option_name in simulation_options:
                    action = menu.addAction(option_name)
                    action.triggered.connect(lambda checked, name=option_name: self.simulation_option_handler(name))

                action = QAction(button_text, self)
                action.setMenu(menu)  # 设置下拉菜单
                self.toolbar.addAction(action)

            else:
                # 其他没有下拉菜单的按钮
                action = QAction(button_text, self)
                action.setObjectName(object_name)
                action.triggered.connect(lambda checked, name=object_name: self.MenuAffairs(name))
                self.toolbar.addAction(action)

                # 定义处理各下拉菜单的函数

    def topology_option_handler(self, option_name):
        """通过选项名称动态处理 Topology 下拉菜单"""
        print(f"Topology Option Selected: {option_name}")
        if option_name == "Generate Topo Node":
            self.node_dialog = Dialog_Node(design=self.design)
            self.node_dialog.designUpdated.connect(self.updateMainDesign)
            self.node_dialog.exec_()
        elif option_name == "Random-Generate Topo Edge":
            self.RandomEdge = RandomEdge_Dialog(design=self.design)
            self.RandomEdge.designUpdated.connect(self.updateMainDesign)
            self.RandomEdge.exec_()
        elif option_name == "Custom-Generate Topo Edge":
            self.CustomEdge = CustomEdge_Dialog(design=self.design)
            self.CustomEdge.designUpdated.connect(self.updateMainDesign)
            self.CustomEdge.exec_()

    def qubit_option_handler(self, option_name):
        """通过选项名称动态处理 Qubit 下拉菜单"""
        print(f"Qubit Option Selected: {option_name}")
        if option_name == "Based on the existing topology":
            self.qubit_type = SelectionDialog(design=self.design)
            self.qubit_type.designUpdated.connect(self.updateMainDesign)
            self.qubit_type.exec_()
        elif option_name == "Custom-generate qubits":
            self.custom_qubit = Dialog_Qubit_Custom(design=self.design)
            self.custom_qubit.designUpdated.connect(self.updateMainDesign)
            self.custom_qubit.exec_()

    def line_option_handler(self, option_name):
        """通过选项名称动态处理 Generate Line 下拉菜单"""
        print(f"Generate Line Option Selected: {option_name}")
        if option_name == "Coupling_line":
            self.cpl_dialog = Dialog_cpls(design=self.design)
            self.cpl_dialog.designUpdated.connect(self.updateMainDesign)
            self.cpl_dialog.exec_()
        elif option_name == "Control_line":
            self.ctl_dialog = Dialog_ctls(design=self.design)
            self.ctl_dialog.designUpdated.connect(self.updateMainDesign)
            self.ctl_dialog.exec_()
        elif option_name == "Crossover_line":
            self.crosvs_dialog = Dialog_crosvs(design=self.design)
            self.crosvs_dialog.designUpdated.connect(self.updateMainDesign)
            self.crosvs_dialog.exec_()
        elif option_name == "Transmission_line":
            self.tml_dialog = Dialog_tmls(design=self.design)
            self.tml_dialog.designUpdated.connect(self.updateMainDesign)
            self.tml_dialog.exec_()

    def simulation_option_handler(self, option_name):
        """通过选项名称动态处理 Simulation 下拉菜单"""
        print(f"Simulation Option Selected: {option_name}")
        if option_name == "Xmon":
            self.xmon_dialog = Dialog_Xmon(design=self.design)
            self.xmon_dialog.designUpdated.connect(self.updateMainDesign)
            self.xmon_dialog.exec_()
        elif option_name == "Transmon":
            self.transmon_dialog = Dialog_Transmon(design=self.design)
            self.transmon_dialog.designUpdated.connect(self.updateMainDesign)
            self.transmon_dialog.exec_()
        elif option_name == "Readout":
            self.readout_dialog = Dialog_s21(design=self.design)
            self.readout_dialog.designUpdated.connect(self.updateMainDesign)
            self.readout_dialog.exec_()



    def create_splitter(self):
        """Create and configure main splitter."""

        splitter = QSplitter(Qt.Horizontal)

        # 设置分割器的伸缩因子（左侧占1份，右侧占3份）
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

        manager_widget = self.create_project_manager()
        splitter.addWidget(manager_widget)

        # Create a widget for the right display area using QTabWidget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(False)  # Not allowing close
        self.tab_widget.setStyleSheet("""  
            QTabWidget::pane {   
                border: 1px solid black;   
                border-top-left-radius: 5px;   
                border-top-right-radius: 5px;   
            }  
            QTabBar::tab {  
                background: #f7f7f7;  
                padding: 10px;  
                margin-right: 1px;  
                border: 1px solid black;   
                border-bottom: none;   
            }  
            QTabBar::tab:selected {  
                background: white;  
                font-weight: bold;  
            }  
        """)

        # Create tabs for Topo and GDS
        self.topo_tab = QWidget()
        self.gds_tab = QWidget()

        # Add tabs to the tab widget
        self.tab_widget.addTab(self.topo_tab, "Topo")
        self.tab_widget.addTab(self.gds_tab, "GDS")

        # Set layout for each tab
        self.topo_layout = QVBoxLayout(self.topo_tab)
        self.gds_layout = QVBoxLayout(self.gds_tab)

        # Create QLabel for displaying images and text
        self.topo_display = QLabel("Topo Interface")
        self.gds_display = QLabel("GDS Interface")

        # Use QLabel for image display
        self.topo_image_label = QLabel()
        self.gds_image_label = QLabel()

        # Set size policies for the image labels to fill the space
        self.topo_image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.gds_image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Set maximum size for QLabels to improve usability
        self.topo_display.setMaximumHeight(50)
        self.gds_display.setMaximumHeight(50)

        # Add labels to layouts (initially only show text)
        self.topo_layout.addWidget(self.topo_display, alignment=Qt.AlignCenter)
        self.topo_layout.addWidget(self.topo_image_label)  # Adding image label to the layout
        self.gds_layout.addWidget(self.gds_display, alignment=Qt.AlignCenter)
        self.gds_layout.addWidget(self.gds_image_label)  # Adding image label to the layout

        # Add zoom button in the top-right corner of the display area
        self.add_zoom_button(self.topo_layout, self.topo_image_label, "Topo")  # 传递标签和界面名称
        self.add_zoom_button(self.gds_layout, self.gds_image_label, "GDS")  # 传递标签和界面名称

        # Add the tab widget to the main layout
        splitter.addWidget(self.tab_widget)

        return splitter

    def add_zoom_button(self, layout, image_label, tab_name):
        """Add a zoom button at the top right corner of the specified layout."""
        zoom_button = QPushButton("🔍")  # Zoom icon
        zoom_button.setToolTip("Zoom In")
        # 将tab_name传递给zoom_in函数
        zoom_button.clicked.connect(lambda: self.zoom_in(image_label, tab_name))  # Connect to zoom function

        # Create a horizontal layout to hold the button
        button_layout = QHBoxLayout()
        button_layout.addStretch()  # Add stretchable space to push the button to the right
        button_layout.addWidget(zoom_button)

        layout.addLayout(button_layout)  # Add the button layout to the top of the layout

    def zoom_in(self, label, tab_name):
        """Zoom in functionality with tab-specific behavior."""
        # 根据当前标签页输出不同的提示信息
        if tab_name == "Topo":
            print("放大Topo")
            self.design.topology.show_image()
        elif tab_name == "GDS":
            print("放大GDS")
            self.design.gds.show_gds()


    def load_image(self, label, image_path):
        """Load and display image in the QLabel with resizing."""
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            # Scale the pixmap to fit the label while maintaining aspect ratio
            label.setPixmap(pixmap.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            print(f"Loaded image: {image_path}")  # Debug info for loaded image path
        else:
            print(f"Image not found: {image_path}")

    def reset_design_updated_flag(self):
        """Reset the design updated flag, usually called after the design is used."""
        self.design_updated_flag = False

    def show_topology_image(self, show=False):
        """Display the saved topology image."""
        try:
            # 尝试保存拓扑图像
            self.design.topology.save_image(path='./picture/topology.png')
        except Exception as e:
            print(f"Failed to save topology image: {e}")
            return

        picture_path = './picture/topology.png'  # 图像路径

        if show:  # 仅在 show 为 True 时执行
            if os.path.exists(picture_path):
                print("Displaying topology image")
                self.show_picture(self.topo_image_label, picture_path)
            else:
                print(f"Topology image not found: {picture_path}")  # 增加打印信息以便调试

    def show_circuit_image(self, show=False):
        """Display the saved equivalent circuit image."""
        circuit_picture_path = './picture/circuit.png'
        if show:  # 仅在 show 为 True 时执行
            if os.path.exists(circuit_picture_path):
                print("Displaying equivalent circuit image")
                self.show_picture(self.gds_image_label, circuit_picture_path)
            else:
                print(f"Circuit image not found: {circuit_picture_path}")  # 增加打印信息以便调试

    def show_gds_image(self, show=False):
        """Display the saved GDS layout."""
        try:
            self.design.gds.save_svg(path='./picture/gds.svg')  # 保存 GDS 图像为 SVG 文件
        except Exception as e:
            print(f"Failed to save GDS image: {e}")
            return

        gds_picture_path = './picture/gds.svg'
        if show:  # 仅在 show 为 True 时执行
            if os.path.exists(gds_picture_path):
                print("Displaying GDS image")
                self.show_picture(self.gds_image_label, gds_picture_path)
            else:
                print(f"GDS image not found: {gds_picture_path}")  # 增加打印信息以便调试

    def show_picture(self, label, picture_path):
        try:
            if not os.path.exists(picture_path):
                print(f"Error: Image file not found at {picture_path}")
                return

            # 清除Label内容
            label.clear()

            # 加载图片
            pixmap = QPixmap(picture_path)
            if pixmap.isNull():
                print(f"Error: Failed to load image from {picture_path}")
                return

            # 保持比例缩放图片
            scaled_pixmap = pixmap.scaled(
                label.size(),
                Qt.KeepAspectRatio,  # 保持原始宽高比
                Qt.SmoothTransformation  # 平滑缩放
            )

            # 设置图片到Label并居中显示
            label.setPixmap(scaled_pixmap)
            label.setAlignment(Qt.AlignCenter)  # 新增：强制居中

            print(f"Displayed image: {picture_path}")  # 保留原有日志

        except Exception as e:
            print(f"Failed to display image: {e}")  # 保留原有错误处理

    def _select_file(self):
        """打开文件对话框，选择 topo 文件并更新图像"""
        fileDialog = QFileDialog(self)
        fileDialog.setWindowTitle('请选择 topo 文件')
        fileDialog.setFileMode(QFileDialog.ExistingFiles)  # 设置选择模式为现有文件
        fileDialog.setNameFilter("QASM Files (*.qasm);;All Files (*);;Image Files (*.png *.jpg *.bmp *.svg)")  # 设置文件过滤器
        fileDialog.setViewMode(QFileDialog.List)  # 以列表形式展示文件

        if fileDialog.exec_() == QFileDialog.Accepted:  # 确认选择了文件
            file_paths = fileDialog.selectedFiles()  # 获取选择的所有文件
            if file_paths:  # 确保选择列表不为空
                file_path = file_paths[0]  # 选择第一个文件路径
                print(f"Selected file: {file_path}")

                # 更新设计并显示 topo 图像
                self.design = Design(qasm_path=file_path)
                self.show_topology_image(show=True)  # 显示更新后的 topo 图像

    def MenuAffairs(self, action_name):
        """Perform operations based on the action name."""
        if action_name == 'Algorithm':
            print("Executing algorithm customization operation")
            self._select_file()  # 调用 _select_file 方法执行选择文件操作
        elif action_name == 'Circuit':
            print("Executing equivalent circuit construction operation")
            self.design.generate_equivalent_circuit()
            self.design.equivalent_circuit.show()
        elif action_name == 'ChipLayer':
            print("Executing generate chip layer operation")
            self.chip_layer = Dialog_ChipLayer(design=self.design)
            self.chip_layer.designUpdated.connect(self.updateMainDesign)
            self.chip_layer.show()
        elif action_name == 'ReadingCavity':
            print("Executing generate reading cavity operation")
            self.RCavity = Dialog_RCavity(design=self.design)
            self.RCavity.designUpdated.connect(self.updateMainDesign)
            self.RCavity.show()
        elif action_name == 'GeneratePin':
            print("Executing generate pin operation")
            self.gener_pin = Dialog_pins(design=self.design)
            self.gener_pin.designUpdated.connect(self.updateMainDesign)
            self.gener_pin.show()
        elif action_name == 'GenerateLine':
            print("Executing generate line operation")
            self.show_circuit_image(show=True)  # Ensure to show updated image
        elif action_name == 'RoutingAlgorithm':
            print("Executing routing algorithm operation")
            self.ralgorithm_dialog = Dialog_RAlgorithm(design=self.design)
            self.ralgorithm_dialog.designUpdated.connect(self.updateMainDesign)
            self.ralgorithm_dialog.show()
        elif action_name == 'GDS':
            print("Executing GDS layout modification operation")
            self.gds_dialog = NestedDictViewer(design=self.design)
            self.gds_dialog.window_gds.designUpdated.connect(self.updateMainDesign)
            self.gds_dialog.show()
        elif action_name == 'Others':
            print("Executing other operation")
            self.other_dialog = Dialog_Others(design=self.design)
            self.other_dialog.designUpdated.connect(self.updateMainDesign)
            self.other_dialog.show()
        elif action_name == 'Clear':
            print("Executing clear operation")
            # 清除界面上的显示内容
            self.clear_display()

    def clear_display(self):
        """清除界面上的显示内容"""
        # 清除拓扑图显示
        self.topo_image_label.clear()
        self.topo_display.setText("Topo Interface")  # 重置显示文本

        # 清除GDS布局显示
        self.gds_image_label.clear()
        self.gds_display.setText("GDS Interface")  # 重置显示文本

        # # 清除项目管理器内容
        # self.project_manager.clear()
        # self.nested_dict = {}  # 清空项目数据

        # 重置设计数据
        self.design = Design()  # 重新初始化设计对象
        self.design_updated_flag = False  # 重置设计更新标志

        # 清除所有打开的对话框
        for dialog in self.findChildren(QDialog):
            dialog.close()

        print("界面内容已清除")


    @pyqtSlot(Design)  # Assuming Design is a QString type
    def updateMainDesign(self, updated_design):
        """Slot to update the design in the main window when received from Dialog_Topology."""
        self.design = updated_design
        self.design_updated_flag = True  # Set status flag to True
        print("Main window design has been updated")

        # Update images based on design changes
        if self.design_updated_flag:
            # 尝试显示 GDS 图像
            try:
                self.show_topology_image(show=True)  # Show updated topology image
                self.show_gds_image(show=True)  # Show updated GDS image
            except Exception as e:
                print(f"Failed to display image: {e}")  # Debug info for exceptions

    def create_project_manager(self):
        """Create project manager and its buttons"""
        self.project_manager = QTreeWidget()
        self.project_manager.setHeaderLabel("Project Manager")
        self.project_manager.setContextMenuPolicy(Qt.CustomContextMenu)
        self.project_manager.customContextMenuRequested.connect(self.show_context_menu)

        self.project_manager.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # 允许扩展

        # Add sample projects
        self.nested_dict = {
            'Project A': {
                'Subproject A1': {},
                'Subproject A2': {
                    'Subproject A2-1': {}
                }
            },
            'Project B': {}
        }
        self.populate_tree(self.nested_dict, self.project_manager)

        # Add buttons
        self.button_frame = QFrame()
        self.button_layout = QHBoxLayout()
        self.add_project_manager_buttons()

        self.button_frame.setLayout(self.button_layout)

        manager_layout = QVBoxLayout()
        manager_layout.addWidget(self.button_frame)
        manager_layout.addWidget(self.project_manager)

        manager_widget = QWidget()
        manager_widget.setLayout(manager_layout)
        return manager_widget

    def add_project_manager_buttons(self):
        """Add close and pin buttons to project manager"""
        close_button = QPushButton("❌")
        close_button.setToolTip("Close Project Manager")
        close_button.clicked.connect(self.close_project_manager)

        pin_button = QPushButton("📌")
        pin_button.setToolTip("Pin Project Manager")
        pin_button.clicked.connect(self.pin_project_manager)

        self.button_layout.addWidget(close_button)
        self.button_layout.addWidget(pin_button)

    def populate_tree(self, data, parent):
        """Populate tree widget with nested dictionary"""
        for key, value in data.items():
            item = QTreeWidgetItem(parent, [key])
            if isinstance(value, dict) and value:
                self.populate_tree(value, item)

    def show_context_menu(self, pos):
        """Show context menu on right click"""
        item = self.project_manager.itemAt(pos)  # 获取右键点击的项目
        context_menu = QMenu(self)

        # 添加右键菜单选项
        add_main_action = QAction("Add Main Project", self)
        add_main_action.triggered.connect(self.add_main_project)

        add_sub_action = QAction("Add Sub-Project", self)
        add_sub_action.triggered.connect(lambda: self.add_sub_project(item))  # 传递当前的选项项目

        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(lambda: self.delete_item(item))

        save_action = QAction("Save", self)
        save_action.triggered.connect(lambda: self.save_item(item))

        # 根据是否有选中项，决定是否禁用“Add Sub-Project”
        if item is None:
            add_sub_action.setEnabled(False)

            # 将选项添加到右键菜单
        context_menu.addAction(add_main_action)
        context_menu.addAction(add_sub_action)
        context_menu.addAction(delete_action)
        context_menu.addAction(save_action)

        # 弹出右键菜单
        context_menu.exec_(self.project_manager.viewport().mapToGlobal(pos))
    def delete_item(self, item):
        """Delete the selected item"""
        parent = item.parent()
        if parent:
            parent.removeChild(item)
        else:
            index = self.project_manager.indexOfTopLevelItem(item)
            if index != -1:
                self.project_manager.takeTopLevelItem(index)

    def save_item(self, item):
        """Save the selected item"""
        print(f"Saving item: {item.text(0)}")

    def add_main_project(self):
        """Add a new main project"""
        # Ensure QInputDialog is imported
        from PyQt5.QtWidgets import QInputDialog

        # Get the project name from the user
        new_project_name, ok = QInputDialog.getText(self, "New Main Project",
                                                    "Enter the name for the new main project:")
        if ok and new_project_name.strip():
            # Create a new top-level project item
            new_item = QTreeWidgetItem([new_project_name.strip()])
            self.project_manager.addTopLevelItem(new_item)  # Add to the top level of the tree
            print(f"Main project '{new_project_name}' added.")
        else:
            print("No project name entered, or creation was canceled.")

    def add_sub_project(self, parent_item):
        """Add a new sub-project under the selected project"""
        from PyQt5.QtWidgets import QInputDialog

        # Check if parent_item is valid
        if parent_item is None:
            QMessageBox.warning(self, "Error", "Please select a parent project first.")
            return

            # Prompt for sub-project name
        new_sub_project_name, ok = QInputDialog.getText(self, "New Sub-Project",
                                                        "Enter the name for the new sub-project:")

        # Only proceed if the input is valid
        if ok and new_sub_project_name.strip():
            # Create a new child item and add it to the parent item
            new_sub_item = QTreeWidgetItem(parent_item, [new_sub_project_name.strip()])
            parent_item.addChild(new_sub_item)
            parent_item.setExpanded(True)  # Expand to show the new child
            print(f"Sub-project '{new_sub_project_name}' added under '{parent_item.text(0)}'.")
        else:
            print("No sub-project name entered or operation was canceled.")

    def close_project_manager(self):
        self.project_manager.setVisible(False)

    def pin_project_manager(self):
        self.project_manager.setVisible(True)


    def new_action(self):
        print("New file created")

    def open_file(self):
        print("File opened")

    def save_file(self):
        print("File saved")

    def cut_action(self):
        print("Cut action performed")

    def copy_action(self):
        print("Copy action performed")

    def paste_action(self):
        print("Paste action performed")

    def zoom_in_action(self):
        print("Zoomed in")

    def zoom_out_action(self):
        print("Zoomed out")

    def add_project_action(self):
        print("Project added")

    def remove_project_action(self):
        print("Project removed")

    def settings_action(self):
        print("Settings opened")

    def options_action(self):
        print("Options opened")

    def documentation_action(self):
        print("Documentation opened")

    def about_action(self):
        print("About dialog opened")


if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = MyMainWindow()
    window.show()
    sys.exit(app.exec_())