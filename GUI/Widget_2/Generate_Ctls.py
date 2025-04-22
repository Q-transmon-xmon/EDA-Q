import ast
import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QDialog, QLabel, QLineEdit, QHBoxLayout,
                             QVBoxLayout, QDialogButtonBox, QMessageBox, QPushButton)
from PyQt5.QtCore import Qt
from addict import Dict
from api.design import Design  # 假设这是你的设计模块

class Dialog_ctls(QDialog):
    # Define a signal for design updates
    designUpdated = QtCore.pyqtSignal(object)

    def __init__(self, design, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Control Line Configuration")
        self.setFont(QFont("Microsoft YaHei", int(10)))  # Set font for the dialog
        self.resize(650, 400)
        self.design = design

        # Default values for input fields
        self.default_values = Dict(
            name="charge_line0",
            type="ChargeLine",
            chip="chip0",
            outline=[],  # 新增参数
            pos=[[0, 0], [0, 100]],  # 替换 path 参数
            width=15,  # 改为单值
            gap=5,  # 改为单值
            pad_width=15,  # 新增参数
            pad_height=25,  # 新增参数
            distance=50,  # 新增参数
            corner_radius=20
        )

        # Store input fields and types
        self.lineEdits = {}
        self.input_types = {}

        # Main layout
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(20, 20, 20, 20)  # Set margins for the main layout
        self.mainLayout.setSpacing(15)  # Set spacing between controls in the layout

        # Title label
        titleLabel = QLabel("Control Line Configuration")
        titleLabel.setFont(QFont("Arial", 14, QFont.Bold))
        titleLabel.setAlignment(Qt.AlignCenter)
        self.mainLayout.addWidget(titleLabel)

        # Instructions label
        instructionsLabel = QLabel("Please enter the control line details below:")
        instructionsLabel.setAlignment(Qt.AlignCenter)
        self.mainLayout.addWidget(instructionsLabel)

        # Dynamically generate input fields with default values
        self.loadInputs()

        # Button layout
        self.createButtonLayout()

    def loadInputs(self):
        """Dynamically generate input fields with default values"""
        labels = {
            "name": "Control Line Name:",
            "type": "Type:",
            "chip": "Chip Name:",
            "outline": "Outline (Optional):",
            "pos": "Position Points:",
            "width": "Line Width (μm):",
            "gap": "Gap (μm):",
            "pad_width": "Pad Width (μm):",
            "pad_height": "Pad Height (μm):",
            "distance": "Distance (μm):",
            "corner_radius": "Corner Radius (μm):"
        }

        for key, value in self.default_values.items():
            # Create horizontal layout for each input field
            layout = QHBoxLayout()

            # Create label
            label = QLabel(f"{labels[key]}")
            label.setFixedWidth(150)  # Set fixed width for alignment
            layout.addWidget(label)

            # Create input field with placeholder text
            line_edit = QLineEdit()
            line_edit.setPlaceholderText(str(value))  # Set default value as placeholder
            layout.addWidget(line_edit)

            # Store input field and type
            self.lineEdits[key] = line_edit
            self.input_types[key] = type(value)

            # Add to the main layout
            self.mainLayout.addLayout(layout)

            # Connect the event to allow using Tab to accept the default value
            line_edit.installEventFilter(self)  # Install an event filter for the line edit

        self.mainLayout.addStretch()  # Add stretch to push the layout to the top

    def eventFilter(self, source, event):
        """Event filter for handling Tab key to set default values"""
        if event.type() == QtCore.QEvent.KeyPress and event.key() == QtCore.Qt.Key_Tab:
            for key, line_edit in self.lineEdits.items():
                if line_edit.hasFocus():
                    # Set text to placeholder value on Tab press
                    if line_edit.text().strip() == "":
                        line_edit.setText(line_edit.placeholderText())
                    # Move to the next input field
                    next_index = list(self.lineEdits.keys()).index(key) + 1
                    if next_index < len(self.lineEdits):
                        next_line_edit = self.lineEdits[list(self.lineEdits.keys())[next_index]]
                        next_line_edit.setFocus()
                    return True
        return super().eventFilter(source, event)

    def createButtonLayout(self):
        """Create and set up the button layout"""
        buttonLayout = QHBoxLayout()
        okButton = QPushButton("OK")
        cancelButton = QPushButton("Cancel")

        # Set button sizes
        okButton.setFixedSize(80, 30)
        cancelButton.setFixedSize(80, 30)

        # Add buttons to layout with proper alignment
        buttonLayout.addStretch()  # Add space before buttons to right-align
        buttonLayout.addWidget(okButton)
        buttonLayout.addWidget(cancelButton)

        # Add button layout to the main layout
        self.mainLayout.addLayout(buttonLayout)

        # Connect button events
        okButton.clicked.connect(self.processInputs)  # OK button
        cancelButton.clicked.connect(self.reject)  # Cancel button

    def processInputs(self):
        options = Dict()
        valid_input = True

        for key, line_edit in self.lineEdits.items():
            value_str = line_edit.text() or line_edit.placeholderText()

            try:
                if key == "pos":
                    # 解析二维坐标列表
                    converted_value = ast.literal_eval(value_str.strip())
                    if not isinstance(converted_value, list):
                        raise ValueError("必须为二维列表格式")
                    for i, point in enumerate(converted_value):
                        if not (isinstance(point, list) and len(point) == 2):
                            raise ValueError(f"第 {i + 1} 个坐标点格式错误")
                        x, y = point
                        if not (isinstance(x, (int, float)) and isinstance(y, (int, float))):
                            raise ValueError(f"第 {i + 1} 个坐标点包含非数字值")
                    options.pos = converted_value

                elif key == "outline":
                    # 可选参数，允许空列表
                    converted_value = ast.literal_eval(value_str.strip()) if value_str else []
                    if not isinstance(converted_value, list):
                        raise ValueError("必须为列表格式")
                    options.outline = converted_value

                elif key in ["width", "gap", "pad_width", "pad_height", "distance", "corner_radius"]:
                    # 数值类型验证
                    converted_value = float(value_str)
                    if converted_value <= 0:
                        raise ValueError("必须大于0")
                    options[key] = converted_value

                else:
                    # 字符串类型直接保存
                    options[key] = value_str.strip()

            except Exception as e:
                QMessageBox.warning(self, "输入错误", f"{key} 参数错误: {str(e)}")
                valid_input = False
                break

        if valid_input:
            self.design.gds.control_lines.add(options=options)
            self.designUpdated.emit(self.design)
            self.accept()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    # Create and display dialog
    dialog = Dialog_ctls(design=Design())
    if dialog.exec() == QDialog.Accepted:
        print("Dialog accepted")

    # Exit the application
    sys.exit(app.exec())