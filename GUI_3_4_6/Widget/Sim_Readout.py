from PySide6.QtCore import (QCoreApplication, QMetaObject, QRect, Signal, QSettings, Qt)
from PySide6.QtWidgets import (QDialog, QDialogButtonBox, QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QGroupBox,
                               QApplication)
from api.design import Design

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(500, 400)  # 增加对话框的高度

        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(50, 340, 400, 32))  # 调整按钮框的位置
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)

        self.groupBox = QGroupBox("仿真参数", Dialog)  # 使用 QGroupBox 作为参数框
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(20, 70, 460, 260))  # 调整参数框的位置和大小
        self.groupBox.setStyleSheet("QGroupBox { border: 1px solid black; border-radius: 5px; padding: 10px; }")  # 设置边框样式

        self.verticalLayout = QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setSpacing(15)  # 增加垂直布局的间距
        self.verticalLayout.setContentsMargins(10, 10, 10, 10)  # 设置内容边距

        # 添加模式的标签和输入框
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")
        self.horizontalLayout.addWidget(self.label_3)

        self.lineEdit = QLineEdit(self.groupBox)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setMinimumHeight(30)  # 设置输入框的最小高度
        self.horizontalLayout.addWidget(self.lineEdit)
        self.verticalLayout.addLayout(self.horizontalLayout)

        # 添加 pin0 名称的标签和输入框
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_5 = QLabel(self.groupBox)
        self.label_5.setObjectName(u"label_5")
        self.horizontalLayout_3.addWidget(self.label_5)

        self.lineEdit_3 = QLineEdit(self.groupBox)
        self.lineEdit_3.setObjectName(u"lineEdit_3")
        self.lineEdit_3.setMinimumHeight(30)  # 设置输入框的最小高度
        self.horizontalLayout_3.addWidget(self.lineEdit_3)
        self.verticalLayout.addLayout(self.horizontalLayout_3)

        # 添加 pin1 名称的标签和输入框
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_7 = QLabel(self.groupBox)
        self.label_7.setObjectName(u"label_7")
        self.horizontalLayout_5.addWidget(self.label_7)

        self.lineEdit_5 = QLineEdit(self.groupBox)
        self.lineEdit_5.setObjectName(u"lineEdit_5")
        self.lineEdit_5.setMinimumHeight(30)  # 设置输入框的最小高度
        self.horizontalLayout_5.addWidget(self.lineEdit_5)
        self.verticalLayout.addLayout(self.horizontalLayout_5)

        # 添加读取线名称的标签和输入框
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_4 = QLabel(self.groupBox)
        self.label_4.setObjectName(u"label_4")
        self.horizontalLayout_2.addWidget(self.label_4)

        self.lineEdit_2 = QLineEdit(self.groupBox)
        self.lineEdit_2.setObjectName(u"lineEdit_2")
        self.lineEdit_2.setMinimumHeight(30)  # 设置输入框的最小高度
        self.horizontalLayout_2.addWidget(self.lineEdit_2)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        # 添加传输线名称的标签和输入框
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label_8 = QLabel(self.groupBox)
        self.label_8.setObjectName(u"label_8")
        self.horizontalLayout_6.addWidget(self.label_8)

        self.lineEdit_6 = QLineEdit(self.groupBox)
        self.lineEdit_6.setObjectName(u"lineEdit_6")
        self.lineEdit_6.setMinimumHeight(30)  # 设置输入框的最小高度
        self.horizontalLayout_6.addWidget(self.lineEdit_6)
        self.verticalLayout.addLayout(self.horizontalLayout_6)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", "ReadoutSim", None))
        self.label_3.setText(QCoreApplication.translate("Dialog", "模式：", None))
        self.label_5.setText(QCoreApplication.translate("Dialog", "pin0名称：", None))
        self.label_7.setText(QCoreApplication.translate("Dialog", "pin1名称：", None))
        self.label_4.setText(QCoreApplication.translate("Dialog", "读取线名称：", None))
        self.label_8.setText(QCoreApplication.translate("Dialog", "传输线名称：", None))


class Dialog_s21(QDialog):
    designUpdated = Signal(object)

    def __init__(self, design):
        super(Dialog_s21, self).__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # 设置样式
        self.setStyleSheet("""  
            QWidget {  
                background-color: #f0f0f0;  
                border-radius: 5px;  
                font-family: 'Microsoft YaHei';  
                font-size: 14px;  
                color: #333333;  
            }  
            QLineEdit {  
                background: white;  /* 白色背景 */  
                border: none;  /* 无边框 */  
                border-radius: 4px;  
                padding: 6px 6px;  
            }  
            QPushButton {  
                background-color: #4CAF50;  
                color: white;  
                padding: 8px 16px;  
                border: 1px solid #45a49;   
                border-radius: 4px;  
            }  
            QPushButton:hover {  
                background-color: #45a049;  
            }  
        """)

        # 存储传入的设计参数
        self.design = design

        # 使用 QSettings 保存和加载输入的数据
        self.settings = QSettings("MyCompany", "MyApp")

        # 读取上一次保存的输入内容并显示
        self.loadPreviousInputs()

        # 连接按钮的信号
        self.ui.buttonBox.accepted.connect(self.process_inputs)
        self.ui.buttonBox.rejected.connect(self.reject)

    def loadPreviousInputs(self):
        """加载上一次保存的输入内容"""
        self.ui.lineEdit.setText(self.settings.value("model_param", "", type=str))
        self.ui.lineEdit_3.setText(self.settings.value("pin0_name", "", type=str))
        self.ui.lineEdit_5.setText(self.settings.value("pin1_name", "", type=str))
        self.ui.lineEdit_2.setText(self.settings.value("read_line_name", "", type=str))
        self.ui.lineEdit_6.setText(self.settings.value("tml_name", "", type=str))

    def process_inputs(self):
        """保存输入框的文本到 QSettings,并发出 designUpdated 信号"""
        self.settings.setValue("model_param", self.ui.lineEdit.text())
        self.settings.setValue("pin0_name", self.ui.lineEdit_3.text())
        self.settings.setValue("pin1_name", self.ui.lineEdit_5.text())
        self.settings.setValue("read_line_name", self.ui.lineEdit_2.text())
        self.settings.setValue("tml_name", self.ui.lineEdit_6.text())

        # 示例参数处理
        model_param = self.settings.value("model_param", "", type=str)
        pin0_name = self.settings.value("pin0_name", "", type=str)
        pin1_name = self.settings.value("pin1_name", "", type=str)
        read_line_name = self.settings.value("read_line_name", "", type=str)
        tml_name = self.settings.value("tml_name", "", type=str)

        print(f"模型参数: {model_param}")
        print(f"pin0名称: {pin0_name}")
        print(f"pin1名称: {pin1_name}")
        print(f"读取线名称: {read_line_name}")
        print(f"传输线名称: {tml_name}")

        self.design.simulation(sim_module="s21", mode=model_param, pin0_name=pin0_name, pin1_name=pin1_name, rdl_name=read_line_name, tml_name=tml_name)
        # 发出设计更新信号
        self.designUpdated.emit(self.design)
        self.accept()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    design = Design()  # 在这里假设 design 是一个字典或相应的对象
    dialog = Dialog_s21(design)  # 创建 Dialog_s21 实例并传入设计参数

    def updateMainDesign(updated_design):
        print("主设计已更新")

    dialog.designUpdated.connect(updateMainDesign)

    if dialog.exec() == QDialog.Accepted:
        print("对话框接受，对话框中的输入已处理")

    sys.exit(app.exec())