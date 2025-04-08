import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QCoreApplication, QMetaObject, QSettings, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QDialog, QDialogButtonBox, QHBoxLayout, QLabel,
                             QLineEdit, QVBoxLayout, QMessageBox, QFrame)
from addict import Dict
from api.design import Design


class Ui_Dialog_Rcavity(object):
    def setupUi(self, Dialog_Rcavity):
        if not Dialog_Rcavity.objectName():
            Dialog_Rcavity.setObjectName("Dialog_Rcavity")
        Dialog_Rcavity.resize(600, 500)
        # Set the font of the entire interface to Microsoft YaHei
        Dialog_Rcavity.setFont(QFont("Microsoft YaHei", int(10.5)))
        self.verticalLayout = QVBoxLayout(Dialog_Rcavity)
        self.verticalLayout.setContentsMargins(10, 10, 10, 10)

        # Create rdls_type input field
        self.rdlsLayout = QHBoxLayout()
        self.rdlsLabel = QLabel("Readout Resonator Type:")
        self.rdlsLineEdit = QLineEdit()
        self.rdlsLineEdit.setText("ReadoutCavity")  # Set default value
        self.rdlsLayout.addWidget(self.rdlsLabel)
        self.rdlsLayout.addWidget(self.rdlsLineEdit)
        self.verticalLayout.addLayout(self.rdlsLayout)

        # Create chip layer name input field
        self.chipLayerLayout = QHBoxLayout()  # New layout
        self.chipLayerLabel = QLabel("Chip Layer Name:")  # New label
        self.chipLayerLineEdit = QLineEdit()  # New input field
        self.chipLayerLineEdit.setText("chip0")  # Set default value
        self.chipLayerLayout.addWidget(self.chipLayerLabel)  # Add label to layout
        self.chipLayerLayout.addWidget(self.chipLayerLineEdit)  # Add input field to layout
        self.verticalLayout.addLayout(self.chipLayerLayout)  # Add layout to main layout

        # Create a gray frame for the dictionary part
        self.dictFrame = QFrame(Dialog_Rcavity)
        self.dictFrame.setFrameShape(QFrame.StyledPanel)
        self.dictFrame.setStyleSheet("QFrame { border: 2px solid gray; border-radius: 5px; }")
        self.dictFrameLayout = QVBoxLayout(self.dictFrame)
        self.dictFrameLayout.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout.addWidget(self.dictFrame)

        # Create button box and add to layout
        self.buttonBox = QDialogButtonBox(Dialog_Rcavity)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.verticalLayout.addWidget(self.buttonBox)

        # Initialize lists to store input fields and labels
        self.lineEdits = []  # List to store QLineEdit references
        self.labels = []  # List to store labels

        self.retranslateUi(Dialog_Rcavity)
        QMetaObject.connectSlotsByName(Dialog_Rcavity)

    def addInputField(self, label_text, default_value=None):
        """Add label and input field to the dictionary frame"""
        horizontalLayout = QHBoxLayout()
        label = QLabel(label_text)
        line_edit = QLineEdit()
        if default_value is not None:
            line_edit.setText(str(default_value))  # Set default value
        horizontalLayout.addWidget(label)
        horizontalLayout.addWidget(line_edit)
        self.dictFrameLayout.addLayout(horizontalLayout)  # Add to dictionary frame layout
        self.lineEdits.append(line_edit)  # Save reference to input field
        self.labels.append(label_text)  # Save reference to label

    def retranslateUi(self, Dialog_Rcavity):
        Dialog_Rcavity.setWindowTitle(QCoreApplication.translate("Dialog_Rcavity", "Generate Readout Resonator"))


class Dialog_RCavity(QtWidgets.QDialog, Ui_Dialog_Rcavity):
    designUpdated = QtCore.pyqtSignal(object)

    def __init__(self, design):
        super().__init__()
        self.setupUi(self)
        self.design = design
        self.settings = QSettings("MyCompany", "MyApp")

        # Define default values for geometric_options
        self.geometric_options = Dict(
            coupling_length=300,  # Coupling line length
            width=10,  # Coupling line width
            gap=5,  # Coupling line etching width
            outline=[],  # Outline
            height=600,  # CPW height
            finger_length=100,  # Finger length
            finger_orientation=90,  # Finger orientation
            start_dir="top",  # CPW initial bend direction
            start_length=30,  # Straight length near qubit
            length=3000,  # Total coupling line length
            space_dist=60,  # Distance between adjacent bends
            radius=30,  # Coupling line corner radius
            cpw_orientation=90  # CPW orientation
        )
        self.input_types = []  # List to store types of each parameter
        self.loadPreviousInput()
        self.buttonBox.accepted.connect(self.process_RCavity)
        self.buttonBox.rejected.connect(self.reject)

    def loadPreviousInput(self):
        """Dynamically load all contents of geometric_options dictionary and display default values"""
        self.lineEdits = []  # Clear input field list
        self.labels = []  # Clear label list
        self.input_types = []  # Clear input type list

        for key, default_value in self.geometric_options.items():
            # Dynamically add labels and input fields
            label_text = f"{key.replace('_', ' ').capitalize()}:"  # Format label text
            self.addInputField(label_text, default_value)

            # Save default value to QSettings, if not saved before, use default value
            value = self.settings.value(key, default_value)
            try:
                # Attempt to convert value to the type of default value
                converted_value = type(default_value)(value)
                self.lineEdits[-1].setText(str(converted_value))  # Set input field's default value
            except (ValueError, TypeError):
                self.lineEdits[-1].setText(str(default_value))  # If conversion fails, use default value

            # Save labels and input types
            self.input_types.append(type(default_value))

    def process_RCavity(self):
        """Process user input and generate geometric_options dictionary"""
        geometric_options = Dict()
        valid_input = True

        # Get rdls_type value
        rdls_type = self.rdlsLineEdit.text()  # Get rdls_type value
        chip_layer_name = self.chipLayerLineEdit.text()  # Get chip layer name value

        for i, label in enumerate(self.labels):
            key = label[:-1].replace(' ', '_').lower()  # Convert label to dictionary key
            value_str = self.lineEdits[i].text()
            expected_type = self.input_types[i]

            try:
                # Convert input value based on type
                if expected_type == list:
                    # If it's a list type, try to parse as Python list
                    converted_value = eval(value_str)
                    if not isinstance(converted_value, list):
                        raise ValueError("Input value is not a valid list")
                else:
                    converted_value = expected_type(value_str)

                geometric_options[key] = converted_value  # Save to dictionary
            except (ValueError, SyntaxError) as e:
                QMessageBox.warning(self, "Invalid Input", f"{label} input is invalid: {e}")
                valid_input = False
                break

        if valid_input:
            # Save to QSettings
            for key, value in geometric_options.items():
                self.settings.setValue(key, value)

            # Call design generation method
            self.design.generate_readout_lines(qubits=True, rdls_type=rdls_type, chip_name=chip_layer_name, geometric_options=geometric_options)

            # Emit design updated signal
            self.designUpdated.emit(self.design)
            self.accept()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    design = Design()
    design.generate_topology(topo_col=4, topo_row=4)
    design.generate_qubits(topology=True, qubits_type='Xmon')
    dialog = Dialog_RCavity(design)

    def updateMainDesign(updated_design):
        print("Main window design has been updated")

    dialog.designUpdated.connect(updateMainDesign)
    design.gds.show_svg()
    if dialog.exec_() == QDialog.Accepted:
        pass
    sys.exit(app.exec_())