import sys
import os

# 获取当前脚本所在的目录
current_path = os.path.dirname(os.path.abspath(__file__))
GUI_PATH = os.path.dirname(current_path)
PROJ_PATH = os.path.dirname(GUI_PATH)

# 添加路径
sys.path.append(GUI_PATH)
sys.path.append(PROJ_PATH)

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot, Qt
from qfluentwidgets import *
from GUI_3_4_6.Widget.Widget_topology import Dialog_Topology
from GUI_3_4_6.Widget.Widget_qubit import Dialog_Qubit
from GUI_3_4_6.Widget.Widget_chiplayer import Dialog_ChipLayer
from GUI_3_4_6.Widget.Widget_RAlgorithm import Dialog_RAlgorithm
from GUI_3_4_6.Widget.Widget_RCavity import Dialog_RCavity
from GUI_3_4_6.Widget.Widget_Gds import NestedDictViewer
from GUI_3_4_6.Widget.Widget_Simulation import Dialog_Simulation
from GUI_3_4_6.Widget.Widget_LineGenerate import Dialog_Line
from GUI_3_4_6.Widget.Widget_Pin import Dialog_pins
from GUI_3_4_6.Widget.Widget_Others import Dialog_Others
from api.design import Design


class MainWindow(QtWidgets.QMainWindow):  # 更改为 QMainWindow


    def __init__(self, parent=None):
        super().__init__(parent)

        # 设置窗口的初始 design
        self.design = Design()

        # 限制窗口的最大最小尺寸
        self.setMinimumSize(QtCore.QSize(1420, 800))

        # 位置
        self.move(100, 100)

        # 创建菜单栏
        self.create_menu_bar()

        layout = QtWidgets.QVBoxLayout()

        # 菜单列表
        menu_layout = FlowLayout(needAni=False)
        menu_layout.setContentsMargins(50, 30, 50, 30)
        menu_layout.setVerticalSpacing(20)
        menu_layout.setHorizontalSpacing(20)

        # 定义按钮
        btn1 = QtWidgets.QPushButton('算法定制拓扑')
        btn2 = QtWidgets.QPushButton('自定义拓扑')
        btn3 = QtWidgets.QPushButton('构建等效电路')
        btn4 = QtWidgets.QPushButton('生成量子比特')
        btn5 = QtWidgets.QPushButton('生成芯片层')
        btn6 = QtWidgets.QPushButton('生成读取腔')
        btn7 = QtWidgets.QPushButton('生成引脚')
        btn8 = QtWidgets.QPushButton('生成线')
        btn9 = QtWidgets.QPushButton('布线算法')
        btn10 = QtWidgets.QPushButton('GDS版图修改')
        btn11 = QtWidgets.QPushButton('仿真')
        btn12 = QtWidgets.QPushButton('Others')
        btn13 = QtWidgets.QPushButton('清空')

        # 设置按钮名称
        btn1.setObjectName('Algorithm')
        btn2.setObjectName('Topology')
        btn3.setObjectName('Circuit')
        btn4.setObjectName('Qubit')
        btn5.setObjectName('ChipLayer')
        btn6.setObjectName('ReadingCavity')
        btn7.setObjectName('GeneratePin')
        btn8.setObjectName('GenerateLine')
        btn9.setObjectName('RoutingAlgorithm')
        btn10.setObjectName('GDS')
        btn11.setObjectName('Simulation')
        btn12.setObjectName('Others')
        btn13.setObjectName('Clear')

        # 绑定按钮事件
        btn1.clicked.connect(self._select_file)
        btn2.clicked.connect(self.MenuAffairs)
        btn3.clicked.connect(self.MenuAffairs)
        btn4.clicked.connect(self.MenuAffairs)
        btn5.clicked.connect(self.MenuAffairs)
        btn6.clicked.connect(self.MenuAffairs)
        btn7.clicked.connect(self.MenuAffairs)
        btn8.clicked.connect(self.MenuAffairs)
        btn9.clicked.connect(self.MenuAffairs)
        btn10.clicked.connect(self.MenuAffairs)
        btn11.clicked.connect(self.MenuAffairs)
        btn12.clicked.connect(self.MenuAffairs)
        btn13.clicked.connect(self.MenuAffairs)

        # 将按钮添加到布局
        menu_layout.addWidget(btn1)
        menu_layout.addWidget(btn2)
        menu_layout.addWidget(btn3)
        menu_layout.addWidget(btn4)
        menu_layout.addWidget(btn5)
        menu_layout.addWidget(btn6)
        menu_layout.addWidget(btn7)
        menu_layout.addWidget(btn8)
        menu_layout.addWidget(btn9)
        menu_layout.addWidget(btn10)
        menu_layout.addWidget(btn11)
        menu_layout.addWidget(btn12)
        menu_layout.addWidget(btn13)

        # 右侧内容区域布局
        vBoxLayout = QtWidgets.QVBoxLayout()
        self.pivot = SegmentedWidget()
        self.stackedWidget = QtWidgets.QStackedWidget()

        # 创建不同的界面
        topoInterface = QtWidgets.QLabel('topo Interface')
        CircuitInterface = QtWidgets.QLabel('Circuit Interface')
        GDSInterface = QtWidgets.QLabel('GDS Interface')

        self.topoface = topoInterface
        self.circuitface = CircuitInterface
        self.gdsface = GDSInterface

        # 添加子界面
        self.addSubInterface(topoInterface, 'topoInterface', 'topo')
        self.addSubInterface(GDSInterface, 'GDSInterface', 'GDS')

        # 添加到布局
        vBoxLayout.addWidget(self.pivot)
        vBoxLayout.addWidget(self.stackedWidget)
        vBoxLayout.setContentsMargins(30, 10, 30, 30)

        # 监听界面切换
        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)
        self.stackedWidget.setCurrentWidget(topoInterface)
        self.pivot.setCurrentItem(topoInterface.objectName())

        # 添加放大按钮
        self.zoomButton = QtWidgets.QPushButton("放大")
        self.zoomButton.setFixedSize(60, 30)
        self.zoomButton.setStyleSheet("position: absolute; bottom: 10px; right: 10px;")
        self.zoomButton.clicked.connect(self.onZoomButtonClicked)  # 绑定点击事件
        vBoxLayout.addWidget(self.zoomButton, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)

        # 左侧导航栏
        hBoxLayout = QtWidgets.QHBoxLayout()

        view = TreeView()
        model = QtWidgets.QFileSystemModel()
        model.setRootPath('.')
        view.setModel(model)
        view.setBorderVisible(True)
        view.setBorderRadius(8)

        hBoxLayout.addWidget(view)
        hBoxLayout.setContentsMargins(30, 20, 200, 30)

        # 布局
        layout.addLayout(menu_layout)
        content_layout = QtWidgets.QHBoxLayout()
        content_layout.addLayout(hBoxLayout)
        content_layout.addLayout(vBoxLayout)
        layout.addLayout(content_layout)

        # 设置中心窗口
        central_widget = QtWidgets.QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # 式样定义（式样最后再调！！）
        self.setStyleSheet('*{background:rgb(255,255,255)} QPushButton{padding: 5px 10px; font:13px "Microsoft YaHei"}')

        self.design_updated_flag = False  # 添加状态标志

    def create_menu_bar(self):
        # 创建菜单栏
        menu_bar = QtWidgets.QMenuBar(self)

        # 添加菜单项
        file_menu = menu_bar.addMenu("File")
        edit_menu = menu_bar.addMenu("Edit")
        view_menu = menu_bar.addMenu("View")
        project_menu = menu_bar.addMenu("Project")
        tools_menu = menu_bar.addMenu("Tools")
        window_menu = menu_bar.addMenu("Window")
        help_menu = menu_bar.addMenu("Help")

        # 添加菜单项的示例
        file_menu.addAction("New", self.new_file)
        file_menu.addAction("Open", self.open_file)
        file_menu.addAction("Save", self.save_file)
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)

        edit_menu.addAction("Undo")
        edit_menu.addAction("Redo")

        view_menu.addAction("Show Toolbar")
        view_menu.addAction("Show Status Bar")

        project_menu.addAction("Manage Projects")

        tools_menu.addAction("Settings")

        window_menu.addAction("Minimize", self.showMinimized)
        window_menu.addAction("Maximize", self.showMaximized)

        help_menu.addAction("About")

        self.setMenuBar(menu_bar)

    def new_file(self):
        print("新建文件")

    def open_file(self):
        print("打开文件")

    def save_file(self):
        print("保存文件")

    def onZoomButtonClicked(self):
        # 获取当前界面
        currentWidget = self.stackedWidget.currentWidget()
        if currentWidget == self.topoface:
            self.zoomTopoInterface()
        elif currentWidget == self.circuitface:
            self.zoomCircuitInterface()
        elif currentWidget == self.gdsface:
            self.zoomGDSInterface()
        else:
            print("未知界面")

    def zoomTopoInterface(self):
        print("放大Topo界面")
        self.design.topology.show_image()

    def zoomCircuitInterface(self):
        print("放大Circuit界面")
        self.design.equivalent_circuit.show()

    def zoomGDSInterface(self):
        print("放大GDS界面")
        self.design.gds.show_gds()

    def MenuAffairs(self, checked):
        sender = self.sender()
        if sender.objectName() == 'Topology':
            print('自定义拓扑')
            self.page_topology = Dialog_Topology(design=self.design)
            self.page_topology.designUpdated.connect(self.updateMainDesign)
            self.page_topology.show()
        elif sender.objectName() == 'Circuit':
            print('构建等效电路')
            self.design.generate_equivalent_circuit()
            self.design.equivalent_circuit.show()
        elif sender.objectName() == 'Qubit':
            print('生成量子比特')
            self.page_qubit = Dialog_Qubit(design=self.design)
            self.page_qubit.designUpdated.connect(self.updateMainDesign)
            self.page_qubit.show()
        elif sender.objectName() == 'ChipLayer':
            print('生成芯片层')
            self.page_chiplayer = Dialog_ChipLayer(design=self.design)
            self.page_chiplayer.designUpdated.connect(self.updateMainDesign)
            self.page_chiplayer.show()
        elif sender.objectName() == 'ReadingCavity':
            print('生成读取腔')
            self.page_readingcavity = Dialog_RCavity(design=self.design)
            self.page_readingcavity.designUpdated.connect(self.updateMainDesign)
            self.page_readingcavity.show()
        elif sender.objectName() == 'GeneratePin':
            print('生成引脚')
            self.page_pins = Dialog_pins(design=self.design)
            self.page_pins.designUpdated.connect(self.updateMainDesign)
            self.page_pins.show()
        elif sender.objectName() == 'GenerateLine':
            print('生成线')
            self.page_generateline = Dialog_Line(design=self.design)
            self.page_generateline.designUpdated.connect(self.updateMainDesign)
            self.page_generateline.show()
        elif sender.objectName() == 'RoutingAlgorithm':
            print('布线算法')
            self.page_Ralogrithm = Dialog_RAlgorithm(design=self.design)
            self.page_Ralogrithm.designUpdated.connect(self.updateMainDesign)
            self.page_Ralogrithm.show()
        elif sender.objectName() == 'GDS':
            print('GDS版图修改')
            self.page_gds = NestedDictViewer(design=self.design)
            self.page_gds.window_gds.designUpdated.connect(self.updateMainDesign)
            self.page_gds.show()
        elif sender.objectName() == 'Simulation':
            print('仿真')
            self.page_simulation = Dialog_Simulation(design=self.design)
            self.page_simulation.designUpdated.connect(self.updateMainDesign)
            self.page_simulation.show()
        elif sender.objectName() == 'Others':
            print('Others')
            self.page_other = Dialog_Others(design=self.design)
            self.page_other.designUpdated.connect(self.updateMainDesign)
            self.page_other.show()
        elif sender.objectName() == 'Clear':
            print('清空')
            self.design = Design()

    def addSubInterface(self, widget: QtWidgets.QLabel, objectName, text):
        widget.setObjectName(objectName)
        widget.setAlignment(Qt.AlignCenter)
        self.stackedWidget.addWidget(widget)
        self.pivot.addItem(
            routeKey=objectName,
            text=text,
            onClick=lambda: self.stackedWidget.setCurrentWidget(widget) or self.onFaceClicked(objectName),
        )

    def onCurrentIndexChanged(self, index):
        widget = self.stackedWidget.widget(index)
        self.pivot.setCurrentItem(widget.objectName())

    def onFaceClicked(self, objectName):
        if not self.design_updated_flag:
            return

        if objectName == 'topoInterface':
            print("显示拓扑图像")
            self.show_topology_image(show=True)
        elif objectName == 'CircuitInterface':
            print("显示等效电路图像")
            self.show_circuit_image(show=True)
        elif objectName == 'GDSInterface':
            print("显示GDS图像")
            self.show_gds_image(show=True)

    def _select_file(self, checked):
        fileDialog = QtWidgets.QFileDialog(self)
        fileDialog.setWindowTitle('请选择文件')
        fileDialog.setFileMode(QtWidgets.QFileDialog.FileMode.AnyFile)
        file_path, _ = fileDialog.getOpenFileName()
        print(file_path)
        self.design = Design(qasm_path=file_path)
        self.show_topology_image(show=True)

    @Slot(Design)
    def updateMainDesign(self, updated_design):
        self.design = updated_design
        self.design_updated_flag = True
        print("主窗口的设计已更新")
        self.show_topology_image(show=True)

    def resetDesignUpdatedFlag(self):
        self.design_updated_flag = False

    def show_topology_image(self, show=False):
        self.design.topology.save_image(path='./picture/topology.png')
        picture_path = './picture/topology.png'
        if show and os.path.exists(picture_path):
            print("显示拓扑图像")
            self.show_picture(self.topoface, picture_path)

    def show_circuit_image(self, show=False):
        circuit_picture_path = './picture/circuit.png'
        if show and os.path.exists(circuit_picture_path):
            print("显示等效电路图像")
            self.show_picture(self.circuitface, circuit_picture_path)
            self.resetDesignUpdatedFlag()

    def show_gds_image(self, show=False):
        self.design.gds.save_svg(path='./picture/gds.svg')
        gds_picture_path = './picture/gds.svg'
        if show and os.path.exists(gds_picture_path):
            print("显示GDS图像")
            self.show_picture(self.gdsface, gds_picture_path)
            self.resetDesignUpdatedFlag()

    def show_picture(self, label, picture_path):
        label.resize(500, 500)
        label.setPixmap(QtGui.QPixmap(picture_path))
        print(f"显示图片: {picture_path}")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()