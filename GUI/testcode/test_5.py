import sys
import os

# Retrieve the directory where the current script is located
current_path = os.path.dirname(os.path.abspath(__file__))
GUI_PATH = os.path.dirname(current_path)
PROJ_PATH = os.path.dirname(GUI_PATH)

# Add path
sys.path.append(GUI_PATH)
sys.path.append(PROJ_PATH)

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot, Qt
from qfluentwidgets import *
from qframelesswindow import FramelessWindow
from GUI.Widget.Widget_topology import Dialog_Topology
from GUI.Widget.Widget_qubit import Dialog_Qubit
from GUI.Widget.Widget_chiplayer import Dialog_ChipLayer
from GUI.Widget.Widget_RAlgorithm import Dialog_RAlgorithm
from GUI.Widget.Widget_RCavity import Dialog_RCavity
from GUI.Widget.Widget_Gds import NestedDictViewer
from GUI.Widget.Widget_Simulation import Dialog_Simulation
from GUI.Widget.Widget_LineGenerate import Dialog_Line
from GUI.Widget.Widget_Pin import Dialog_pins
from GUI.Widget.Widget_Others import Dialog_Others
from api.design import Design


class MainWindow(FramelessWindow):

    def __init__(self, parent=None):
        super().__init__(parent)

        # Set the initial setting of the window design
        self.design = Design()


        # Limit the maximum and minimum size of the window
        self.setMinimumSize(QtCore.QSize(1420, 800))
        # self.setMaximumSize(QtCore.QSize(1920, 1080))

        # position
        self.move(100, 100)

        layout = QtWidgets.QVBoxLayout()

        # Menu List
        menu_layout = FlowLayout(needAni=False)
        menu_layout.setContentsMargins(50, 30, 50, 30)
        menu_layout.setVerticalSpacing(20)
        menu_layout.setHorizontalSpacing(20)

        # Custom Button
        btn1 = QtWidgets.QPushButton('算法定制拓扑')
        btn2 = QtWidgets.QPushButton('自定义拓扑')
        btn3 = QtWidgets.QPushButton('构建等效电路')
        btn4 = QtWidgets.QPushButton('生成量子比特')
        btn5 = QtWidgets.QPushButton('生成芯片层')
        btn6 = QtWidgets.QPushButton('生成读取腔')
        btn7 = QtWidgets.QPushButton('生成引脚')  # Add button，Placed after generating the reading cavity
        btn8 = QtWidgets.QPushButton('生成线')
        btn9 = QtWidgets.QPushButton('布线算法')
        btn10 = QtWidgets.QPushButton('GDS版图修改')
        btn11 = QtWidgets.QPushButton('仿真')
        btn12 = QtWidgets.QPushButton('Others')  # newly addedOthersbutton，Placed after simulation
        btn13 = QtWidgets.QPushButton('清空')

        # Set button name
        btn1.setObjectName('Algorithm')
        btn2.setObjectName('Topology')
        btn3.setObjectName('Circuit')
        btn4.setObjectName('Qubit')
        btn5.setObjectName('ChipLayer')
        btn6.setObjectName('ReadingCavity')
        btn7.setObjectName('GeneratePin')  # Generate the name of the pin button
        btn8.setObjectName('GenerateLine')
        btn9.setObjectName('RoutingAlgorithm')
        btn10.setObjectName('GDS')
        btn11.setObjectName('Simulation')
        btn12.setObjectName('Others')  # OthersThe name of the button
        btn13.setObjectName('Clear')

        # Binding button event
        btn1.clicked.connect(self._select_file)
        btn2.clicked.connect(self.MenuAffairs)
        btn3.clicked.connect(self.MenuAffairs)
        btn4.clicked.connect(self.MenuAffairs)
        btn5.clicked.connect(self.MenuAffairs)
        btn6.clicked.connect(self.MenuAffairs)
        btn7.clicked.connect(self.MenuAffairs)  # Event binding for adding buttons
        btn8.clicked.connect(self.MenuAffairs)
        btn9.clicked.connect(self.MenuAffairs)
        btn10.clicked.connect(self.MenuAffairs)
        btn11.clicked.connect(self.MenuAffairs)
        btn12.clicked.connect(self.MenuAffairs)  # bindingOthersbutton event
        btn13.clicked.connect(self.MenuAffairs)

        # Add buttons to the layout
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

        # Layout of the right content area
        vBoxLayout = QtWidgets.QVBoxLayout()
        self.pivot = SegmentedWidget()
        self.stackedWidget = QtWidgets.QStackedWidget()

        # Create different interfaces
        topoInterface = QtWidgets.QLabel('topo Interface')
        CircuitInterface = QtWidgets.QLabel('Circuit Interface')
        GDSInterface = QtWidgets.QLabel('GDS Interface')

        self.topoface = topoInterface
        self.circuitface = CircuitInterface
        self.gdsface = GDSInterface

        # Add sub interface
        self.addSubInterface(topoInterface, 'topoInterface', 'topo')
        # self.addSubInterface(CircuitInterface, 'CircuitInterface', 'Circuit')
        self.addSubInterface(GDSInterface, 'GDSInterface', 'GDS')

        # Add to Layout
        vBoxLayout.addWidget(self.pivot)
        vBoxLayout.addWidget(self.stackedWidget)
        vBoxLayout.setContentsMargins(30, 10, 30, 30)

        # Switching between monitoring interfaces
        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)
        self.stackedWidget.setCurrentWidget(topoInterface)
        self.pivot.setCurrentItem(topoInterface.objectName())

        # Add zoom in button
        self.zoomButton = QtWidgets.QPushButton("放大")
        self.zoomButton.setFixedSize(60, 30)
        self.zoomButton.setStyleSheet("position: absolute; bottom: 10px; right: 10px;")
        self.zoomButton.clicked.connect(self.onZoomButtonClicked)  # Bind click event
        vBoxLayout.addWidget(self.zoomButton, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)

        # self.setLayout(vBoxLayout)

        # Left navigation bar
        hBoxLayout = QtWidgets.QHBoxLayout()

        view = TreeView()
        model = QtWidgets.QFileSystemModel()
        model.setRootPath('.')
        view.setModel(model)
        view.setBorderVisible(True)
        view.setBorderRadius(8)

        hBoxLayout.addWidget(view)
        hBoxLayout.setContentsMargins(30, 20, 200, 30)

        # layout
        layout.addLayout(menu_layout)
        content_layout = QtWidgets.QHBoxLayout()
        content_layout.addLayout(hBoxLayout)
        content_layout.addLayout(vBoxLayout)
        layout.addLayout(content_layout)
        self.setLayout(layout)

        # Style definition（Adjust the style at the end！！）
        self.setStyleSheet('*{background:rgb(255,255,255)} QPushButton{padding: 5px 10px; font:13px "Microsoft YaHei"}')

        self.design_updated_flag = False  # Add status flag

    def onZoomButtonClicked(self):
        # Get the current interface
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
        # Implement hereTopoThe logic of enlarging the interface
        self.design.topology.show_image()

    def zoomCircuitInterface(self):
        print("放大Circuit界面")
        # Implement hereCircuitThe logic of enlarging the interface
        self.design.equivalent_circuit.show()

    def zoomGDSInterface(self):
        print("放大GDS界面")
        # Implement hereGDSThe logic of enlarging the interface
        self.design.gds.show_gds()


    def MenuAffairs(self, checked):
        sender = self.sender()
        # Ensure that each window object is saved as an instance variable of the class
        if sender.objectName() == 'Topology':
            print('自定义拓扑')
            self.page_topology = Dialog_Topology(design=self.design)
            self.page_topology.designUpdated.connect(self.updateMainDesign)
            self.page_topology.show()
        elif sender.objectName() == 'Circuit':
            print('构建等效电路')
            self.design.generate_equivalent_circuit()
            self.design.equivalent_circuit.show()
            # Not useful at the moment
            # self.show_circuit_image()  # Only displayed when clicked on the panel
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
            self.design=Design()


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
            # print("Currently, no images have been generated！")
            return  # If the design has not been updated，Direct Return，Do not perform subsequent operations

        if objectName == 'topoInterface':
            print("显示拓扑图像")
            self.show_topology_image(show=True)  # Only displayed when this interface is activated
        elif objectName == 'CircuitInterface':
            print("显示等效电路图像")
            self.show_circuit_image(show=True)  # Only displayed when this interface is activated
        elif objectName == 'GDSInterface':
            print("显示GDS图像")
            self.show_gds_image(show=True)  # Only displayed when this interface is activated

    def _select_file(self, checked):
        fileDialog = QtWidgets.QFileDialog(self)
        fileDialog.setWindowTitle('请选择文件')
        fileDialog.setFileMode(QtWidgets.QFileDialog.FileMode.AnyFile)
        file_path, _ = fileDialog.getOpenFileName()
        print(file_path)
        self.design = Design(qasm_path=file_path)
        # self.design.topology.show_image()  # This part can be adjusted，See if it is necessary
        self.show_topology_image(show=True)

    @Slot(Design)
    def updateMainDesign(self, updated_design):
        """Slot to update the design in the main window when received from Dialog_Topology."""
        self.design = updated_design
        self.design_updated_flag = True  # Set the status flag to True
        print("主窗口的设计已更新")
        # It may not be necessary to call the display image here
        self.show_topology_image(show=True)
        # self.show_gds_image(show=True)

    def resetDesignUpdatedFlag(self):
        """Reset design update flag，Usually called after the design is used。"""
        self.design_updated_flag = False

    def show_topology_image(self, show=False):
        # Save topology image
        self.design.topology.save_image(path='./picture/topology.png')
        picture_path = './picture/topology.png'  # Image path
        if show and os.path.exists(picture_path):
            print("显示拓扑图像")
            self.show_picture(self.topoface, picture_path)
            # self.resetDesignUpdatedFlag()

    def show_circuit_image(self, show=False):
        # Display the saved equivalent circuit image
        # self.design.equivalent_circuit.save_image(path='./picture/circuit.png')
        circuit_picture_path = './picture/circuit.png'
        if show and os.path.exists(circuit_picture_path):
            print("显示等效电路图像")
            self.show_picture(self.circuitface, circuit_picture_path)
            self.resetDesignUpdatedFlag()

    def show_gds_image(self, show=False):
        # display GDS territory
        self.design.gds.save_svg(path='./picture/gds.svg')
        gds_picture_path = './picture/gds.svg'
        if show and os.path.exists(gds_picture_path):
            print("显示GDS图像")
            self.show_picture(self.gdsface, gds_picture_path)
            # self.show_topology_image(show=True)
            self.resetDesignUpdatedFlag()

    def show_picture(self, label, picture_path):
        label.resize(500, 500)  # ensurelabelThe size is sufficient to display the image
        label.setPixmap(QtGui.QPixmap(picture_path))
        print(f"显示图片: {picture_path}")  # debug information，Confirm the path of the displayed image


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()