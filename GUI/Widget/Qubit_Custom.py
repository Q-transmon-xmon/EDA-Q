import sys
from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import QDialog, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QWidget, QDialogButtonBox, QComboBox
from PySide6.QtCore import QCoreApplication, QMetaObject, QRect, QSettings
from api.design import Design
import math


class Ui_Dialog_Qubit_Custom:
    def setupUi(self, Dialog_Qubit_Custom):
        if not Dialog_Qubit_Custom.objectName():
            Dialog_Qubit_Custom.setObjectName("Dialog_Qubit_Custom")
        Dialog_Qubit_Custom.resize(400, 350)

        self.buttonBox = QDialogButtonBox(Dialog_Qubit_Custom)
        self.buttonBox.setGeometry(QRect(30, 280, 341, 32))
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)

        self.layoutWidget = QWidget(Dialog_Qubit_Custom)
        self.layoutWidget.setGeometry(QRect(40, 40, 331, 200))
        self.verticalLayout = QVBoxLayout(self.layoutWidget)

        # Create labels and input boxes
        self.createLabeledInput("Number of Qubits:")
        self.createLabeledInput("Distance:")
        self.createLabeledInput("Chip Layer:")

        # Add qubit type selection
        self.addQubitTypeSelection()

        self.retranslateUi(Dialog_Qubit_Custom)

        # Connect signal and slot
        QMetaObject.connectSlotsByName(Dialog_Qubit_Custom)

    def createLabeledInput(self, label_text):
        """Create a label and corresponding input box, and add them to the layout"""
        horizontalLayout = QHBoxLayout()
        label = QLabel(label_text)
        line_edit = QLineEdit()

        horizontalLayout.addWidget(label)
        horizontalLayout.addWidget(line_edit)
        self.verticalLayout.addLayout(horizontalLayout)

        # Add input box to instance variable for future access
        if not hasattr(self, 'lineEdits'):
            self.lineEdits = []
        self.lineEdits.append(line_edit)

    def addQubitTypeSelection(self):
        """Add qubit type selection"""
        horizontalLayout = QHBoxLayout()
        label = QLabel("Qubit Type:")
        self.qubit_type_combo = QComboBox()
        self.qubit_type_combo.addItems(["Xmon", "Transmon"])

        horizontalLayout.addWidget(label)
        horizontalLayout.addWidget(self.qubit_type_combo)
        self.verticalLayout.addLayout(horizontalLayout)

    def retranslateUi(self, Dialog_Qubit_Custom):
        Dialog_Qubit_Custom.setWindowTitle(QCoreApplication.translate("Dialog_Qubit_Custom", "Generate Qubits"))


class Dialog_Qubit_Custom(QDialog, Ui_Dialog_Qubit_Custom):
    designUpdated = QtCore.Signal(object)

    def __init__(self, design):
        super(Dialog_Qubit_Custom, self).__init__()
        self.setupUi(self)

        # Store the passed design parameter
        self.design = design

        # QSettings used to save and load input data
        self.settings = QSettings("MyCompany", "MyApp")

        # Read the last saved input content and display it
        self.loadPreviousInputs()

        # Signal for connecting button
        self.buttonBox.accepted.connect(self.Process_Qubit)
        self.buttonBox.rejected.connect(self.reject)  # Connect cancel button to QDialog's reject method

    def loadPreviousInputs(self):
        """Load the last saved input content"""
        self.lineEdits[0].setText(self.settings.value("quantum_bits", "", type=str))
        self.lineEdits[1].setText(self.settings.value("distance", "", type=str))
        self.lineEdits[2].setText(self.settings.value("thickness", "", type=str))

    def Process_Qubit(self):
        """Save the text of the input box to QSettings"""
        self.settings.setValue("quantum_bits", self.lineEdits[0].text())
        self.settings.setValue("distance", self.lineEdits[1].text())
        self.settings.setValue("thickness", self.lineEdits[2].text())

        quantum_bits = int(self.lineEdits[0].text())
        distance = int(self.lineEdits[1].text())
        thickness = self.lineEdits[2].text()
        qubit_type = self.qubit_type_combo.currentText()

        print(f"Number of Qubits: {quantum_bits}")
        print(f"Distance: {distance}")
        print(f"Chip Layer: {thickness}")
        print(f"Selected Qubit Type: {qubit_type}")

        self.design.generate_topology(qubits_num=quantum_bits, topo_col=int(math.sqrt(quantum_bits)))
        self.design.generate_qubits(chip_name=thickness, dist=distance, qubits_type=qubit_type,
                                    topo_positions=self.design.topology.positions)
        # Send design update signal
        self.designUpdated.emit(self.design)

        # Close dialog box
        self.accept()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    design = Design()  # Create Design instance
    dialog = Dialog_Qubit_Custom(design=design)  # Pass design instance to Dialog_Qubit_Custom

    # Connect the design update signal to the main design
    def updateMainDesign(updated_design):
        print("Main window design has been updated")
    dialog.designUpdated.connect(updateMainDesign)

    # If the dialog box is accepted, display the input content
    if dialog.exec() == QDialog.Accepted:
        dialog.design.gds.show_svg()

    # Exit the application
    sys.exit(app.exec())