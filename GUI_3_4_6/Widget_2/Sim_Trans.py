import sys
import os

# 获取当前脚本所在的目录
current_path = os.path.dirname(os.path.abspath(__file__))
GUI_PATH = os.path.dirname(current_path)
PROJ_PATH = os.path.dirname(GUI_PATH)

# 添加路径
sys.path.append(GUI_PATH)
sys.path.append(PROJ_PATH)

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QDialog, QLabel, QLineEdit, QVBoxLayout,
                             QPushButton, QMessageBox, QHBoxLayout, QWidget, QDialogButtonBox)
from PyQt5.QtCore import Qt, QSettings, pyqtSignal
from api.design import Design
from GUI_3_4_6.Widget_2.Show_Dataframe import DataFrameDisplay


class Ui_Dialog:
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setMinimumSize(400, 300)  # Set minimum size of the dialog
        Dialog.setFont(QFont("Microsoft YaHei", 10))

        # Main layout
        self.mainLayout = QVBoxLayout(Dialog)
        self.mainLayout.addStretch(1)

        # Title label
        titleLabel = QLabel("Transmon Parameter Configuration")
        titleLabel.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        titleLabel.setAlignment(Qt.AlignCenter)
        self.mainLayout.addWidget(titleLabel)

        # Instruction label
        instructionsLabel = QLabel("Please enter the parameters below:")
        instructionsLabel.setAlignment(Qt.AlignCenter)
        self.mainLayout.addWidget(instructionsLabel)

        # Input section
        self.layoutWidget = QWidget(Dialog)
        self.verticalLayout = QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setSpacing(20)
        self.verticalLayout.setContentsMargins(20, 20, 20, 20)

        self.defaults = ["q0", "5.6"]  # Default values
        self.lineEdits = []

        self.createLabeledInput("Qubit Name:", self.defaults[0])
        self.createLabeledInput("Qubit Frequency:", self.defaults[1])

        self.mainLayout.addWidget(self.layoutWidget)

        # Button box
        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(self.buttonBox.button(QDialogButtonBox.Ok))
        buttonLayout.addWidget(self.buttonBox.button(QDialogButtonBox.Cancel))

        self.mainLayout.addLayout(buttonLayout)
        self.mainLayout.addStretch(1)

    def createLabeledInput(self, label_text, default_value):
        """Create a labeled input field"""
        layout = QHBoxLayout()  # Create layout for each input item
        label = QLabel(label_text)
        label.setFixedWidth(150)  # Set label width
        line_edit = QLineEdit()
        line_edit.setMinimumWidth(200)
        line_edit.setPlaceholderText(default_value)  # Set default value
        layout.addWidget(label)
        layout.addWidget(line_edit)
        self.verticalLayout.addLayout(layout)  # Add to vertical layout
        self.lineEdits.append(line_edit)  # Save the input field

    def get_line_edits(self):
        return self.lineEdits


class Dialog_Transmon(QDialog):
    designUpdated = pyqtSignal(object)  # Define signal to notify design update

    def __init__(self, design):
        super().__init__()
        self.design = design
        self.settings = QSettings("MyCompany", "MyApp")

        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # Connect signals
        self.ui.buttonBox.accepted.connect(self.checkInputs)  # OK button
        self.ui.buttonBox.rejected.connect(self.reject)  # Cancel button
        # 初始化矩阵对话框为 None
        self.matrix_dialog = None
        # Install event filter for input fields
        for line_edit in self.ui.get_line_edits():
            line_edit.installEventFilter(self)

    def eventFilter(self, source, event):
        """Handle Tab key events to set default values"""
        if event.type() == QtCore.QEvent.KeyPress and event.key() == Qt.Key_Tab:
            for line_edit in self.ui.get_line_edits():
                if line_edit.hasFocus():
                    # Set default value if input field is empty
                    if line_edit.text().strip() == "":
                        line_edit.setText(line_edit.placeholderText())
                    # Move to the next input field
                    next_index = self.ui.get_line_edits().index(line_edit) + 1
                    if next_index < len(self.ui.get_line_edits()):
                        self.ui.get_line_edits()[next_index].setFocus()
                    return True  # Prevent further processing
        return super().eventFilter(source, event)

    def checkInputs(self):
        inputs = []
        for i, line_edit in enumerate(self.ui.get_line_edits()):
            value = line_edit.text().strip() or self.ui.defaults[i]
            if not value:  # Check value
                QMessageBox.critical(self, "Input Error", "All fields must be filled out. Please enter valid values.")
                return
            inputs.append(value)

        self.processNode(inputs)

    def processNode(self, inputs):
        self.settings.setValue("Qubit_name", inputs[0])
        self.settings.setValue("Qubit_freq", inputs[1])

        print(f"Qubit Name: {inputs[0]}")
        print(f"Qubit Frequency: {inputs[1]}")

        # Execute design-related operations
        self.design.simulation(sim_module="TransmonSim", frequency=inputs[1], qubit_name=inputs[0])
        self.designUpdated.emit(self.design)  # Emit design updated signal
        self.accept()  # Close the dialog
        # 在对话框关闭后显示矩阵窗口
        self.show_matrix_display()

    def show_matrix_display(self):
        """显示矩阵窗口"""
        file_path = 'C:/sim_proj/transmon_sim/capacitance_matrix.txt'

        # 检查文件是否存在
        if not os.path.exists(file_path):
            print(f"文件 {file_path} 不存在，无法显示矩阵窗口")
            return

        print('xianshi')

            # 创建并显示 DataFrameDisplay 窗口
        self.matrix_dialog = DataFrameDisplay(file_path=file_path)
        self.matrix_dialog.exec()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    design = Design()  # Instantiate design object
    dialog = Dialog_Transmon(design=design)  # Create dialog

    dialog.designUpdated.connect(
        lambda updated_design: print("Design Updated Back to Main Window!"))  # Connect signal
    dialog.exec_()  # Show dialog

    sys.exit(app.exec_())