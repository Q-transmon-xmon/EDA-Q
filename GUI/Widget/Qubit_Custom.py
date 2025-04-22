import sys
from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import QDialog, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QWidget, QDialogButtonBox, QComboBox
from PySide6.QtCore import QCoreApplication, QMetaObject, QRect, QSettings
from api.design import Design
import math


class Ui_Dialog_Qubit_Custom:
    def setupUi(self, Dialog_Qubit_Custom):
        if not Dialog_Qubit_Custom.objectName():
            Dialog_Qubit_Custom.setObjectName("Dialog_Qubit_Custom")
        Dialog_Qubit_Custom.resize(400, 350)

        self.buttonBox = QDialogButtonBox(Dialog_Qubit_Custom)
        self.buttonBox.setGeometry(QRect(30, 280, 341, 32))
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)

        self.layoutWidget = QWidget(Dialog_Qubit_Custom)
        self.layoutWidget.setGeometry(QRect(40, 40, 331, 200))
        self.verticalLayout = QVBoxLayout(self.layoutWidget)

        # 创建标签和输入框
        self.createLabeledInput("量子比特数目：")
        self.createLabeledInput("距离：")
        self.createLabeledInput("芯片层：")

        # 添加量子比特类型选择
        self.addQubitTypeSelection()

        self.retranslateUi(Dialog_Qubit_Custom)

        # 连接信号与槽
        QMetaObject.connectSlotsByName(Dialog_Qubit_Custom)

    def createLabeledInput(self, label_text):
        """创建一个标签和相应的输入框，并将它们添加到布局中"""
        horizontalLayout = QHBoxLayout()
        label = QLabel(label_text)
        line_edit = QLineEdit()

        horizontalLayout.addWidget(label)
        horizontalLayout.addWidget(line_edit)
        self.verticalLayout.addLayout(horizontalLayout)

        # 将输入框添加到实例变量中，以便后续访问
        if not hasattr(self, 'lineEdits'):
            self.lineEdits = []
        self.lineEdits.append(line_edit)

    def addQubitTypeSelection(self):
        """添加量子比特类型选择"""
        horizontalLayout = QHBoxLayout()
        label = QLabel("量子比特类型：")
        self.qubit_type_combo = QComboBox()
        self.qubit_type_combo.addItems(["Xmon", "Transmon"])

        horizontalLayout.addWidget(label)
        horizontalLayout.addWidget(self.qubit_type_combo)
        self.verticalLayout.addLayout(horizontalLayout)

    def retranslateUi(self, Dialog_Qubit_Custom):
        Dialog_Qubit_Custom.setWindowTitle(QCoreApplication.translate("Dialog_Qubit_Custom", "生成量子比特"))


class Dialog_Qubit_Custom(QDialog, Ui_Dialog_Qubit_Custom):
    designUpdated = QtCore.Signal(object)

    def __init__(self, design):
        super(Dialog_Qubit_Custom, self).__init__()
        self.setupUi(self)

        # Store the passed design parameter
        self.design = design

        # QSettings 用于保存和加载输入的数据
        self.settings = QSettings("MyCompany", "MyApp")

        # 读取上一次保存的输入内容并显示
        self.loadPreviousInputs()

        # 连接按钮的信号
        self.buttonBox.accepted.connect(self.Process_Qubit)
        self.buttonBox.rejected.connect(self.reject)  # 连接取消按钮到 QDialog 的 reject 方法

    def loadPreviousInputs(self):
        """加载上一次保存的输入内容"""
        self.lineEdits[0].setText(self.settings.value("quantum_bits", "", type=str))
        self.lineEdits[1].setText(self.settings.value("distance", "", type=str))
        self.lineEdits[2].setText(self.settings.value("thickness", "", type=str))

    def Process_Qubit(self):
        """保存输入框的文本到 QSettings"""
        self.settings.setValue("quantum_bits", self.lineEdits[0].text())
        self.settings.setValue("distance", self.lineEdits[1].text())
        self.settings.setValue("thickness", self.lineEdits[2].text())

        quantum_bits = self.settings.value("quantum_bits", "", type=int)
        distance = self.settings.value("distance", "", type=int)
        thickness = self.settings.value("thickness", "", type=str)
        qubit_type = self.qubit_type_combo.currentText()

        print(f"量子比特数目: {quantum_bits}")
        print(f"距离: {distance}")
        print(f"芯片层: {thickness}")
        print(f"选择的量子比特类型: {qubit_type}")

        self.design.generate_topology(qubits_num=quantum_bits, topo_col=int(math.sqrt(quantum_bits)))
        self.design.generate_qubits(chip_name=thickness, dist=distance, qubits_type=qubit_type,
                                    topo_positions=self.design.topology.positions)
        # 发出设计更新信号
        self.designUpdated.emit(self.design)

        # 关闭对话框
        self.accept()  # 关闭对话框


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    design = Design()  # 创建 Design 实例
    dialog = Dialog_Qubit_Custom(design=design)  # 将 design 实例传递给 Dialog_Qubit_Custom

    # 更新主设计的信号
    def updateMainDesign(updated_design):
        print("主窗口设计已更新")
    dialog.designUpdated.connect(updateMainDesign)

    # 如果对话框接受，显示输入内容
    if dialog.exec() == QDialog.Accepted:
        dialog.design.gds.show_svg()

    # 退出应用程序
    sys.exit(app.exec())