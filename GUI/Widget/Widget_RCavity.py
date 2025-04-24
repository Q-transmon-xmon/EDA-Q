import sys
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import QCoreApplication, QMetaObject, QSettings, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QDialog, QDialogButtonBox, QHBoxLayout, QLabel,
                               QLineEdit, QVBoxLayout, QMessageBox, QFrame)
from addict import Dict
from api.design import Design


class Ui_Dialog_Rcavity(object):
    def setupUi(self, Dialog_Rcavity):
        if not Dialog_Rcavity.objectName():
            Dialog_Rcavity.setObjectName("Dialog_Rcavity")
        Dialog_Rcavity.resize(600, 500)
        # Set the font of the entire interface to Microsoft Yahei
        Dialog_Rcavity.setFont(QFont("Microsoft YaHei", 10.5))
        self.verticalLayout = QVBoxLayout(Dialog_Rcavity)
        self.verticalLayout.setContentsMargins(10, 10, 10, 10)

        # create rdls_type Input box
        self.rdlsLayout = QHBoxLayout()
        self.rdlsLabel = QLabel("读取腔类型：")
        self.rdlsLineEdit = QLineEdit()
        self.rdlsLineEdit.setText("ReadoutCavity")  # Set default values
        self.rdlsLayout.addWidget(self.rdlsLabel)
        self.rdlsLayout.addWidget(self.rdlsLineEdit)
        self.verticalLayout.addLayout(self.rdlsLayout)

        # Create a chip layer name input box
        self.chipLayerLayout = QHBoxLayout()  # Add Layout
        self.chipLayerLabel = QLabel("芯片层名称：")  # Add tags
        self.chipLayerLineEdit = QLineEdit()  # Add input box
        self.chipLayerLineEdit.setText("chip0")  # Set default values
        self.chipLayerLayout.addWidget(self.chipLayerLabel)  # Add tags to layout
        self.chipLayerLayout.addWidget(self.chipLayerLineEdit)  # Add input box to layout
        self.verticalLayout.addLayout(self.chipLayerLayout)  # Add layout to main layout

        # Create a gray frame to display the dictionary section
        self.dictFrame = QFrame(Dialog_Rcavity)
        self.dictFrame.setFrameShape(QFrame.StyledPanel)
        self.dictFrame.setStyleSheet("QFrame { border: 2px solid gray; border-radius: 5px; }")
        self.dictFrameLayout = QVBoxLayout(self.dictFrame)
        self.dictFrameLayout.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout.addWidget(self.dictFrame)

        # Create button boxes and add them to the layout
        self.buttonBox = QDialogButtonBox(Dialog_Rcavity)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.verticalLayout.addWidget(self.buttonBox)

        # Initialize the list of input boxes and labels for storage
        self.lineEdits = []  # storage QLineEdit List of
        self.labels = []  # List of Storage Tags

        self.retranslateUi(Dialog_Rcavity)
        QMetaObject.connectSlotsByName(Dialog_Rcavity)

    def addInputField(self, label_text, default_value=None):
        """Add tags and input boxes to the dictionary box"""
        horizontalLayout = QHBoxLayout()
        label = QLabel(label_text)
        line_edit = QLineEdit()
        if default_value is not None:
            line_edit.setText(str(default_value))  # Set default values
        horizontalLayout.addWidget(label)
        horizontalLayout.addWidget(line_edit)
        self.dictFrameLayout.addLayout(horizontalLayout)  # Add to the layout of the dictionary box
        self.lineEdits.append(line_edit)  # Save reference to input box
        self.labels.append(label_text)  # Save tag reference

    def retranslateUi(self, Dialog_Rcavity):
        Dialog_Rcavity.setWindowTitle(QCoreApplication.translate("Dialog_Rcavity", "生成读取腔"))


