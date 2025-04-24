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
        Dialog.resize(400, 150)
        # Set the font of the entire interface to Microsoft Yahei
        Dialog.setFont(QFont("Microsoft YaHei", 10.5))
        # Create main vertical layout
        self.mainLayout = QVBoxLayout(Dialog)
        self.mainLayout.setContentsMargins(20, 20, 20, 20)  # Set the margins for the main layout
        self.mainLayout.setSpacing(15)  # Set the spacing between controls within the layout

        # Create a layout for input boxes
        self.inputLayout = QVBoxLayout()
        self.inputLayout.setSpacing(10)  # Set the spacing between controls within the input box layout

        # Create tags and input boxes
        self.createLabeledInput("芯片层名称:")

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
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", "Crossover_lines"))

class Dialog_crosvs(QDialog, Ui_Dialog):

    designUpdated = QtCore.Signal(object)
    def __init__(self,design):
        super(Dialog_crosvs, self).__init__()
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
            "chip_layer_name": "chip0"
        }
        keys = ["chip_layer_name"]
        for i, key in enumerate(keys):
            self.lineEdits[i].setText(defaults[key])  # Directly set default values

    def processInputs(self):
        """Save the text of the input box to QSettingsAnd convert to the appropriate type"""
        keys = ["chip_layer_name"]
        for i, key in enumerate(keys):
            self.settings.setValue(key, self.lineEdits[i].text())

        # Save the input parameters as variables of different types
        chip_layer_name = self.settings.value("chip_layer_name", "", type=str)

        # Print the input value
        print(f"Chip Layer Name: {chip_layer_name}")
        self.design.generate_cross_overs(coupling_lines=True, transmission_lines=True, chip_name=chip_layer_name)
        self.designUpdated.emit(self.design)
        # close dialog boxes
        self.accept()  # close dialog boxes

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    dialog = Dialog_crosvs(design=Design())

    # If the dialog box accepts，Display input content
    if dialog.exec() == QDialog.Accepted:
        print("Dialog accepted")

    # exit from application program
    sys.exit(app.exec())