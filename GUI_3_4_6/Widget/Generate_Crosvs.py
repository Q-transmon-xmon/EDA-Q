import sys
from PySide6 import QtCore, QtWidgets
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QDialog, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QDialogButtonBox
from PySide6.QtCore import QCoreApplication, QMetaObject, QSettings
from api.design import Design
class Ui_Dialog:
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName("Dialog")
        Dialog.resize(400, 150)
        # 设置整个界面的字体为微软雅黑
        Dialog.setFont(QFont("Microsoft YaHei", 10.5))
        # 创建主垂直布局
        self.mainLayout = QVBoxLayout(Dialog)
        self.mainLayout.setContentsMargins(20, 20, 20, 20)  # 设置主布局的边距
        self.mainLayout.setSpacing(15)  # 设置布局内控件之间的间距

        # 创建一个布局用于输入框
        self.inputLayout = QVBoxLayout()
        self.inputLayout.setSpacing(10)  # 设置输入框布局内控件之间的间距

        # 创建标签和输入框
        self.createLabeledInput("芯片层名称:")

        # 将输入框布局添加到主布局中
        self.mainLayout.addLayout(self.inputLayout)

        # 创建按钮框
        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.mainLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)

        # 连接信号与槽
        QMetaObject.connectSlotsByName(Dialog)

    def createLabeledInput(self, label_text):
        """创建一个标签和相应的输入框，并将它们添加到布局中"""
        horizontalLayout = QHBoxLayout()
        label = QLabel(label_text)
        line_edit = QLineEdit()

        horizontalLayout.addWidget(label)
        horizontalLayout.addWidget(line_edit)
        self.inputLayout.addLayout(horizontalLayout)

        # 将输入框添加到实例变量中，以便后续访问
        if not hasattr(self, 'lineEdits'):
            self.lineEdits = []
        self.lineEdits.append(line_edit)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", "Crossover_lines"))

class Dialog_crosvs(QDialog, Ui_Dialog):

    designUpdated = QtCore.Signal(object)
    def __init__(self,design):
        super(Dialog_crosvs, self).__init__()
        self.setupUi(self)
        self.design = design
        # QSettings 用于保存和加载输入的数据
        self.settings = QSettings("MyCompany", "MyApp")

        # 读取默认值并显示
        self.loadPreviousInputs()

        # 连接按钮的信号
        self.buttonBox.accepted.connect(self.processInputs)
        self.buttonBox.rejected.connect(self.reject)  # 连接取消按钮到 QDialog 的 reject 方法

    def loadPreviousInputs(self):
        """加载默认值"""
        defaults = {
            "chip_layer_name": "chip0"
        }
        keys = ["chip_layer_name"]
        for i, key in enumerate(keys):
            self.lineEdits[i].setText(defaults[key])  # 直接设置默认值

    def processInputs(self):
        """保存输入框的文本到 QSettings并转换为适当的类型"""
        keys = ["chip_layer_name"]
        for i, key in enumerate(keys):
            self.settings.setValue(key, self.lineEdits[i].text())

        # 将输入的参数保存为不同类型的变量
        chip_layer_name = self.settings.value("chip_layer_name", "", type=str)

        # 打印输入的值
        print(f"Chip Layer Name: {chip_layer_name}")
        self.design.generate_cross_overs(coupling_lines=True, transmission_lines=True, chip_name=chip_layer_name)
        self.designUpdated.emit(self.design)
        # 关闭对话框
        self.accept()  # 关闭对话框

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    dialog = Dialog_crosvs(design=Design())

    # 如果对话框接受，显示输入内容
    if dialog.exec() == QDialog.Accepted:
        print("Dialog accepted")

    # 退出应用程序
    sys.exit(app.exec())