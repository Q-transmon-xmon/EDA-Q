from PySide6 import QtCore, QtWidgets
from PySide6.QtGui import QFont
from api.design import Design
import sys


class RandomEdge_Dialog(QtWidgets.QDialog):
    # 定义一个信号，用于在设计更新后通知外部
    designUpdated = QtCore.Signal(object)

    def __init__(self, design, parent=None):
        super(RandomEdge_Dialog, self).__init__(parent)
        self.design = design
        self.num = None  # Initialize the num variable
        self.setupUi()

    def setupUi(self):
        self.setObjectName("Dialog")
        self.resize(400, 129)
        # 设置整个界面的字体为微软雅黑
        self.setFont(QFont("Microsoft YaHei", 10.5))
        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(290, 20, 81, 241))
        self.buttonBox.setOrientation(QtCore.Qt.Vertical)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.widget = QtWidgets.QWidget(self)
        self.widget.setGeometry(QtCore.QRect(10, 40, 223, 21))
        self.widget.setObjectName("widget")

        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.label = QtWidgets.QLabel(self.widget)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)

        self.lineEdit = QtWidgets.QLineEdit(self.widget)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout.addWidget(self.lineEdit)

        self.retranslateUi()
        self.buttonBox.accepted.connect(self.Process_RandomEdge)
        self.buttonBox.rejected.connect(self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Dialog", "随机化拓扑边设计"))
        self.label.setText(_translate("Dialog", "添加边的数目："))

    def Process_RandomEdge(self):
        """保存输入框的数值到 num 变量"""
        try:
            self.num = int(self.lineEdit.text())  # Convert input to an integer
            print(f"输入的边数：{self.num}")
            self.design.topology.generate_random_edges(self.num)
            # self.design.topology.show_image()

            # 发出信号，传递设计对象给外部
            self.designUpdated.emit(self.design)
            # 关闭窗口
            self.accept()

        except ValueError:
            QtWidgets.QMessageBox.warning(self, "输入错误", "请输入一个有效的整数。")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    # 假设有一个设计对象
    design = Design()  # 这里需要替换为实际的设计对象
    dialog = RandomEdge_Dialog(design)

    # 连接信号到一个函数以处理设计更新
    dialog.designUpdated.connect(lambda updated_design: print("设计更新已传回主窗口！"))
    dialog.exec()  # Show the dialog

    sys.exit(app.exec())