class Dialog_RCavity(QtWidgets.QDialog, Ui_Dialog_Rcavity):
    designUpdated = QtCore.Signal(object)

    def __init__(self, design):
        super().__init__()
        self.setupUi(self)
        self.design = design
        self.settings = QSettings("MyCompany", "MyApp")

        # definition geometric_options The default value
        self.geometric_options = Dict(
            coupling_length=300,  # Coupling line length
            width=10,  # Coupling line width
            gap=5,  # Coupling line etching width
            outline=[],  # Outer contour
            height=600,  # cpw height
            finger_length=100,  # Finger length
            finger_orientation=90,  # Finger direction
            start_dir="top",  # cpw Initial turning direction
            start_length=30,  # The length of the straight line near the quantum bit
            length=3000,  # Total length of coupling line
            space_dist=60,  # Distance between adjacent turns
            radius=30,  # Coupling line corner radius
            cpw_orientation=90  # cpw face
        )
        self.input_types = []  # Store the type of each parameter
        self.loadPreviousInput()
        self.buttonBox.accepted.connect(self.process_RCavity)
        self.buttonBox.rejected.connect(self.reject)

    def loadPreviousInput(self):
        """dynamic loading geometric_options All contents in the dictionary，And display default values"""
        self.lineEdits = []  # Clear the input box list
        self.labels = []  # Clear tag list
        self.input_types = []  # Clear the input type list

        for key, default_value in self.geometric_options.items():
            # Dynamically add tags and input boxes
            label_text = f"{key.replace('_', ' ').capitalize()}："  # Format label text
            self.addInputField(label_text, default_value)

            # Save default values to QSettings，If it has not been saved before，Then use default values
            value = self.settings.value(key, default_value)
            try:
                # Attempt to convert the value to the default value type
                converted_value = type(default_value)(value)
                self.lineEdits[-1].setText(str(converted_value))  # Set default values for input boxes
            except (ValueError, TypeError):
                self.lineEdits[-1].setText(str(default_value))  # If the conversion fails，Use default values

            # Save tags and input types
            self.input_types.append(type(default_value))

    def process_RCavity(self):
        """Process user input and generate geometric_options dictionary"""
        geometric_options = Dict()
        valid_input = True

        # obtain rdls_type The value of
        rdls_type = self.rdlsLineEdit.text()  # obtain rdls_type The value of
        chip_layer_name = self.chipLayerLineEdit.text()  # Obtain the value of the chip layer name

        for i, label in enumerate(self.labels):
            key = label[:-1].replace(' ', '_').lower()  # Convert tags to dictionary keys
            value_str = self.lineEdits[i].text()
            expected_type = self.input_types[i]

            try:
                # Convert input values based on type
                if expected_type == list:
                    # If it is a list type，Attempt to parse as Python list
                    converted_value = eval(value_str)
                    if not isinstance(converted_value, list):
                        raise ValueError("输入值不是有效的列表")
                else:
                    converted_value = expected_type(value_str)

                geometric_options[key] = converted_value  # Save to dictionary
            except (ValueError, SyntaxError) as e:
                QMessageBox.warning(self, "无效输入", f"{label} 输入无效: {e}")
                valid_input = False
                break

        if valid_input:
            # save to QSettings
            for key, value in geometric_options.items():
                self.settings.setValue(key, value)

            # Call the design generation method
            self.design.generate_readout_lines(qubits=True, rdls_type=rdls_type, chip_name=chip_layer_name, geometric_options=geometric_options)

            # Send design update signal
            self.designUpdated.emit(self.design)
            self.accept()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    design = Design()
    design.generate_topology(topo_col=4, topo_row=4)
    design.generate_qubits(topology=True, qubits_type='Xmon')
    dialog = Dialog_RCavity(design)

    def updateMainDesign(updated_design):
        print("主窗口设计已更新")

    dialog.designUpdated.connect(updateMainDesign)
    design.gds.show_svg()
    if dialog.exec() == QDialog.Accepted:
        pass
    sys.exit(app.exec())