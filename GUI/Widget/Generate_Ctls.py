import sys
from PySide6 import QtCore, QtWidgets
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QDialog, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QDialogButtonBox
from PySide6.QtCore import QCoreApplication, QMetaObject, QSettings
from addict import Dict
from api.design import Design

class Ui_Dialog:
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName("Dialog")
        Dialog.resize(650, 400)
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
        self.createLabeledInput("Name:")
        self.createLabeledInput("Type:")
        self.createLabeledInput("Chip:")
        self.createLabeledInput("Path:")
        self.createLabeledInput("Width:")
        self.createLabeledInput("Gap:")
        self.createLabeledInput("Buffer Length:")
        self.createLabeledInput("Corner Radius:")

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
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", "Control_lines"))


class Dialog_ctls(QDialog, Ui_Dialog):
    designUpdated = QtCore.Signal(object)
    def __init__(self,design):
        super(Dialog_ctls, self).__init__()
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
            "name": "ControlLineWidthDiff0",
            "type": "ChargeLine",
            "chip": "chip0",
            "path": "[(-4300, 800), (-3800, 800), (-3800, -2000), (-1700, -2000), (-1700, -700), (-1700, -220)]",
            "width": "[15, 10]",
            "gap": "[5, 4]",
            "buffer_length": "100",
            "corner_radius": "100"
        }
        keys = ["name", "type", "chip", "path", "width", "gap", "buffer_length", "corner_radius"]
        for i, key in enumerate(keys):
            self.lineEdits[i].setText(defaults[key])  # Directly set default values

    def processInputs(self):
        """Save the text of the input box to QSettingsAnd convert to the appropriate type"""
        keys = ["name", "type", "chip", "path", "width", "gap", "buffer_length", "corner_radius"]
        for i, key in enumerate(keys):
            self.settings.setValue(key, self.lineEdits[i].text())

        # Save the input parameters as variables of different types
        name = self.settings.value("name", "", type=str)
        type_name = self.settings.value("type", "", type=str)
        chip = self.settings.value("chip", "", type=str)
        path = eval(self.settings.value("path", "[]", type=str))  # use eval Convert a string to a list
        width = eval(self.settings.value("width", "[]", type=str))
        gap = eval(self.settings.value("gap", "[]", type=str))
        buffer_length = int(self.settings.value("buffer_length", "0", type=str))
        corner_radius = int(self.settings.value("corner_radius", "0", type=str))

        # Print the input value
        print(f"Name: {name}")
        print(f"Type: {type_name}")
        print(f"Chip: {chip}")
        print(f"Path: {path}")
        print(f"Width: {width}")
        print(f"Gap: {gap}")
        print(f"Buffer Length: {buffer_length}")
        print(f"Corner Radius: {corner_radius}")

        options = Dict(
            name=name,  # Control line name
            type=type_name,  # Control line type
            chip=chip,  # The chip layer where it is located
            path=path,
            # Set of coordinate points for the control line path
            width=width,  #
            gap=gap,
            buffer_length=buffer_length,
            corner_radius=corner_radius  # corner radius
        )
        self.design.gds.control_lines.add(options)
        self.designUpdated.emit(self.design)
        # close dialog boxes
        self.accept()  # close dialog boxes


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    dialog = Dialog_ctls(design=Design())

    # If the dialog box accepts，Display input content
    if dialog.exec() == QDialog.Accepted:
        print("Dialog accepted")

    # exit from application program
    sys.exit(app.exec())