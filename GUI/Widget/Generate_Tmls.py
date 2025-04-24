import sys
from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox)
from addict import Dict
from api.design import Design

class Dialog_tmls(QDialog):
    # Define a signal for design updates
    designUpdated = QtCore.Signal(object)
    def __init__(self, design,parent=None):
        super().__init__(parent)
        self.setWindowTitle("Transmission_line")
        self.setFont(QFont("Microsoft YaHei", 10.5))
        self.resize(600, 400)
        self.design = design
        # Pre-defined dictionary templates
        self.tml_ops_template = Dict(
            name="tmls0",
            type="TransmissionPath",
            chip_name="chip0",
            pos=[(-1000, 1100), (-1000, 1250), (15000, 1250), (15000, 1000)],
            corner_radius=90
        )

        # Friendly label mapping
        self.labels = {
            "name": "名称",
            "type": "类型",
            "chip_name": "芯片层",
            "pos": "位置",
            "corner_radius": "半径"
        }

        self.process_function = self.default_process_function  # Default processing function
        self.lineEdits = {}  # Store the input box corresponding to each key
        self.input_types = {}  # Store the type of each key

        # Main layout
        self.mainLayout = QVBoxLayout(self)

        # Dynamically load dictionary template
        self.loadDictionary()

        # add button
        self.buttonLayout = QHBoxLayout()
        self.processButton = QPushButton("添加")
        self.cancelButton = QPushButton("取消")

        # Set button size
        self.processButton.setFixedSize(80, 30)
        self.cancelButton.setFixedSize(80, 30)

        self.buttonLayout.addWidget(self.processButton)
        self.buttonLayout.addWidget(self.cancelButton)
        self.buttonLayout.setAlignment(Qt.AlignRight)  # right alignment
        self.mainLayout.addLayout(self.buttonLayout)

        # Connection button event
        self.processButton.clicked.connect(self.processDictionary)
        self.cancelButton.clicked.connect(self.reject)

    def loadDictionary(self):
        """Dynamically load dictionary template and generate input box"""
        for key, value in self.tml_ops_template.items():
            # Create horizontal layout
            layout = QHBoxLayout()

            # create label
            label = QLabel(f"{self.labels[key]}：")  # Use friendly tags
            layout.addWidget(label)

            # Create input box
            line_edit = QLineEdit()
            line_edit.setText(str(value))  # Set default values
            layout.addWidget(line_edit)

            # Save input box and type
            self.lineEdits[key] = line_edit
            self.input_types[key] = type(value)

            # Add to main layout
            self.mainLayout.addLayout(layout)

    def processDictionary(self):
        """Process user input and call processing functions"""
        valid_input = True
        updated_dict = Dict()

        for key, line_edit in self.lineEdits.items():
            value_str = line_edit.text()
            expected_type = self.input_types[key]

            try:
                # Convert input values based on type
                if expected_type == list:
                    # If it is a list type，Attempt to parse as Python list
                    converted_value = eval(value_str)
                    if not isinstance(converted_value, list):
                        raise ValueError("输入值不是有效的列表")
                elif expected_type == tuple:
                    # If it is a tuple type，Attempt to parse as Python tuple
                    converted_value = eval(value_str)
                    if not isinstance(converted_value, tuple):
                        raise ValueError("输入值不是有效的元组")
                else:
                    converted_value = expected_type(value_str)

                updated_dict[key] = converted_value  # Save to the updated dictionary
            except (ValueError, SyntaxError) as e:
                QMessageBox.warning(self, "无效输入", f"{self.labels[key]} 的输入无效: {e}")
                valid_input = False
                break

        if valid_input:
            # Call processing function
            self.process_function(updated_dict)
            self.accept()  # close dialog boxes

    def default_process_function(self, tml_ops):
        """
        Default processing function，Receive the dictionary input by the user as a parameter
        :param tml_ops: Dictionary inputted by the user
        """
        print("处理后的字典：", tml_ops)
        self.design.gds.transmission_lines.add(options=tml_ops)
        self.designUpdated.emit(self.design)  # Send design update signal

        # Add your processing logic here
        # QMessageBox.information(None, "Processing completed", f"Dictionary processed：\n{tml_ops}")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    design = Design()
    design.generate_topology(topo_col=4, topo_row=4)
    design.generate_qubits(topology=True, qubits_type='Xmon')
    # Create and display a dialog box
    dialog = Dialog_tmls(design=design)
    dialog.exec()

    sys.exit(app.exec())