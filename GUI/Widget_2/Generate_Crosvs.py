import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QDialog, QDialogButtonBox, QLabel, QLineEdit,
                             QHBoxLayout, QVBoxLayout, QMessageBox, QPushButton)
from PyQt5.QtCore import Qt, QSettings
from addict import Dict
from api.design import Design


class Ui_Dialog:
    def setupUi(self, Dialog):
        # Initialize UI setup for the dialog
        if not Dialog.objectName():
            Dialog.setObjectName("Dialog")
        Dialog.resize(450, 250)  # Set the dialog size
        # Set the font of the entire dialog to Microsoft YaHei
        Dialog.setFont(QFont("Microsoft YaHei", 10))  # Use integer for font size
        # Create the main vertical layout
        self.mainLayout = QVBoxLayout(Dialog)
        self.mainLayout.setContentsMargins(20, 20, 20, 20)  # Set margins for the main layout
        self.mainLayout.setSpacing(15)  # Set spacing between controls in the layout

        # Title label
        titleLabel = QLabel("Crossover Line Configuration")  # Set the title label text
        titleLabel.setFont(QFont("Arial", 14, QFont.Bold))  # Set font for the title label
        titleLabel.setAlignment(Qt.AlignCenter)  # Center the title label
        self.mainLayout.addWidget(titleLabel)  # Add title label to the main layout

        # Instructions label with updated text
        instructionsLabel = QLabel("Please enter the chip name for which you want to generate a crossover line:")
        instructionsLabel.setAlignment(Qt.AlignCenter)  # Center align the instructions label
        instructionsLabel.setWordWrap(True)  # Enable word wrap for the label
        self.mainLayout.addWidget(instructionsLabel)  # Add instructions label to the main layout

        # Create a layout for input fields
        self.inputLayout = QVBoxLayout()
        self.inputLayout.setSpacing(10)  # Set spacing between input fields

        # Create label and input field for chip layer name
        self.createLabeledInput("Chip Name:")

        # Add input layout to the main layout
        self.mainLayout.addLayout(self.inputLayout)

        # Increase space between input fields and OK button
        self.mainLayout.addSpacing(20)  # Add spacing between input field and buttons

        # Create a button box for dialog actions (OK and Cancel)
        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)  # Set standard buttons
        self.mainLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)  # Set the dialog title

        # Connect signals and slots
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def createLabeledInput(self, label_text):
        """Create a label and corresponding input field and add them to the layout"""
        horizontalLayout = QHBoxLayout()
        label = QLabel(label_text)  # Create a label with the given text
        line_edit = QLineEdit()  # Create an input field

        # Add label and input field to the horizontal layout
        horizontalLayout.addWidget(label)
        horizontalLayout.addWidget(line_edit)
        self.inputLayout.addLayout(horizontalLayout)  # Add horizontal layout to the input layout

        # Add the input field to the instance variable for later access
        if not hasattr(self, 'lineEdits'):
            self.lineEdits = []
        self.lineEdits.append(line_edit)  # Store the input field for processing later

    def retranslateUi(self, Dialog):
        # Set the window title for the dialog
        Dialog.setWindowTitle(QtCore.QCoreApplication.translate("Dialog", "Crossover Lines"))


class Dialog_crosvs(QDialog, Ui_Dialog):
    # Define a signal for design updates
    designUpdated = QtCore.pyqtSignal(object)

    def __init__(self, design):
        super(Dialog_crosvs, self).__init__()
        self.setupUi(self)
        self.design = design  # Store the design object passed during initialization
        # QSettings for saving and loading input data
        self.settings = QSettings("MyCompany", "MyApp")

        # Load default values and display them in the input fields
        self.loadPreviousInputs()

        # Connect button signals to their respective handler methods
        self.buttonBox.accepted.connect(self.processInputs)  # Connect OK button
        self.buttonBox.rejected.connect(self.reject)  # Connect cancel button to QDialog's reject method

        # Install event filter for Tab key handling
        for line_edit in self.lineEdits:
            line_edit.installEventFilter(self)

    def loadPreviousInputs(self):
        """Load default values into the input fields"""
        defaults = {
            "chip_layer_name": "chip0"
        }
        keys = ["chip_layer_name"]
        for i, key in enumerate(keys):
            self.lineEdits[i].setPlaceholderText(defaults[key])  # Set default values as placeholder text

    def eventFilter(self, source, event):
        """Handle Tab key press to fill default values"""
        if event.type() == QtCore.QEvent.KeyPress and event.key() == Qt.Key_Tab:
            for line_edit in self.lineEdits:
                if line_edit.hasFocus():
                    if line_edit.text().strip() == "":
                        line_edit.setText(line_edit.placeholderText())  # Fill with default value
                    # Move to the next input field
                    next_index = self.lineEdits.index(line_edit) + 1
                    if next_index < len(self.lineEdits):
                        self.lineEdits[next_index].setFocus()
                    return True
        return super().eventFilter(source, event)

    def processInputs(self):
        """Save the text from input fields to QSettings and convert to appropriate types"""
        keys = ["chip_layer_name"]  # Define keys to save
        for i, key in enumerate(keys):
            self.settings.setValue(key, self.lineEdits[i].text())  # Save input values to QSettings

        # Retrieve the value for chip layer name and store it in a variable
        chip_layer_name = self.settings.value("chip_layer_name", "", type=str)

        # Check if coupling_lines and transmission_lines options are available
        missing_components = []
        if not hasattr(self.design.gds, 'coupling_lines') or not self.design.gds.coupling_lines.options:
            missing_components.append("Coupling Lines")
        if not hasattr(self.design.gds, 'transmission_lines') or not self.design.gds.transmission_lines.options:
            missing_components.append("Transmission Lines")

        if missing_components:
            missing_components_str = "\n".join(f"- {component}" for component in missing_components)
            QMessageBox.warning(
                self,
                "Missing Components",
                f"Cannot generate crossover lines. Please configure the following components first:\n{missing_components_str}",
                QMessageBox.Ok
            )
            return

        # Print the chip layer name to the console for debugging
        print(f"Chip Layer Name: {chip_layer_name}")

        # Call the design's method to generate crossover lines
        try:
            print("start")
            self.design.generate_cross_overs(
                coupling_lines=True,
                transmission_lines=True,
                chip_name=chip_layer_name
            )
            print("Crossover Lines Generated")
            self.designUpdated.emit(self.design)  # Emit design update signal to notify interested parties
            self.accept()  # Close the dialog
        except Exception as e:
            QMessageBox.critical(
                self,
                "Generation Failed",
                f"Error occurred during crossover line generation:\n{str(e)}",
                QMessageBox.Ok
            )

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)  # Initialize the application
    dialog = Dialog_crosvs(design=Design())  # Create an instance of the dialog with design object

    # If the dialog is accepted, print a message to the console
    if dialog.exec() == QDialog.Accepted:
        print("Dialog accepted")

    # Exit the application
    sys.exit(app.exec())