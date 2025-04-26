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
        Dialog.resize(400, 200)
        # Set the font of the entire interface to Microsoft Yahei
        Dialog.setFont(QFont("Microsoft YaHei", 10.5))
        # Create main vertical layout
        self.mainLayout = QVBoxLayout(Dialog)
        self.mainLayout.setContentsMargins(20, 20, 20, 20)  # Set the margins for the main layout
        self.mainLayout.setSpacing(15)  # Set the spacing between controls within the layout

        # Create a layout for input boxes
        self.inputLayout = QVBoxLayout()
        self.inputLayout.setSpacing(20)  # Set the spacing between controls within the input box layout

        # Create tags and input boxes
        self.createLabeledInput("Coupling line type:")
        self.createLabeledInput("The chip layer where it is located:")

        # Add input box layout to the main layout
        self.mainLayout.addLayout(self.inputLayout)

        # Create button box
        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.mainLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)

        # Connect signal and slot
        QMetaObject.connectSlotsByName(Dialog)

    def createLabeledInput(self, label_text):
        """Create a label and corresponding input box，And add them to the layout"""
        horizontalLayout = QHBoxLayout()
        label = QLabel(label_text)
        line_edit = QLineEdit()

        horizontalLayout.addWidget(label)
        horizontalLayout.addWidget(line_edit)
        self.inputLayout.addLayout(horizontalLayout)

        # Add input box to instance variable，For future visits
        if not hasattr(self, 'lineEdits'):
            self.lineEdits = []
        self.lineEdits.append(line_edit)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", "Coupling_lines"))

class Dialog_cpls(QDialog, Ui_Dialog):
    designUpdated = QtCore.Signal(object)
    def __init__(self,design):
        super(Dialog_cpls, self).__init__()
        self.setupUi(self)
        self.design = design
        # QSettings Used to save and load input data
        self.settings = QSettings("MyCompany", "MyApp")

        # Read default values and display them
        self.loadPreviousInputs()

        # Signal for connecting button
        self.buttonBox.accepted.connect(self.processInputs)
        self.buttonBox.rejected.connect(self.reject)  # Cancel connection button to QDialog of reject method

    def loadPreviousInputs(self):
        """Load default values"""
        defaults = {
            "coupling_line_type": "CouplingLineStraight",
            "chip_layer_name": "chip0"
        }
        keys = ["coupling_line_type", "chip_layer_name"]
        for i, key in enumerate(keys):
            self.lineEdits[i].setText(defaults[key])  # Directly set default values

    def processInputs(self):
        """Save the text of the input box to QSettingsAnd convert to the appropriate type"""
        keys = ["coupling_line_type", "chip_layer_name"]
        for i, key in enumerate(keys):
            self.settings.setValue(key, self.lineEdits[i].text())

        # Save the input parameters as variables of different types
        coupling_line_type = self.settings.value("coupling_line_type", "", type=str)
        chip_layer_name = self.settings.value("chip_layer_name", "", type=str)

        # Print the input value
        print(f"Coupling Line Type: {coupling_line_type}")
        print(f"Chip Layer Name: {chip_layer_name}")

        self.design.generate_coupling_lines(topology=True, qubits=True,cpls_type = coupling_line_type,chip_name=chip_layer_name)
        self.designUpdated.emit(self.design)
        # close dialog boxes
        self.accept()  # close dialog boxes

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    design = Design()
    dialog = Dialog_cpls(design=design)

    # If the dialog box accepts，Display input content
    if dialog.exec() == QDialog.Accepted:
        print("Dialog accepted")

    # exit from application program
    sys.exit(app.exec())