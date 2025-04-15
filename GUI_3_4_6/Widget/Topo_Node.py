import sys
from PySide6 import QtWidgets, QtCore
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QWidget
from PySide6.QtCore import QSettings, Signal
from api.design import Design


class Ui_Dialog_Node:
    def setupUi(self, Dialog_Node):
        if not Dialog_Node.objectName():
            Dialog_Node.setObjectName("Dialog_Node")
        Dialog_Node.resize(400, 250)

        # 设置整个界面的字体为微软雅黑
        Dialog_Node.setFont(QFont("Microsoft YaHei", 10.5))
        # 创建主布局用于居中
        self.mainLayout = QVBoxLayout(Dialog_Node)

        # 占位，用来将内容在垂直方向居中
        self.mainLayout.addStretch()

        # 创建布局窗口组件
        self.layoutWidget = QWidget(Dialog_Node)
        self.verticalLayout = QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setSpacing(15)  # 设置输入框之间的间距

        # 创建标签和输入框
        self.lineEdits = []
        # q0_ops
        #
        # for key, value in q0_ops:

        self.createLabeledInput("量子比特数目：")
        self.createLabeledInput("行数：")
        self.createLabeledInput("列数：")

        # 添加中间部件到主布局中
        self.mainLayout.addWidget(self.layoutWidget)

        # 创建按钮并设置对齐方式
        self.buttonBox = QDialogButtonBox(Dialog_Node)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)  # 使按钮居中
        self.buttonBox.setMinimumSize(0, 40)  # 设置按钮的最小高度
        self.mainLayout.addWidget(self.buttonBox)

        # 占位，用来将内容在垂直方向居中
        self.mainLayout.addStretch()

        self.retranslateUi(Dialog_Node)

        # 连接信号与槽
        self.buttonBox.accepted.connect(lambda: Dialog_Node.Process_Node())
        self.buttonBox.accepted.connect(Dialog_Node.accept)
        self.buttonBox.rejected.connect(Dialog_Node.reject)

    def createLabeledInput(self, label_text):
        """创建一个标签和相应的输入框，并将它们添加到布局中"""
        layout = QHBoxLayout()
        label = QLabel(label_text)
        line_edit = QLineEdit()

        layout.addWidget(label)
        layout.addWidget(line_edit)
        self.verticalLayout.addLayout(layout)
        self.lineEdits.append(line_edit)  # 保存对输入框的引用

    def retranslateUi(self, Dialog_Node):
        _translate = QtCore.QCoreApplication.translate
        Dialog_Node.setWindowTitle(_translate("Dialog", "拓扑节点生成"))  # Set the window title here


class Dialog_Node(QDialog, Ui_Dialog_Node):
    # 定义信号
    designUpdated = Signal(object)

    def __init__(self, design):
        super(Dialog_Node, self).__init__()
        self.setupUi(self)

        self.design = design  # Store the design object

        # QSettings 用于保存和加载输入的数据
        self.settings = QSettings("MyCompany", "MyApp")
        # self.loadPreviousInputs()
    # def loadPreviousInputs(self):
    #     """加载上一次保存的输入内容"""
    #     self.lineEdits[0].setText(self.settings.value("quantum_bits", "", type=str))
    #     self.lineEdits[1].setText(self.settings.value("rows", "", type=str))
    #     self.lineEdits[2].setText(self.settings.value("columns", "", type=str))

    def Process_Node(self):


        """保存输入框的文本到 QSettings"""
        self.settings.setValue("quantum_bits", self.lineEdits[0].text())
        self.settings.setValue("rows", self.lineEdits[1].text())
        self.settings.setValue("columns", self.lineEdits[2].text())

        self.lineEdits[0].setText(self.settings.value("quantum_bits", "", type=str))
        self.lineEdits[1].setText(self.settings.value("rows", "", type=str))
        self.lineEdits[2].setText(self.settings.value("columns", "", type=str))

        totalnum = self.settings.value("quantum_bits", type=int)
        rows = self.settings.value("rows", "", type=int)
        cols = self.settings.value("columns", "", type=int)

        print(f"量子比特数目: {totalnum}")
        print(f"行数: {rows}")
        print(f"列数: {cols}")

        # 使用存储的设计对象
        self.design.generate_topology(topo_col=cols, topo_row=rows)
        # self.design.generate_random_edges()
        # self.design.topology.show_image()
        # 发出设计更新后的信号
        self.designUpdated.emit(self.design)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    design = Design()  # Instantiate 'Design' before passing to the dialog
    dialog = Dialog_Node(design=design)

    dialog.designUpdated.connect(lambda updated_design: print("设计更新已传回主窗口！"))

    dialog.exec()  # Run the dialog

    sys.exit(app.exec())