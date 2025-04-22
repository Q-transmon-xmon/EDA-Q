import sys
from PySide6 import QtCore, QtWidgets
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QDialog, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QPushButton, QMessageBox
from api.design import Design


class Ui_Dialog:
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(411, 251)
        # 设置整个界面的字体为微软雅黑
        Dialog.setFont(QFont("Microsoft YaHei", 10.5))
        # Main layout to hold all components
        self.mainLayout = QVBoxLayout(Dialog)

        # First input row
        self.horizontalLayout = QHBoxLayout()
        self.label = QLabel("q0_name ：", Dialog)
        self.horizontalLayout.addWidget(self.label)
        self.lineEdit = QLineEdit(Dialog)
        self.horizontalLayout.addWidget(self.lineEdit)

        # Second input row
        self.horizontalLayout_2 = QHBoxLayout()
        self.label_2 = QLabel("q1_name ：", Dialog)
        self.horizontalLayout_2.addWidget(self.label_2)
        self.lineEdit_2 = QLineEdit(Dialog)
        self.horizontalLayout_2.addWidget(self.lineEdit_2)

        # Add input rows to the main layout
        self.mainLayout.addLayout(self.horizontalLayout)
        self.mainLayout.addLayout(self.horizontalLayout_2)

        # Buttons
        self.buttonLayout = QHBoxLayout()
        self.pushButton = QPushButton("Add", Dialog)
        self.buttonLayout.addWidget(self.pushButton)
        self.pushButton_2 = QPushButton("Delete", Dialog)
        self.buttonLayout.addWidget(self.pushButton_2)

        # Add button layout to the main layout
        self.mainLayout.addLayout(self.buttonLayout)

        self.retranslateUi(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "自定义生成边"))  # Set the window title here


class CustomEdge_Dialog(QDialog, Ui_Dialog):
    # 定义一个信号，用于在设计更新后通知外部
    designUpdated = QtCore.Signal(object)

    def __init__(self, design, parent=None):
        super(CustomEdge_Dialog, self).__init__(parent)
        self.setupUi(self)
        self.design = design  # Store the design object

        # Connect buttons to their respective methods
        self.pushButton.clicked.connect(self.add_edge)
        self.pushButton_2.clicked.connect(self.delete_edge)

    def add_edge(self):
        q0_name = self.lineEdit.text()
        q1_name = self.lineEdit_2.text()

        # Check if the qubit names are valid
        if not self.validate_qubit_names(q0_name, q1_name):
            return

        # Implement the logic for adding an edge using the design object
        print(f"Adding edge between {q0_name} and {q1_name}")
        self.design.topology.add_edge(q0_name, q1_name)

        # 发出设计更新后的信号
        self.designUpdated.emit(self.design)

    def delete_edge(self):
        q0_name = self.lineEdit.text()
        q1_name = self.lineEdit_2.text()

        # Check if the qubit names are valid
        if not self.validate_qubit_names(q0_name, q1_name):
            return

        # Implement the logic for deleting an edge using the design object
        print(f"Deleting edge between {q0_name} and {q1_name}")
        self.design.topology.remove_edge([q0_name, q1_name])

        # 发出设计更新后的信号
        self.designUpdated.emit(self.design)

    def validate_qubit_names(self, q0_name, q1_name):
        # Check if the qubit names exist in the topology
        valid_qubits = self.design.topology.positions.keys()
        if q0_name not in valid_qubits or q1_name not in valid_qubits:
            QMessageBox.critical(self, "Error", "Invalid qubit name(s). Please enter valid qubit names.")
            return False
        return True


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    design = Design()  # Instantiate the Design object
    dialog = CustomEdge_Dialog(design=design)

    # 连接信号到一个函数以处理设计更新
    def updateMainDesign(updated_design):
        print("主函数设计已更新")

    dialog.designUpdated.connect(updateMainDesign)
    dialog.exec()
    sys.exit(app.exec())