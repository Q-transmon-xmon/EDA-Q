import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QDialog, QLabel, QLineEdit,
    QHBoxLayout, QVBoxLayout, QMessageBox, QPushButton, QComboBox
)
from PyQt5.QtCore import Qt, QSettings
from addict import Dict
from api.design import Design


class Dialog_RAlgorithm(QDialog):
    # Define a signal for design updates
    designUpdated = QtCore.pyqtSignal(object)

    def __init__(self, design, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Routing Algorithm")
        self.setFont(QFont("Microsoft YaHei", int(10.5)))  # Set font
        self.resize(500, 300)  # Adjust dialog size for better usability
        self.design = design
        self.settings = QSettings("MyCompany", "MyApp")  # Initialize QSettings

        # Main layout with margins
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(30, 30, 30, 30)  # Set larger margins for a spacious look
        self.mainLayout.setSpacing(20)  # Increase the spacing between elements

        # Title label
        titleLabel = QLabel("Select Routing Algorithm")
        titleLabel.setFont(QFont("Arial", 16, QFont.Bold))  # Set title font and size
        titleLabel.setAlignment(Qt.AlignCenter)  # Center align title
        self.mainLayout.addWidget(titleLabel)

        # Instructions label
        instructionsLabel = QLabel("Please select the algorithm and chip layer:")
        instructionsLabel.setAlignment(Qt.AlignCenter)  # Center align instructions
        self.mainLayout.addWidget(instructionsLabel)

        # Chip Layer Input
        self.createChipLayerInput()  # Create the chip layer input field

        # Adding extra vertical space between input fields and their labels for better readability
        self.mainLayout.addSpacing(10)

        # Algorithm Selection Dropdown
        self.createAlgorithmSelection()  # Create the algorithm selection dropdown

        # Adding extra vertical space before buttons
        self.mainLayout.addSpacing(20)

        # Create button layout
        self.createButtonLayout()  # Set up the buttons

    def createChipLayerInput(self):
        """Create the input field for chip layer"""
        self.chipLayout = QHBoxLayout()
        self.chipLayout.setSpacing(10)  # Spacing between label and input

        # Create label for Chip Layer
        self.label_chip = QLabel("Chip name:")
        self.label_chip.setFixedWidth(120)  # Align label width for better alignment
        self.chipLayout.addWidget(self.label_chip)

        # Create line edit for user input
        self.lineEdit = QLineEdit()
        self.lineEdit.setPlaceholderText("chip0")  # Placeholder text
        self.chipLayout.addWidget(self.lineEdit)

        self.mainLayout.addLayout(self.chipLayout)  # Add to main layout

    def createAlgorithmSelection(self):
        """Create dropdown for algorithm selection"""
        self.algorithmLayout = QHBoxLayout()
        self.algorithmLayout.setSpacing(10)  # Spacing between label and dropdown

        # Create label for Algorithm Selection
        self.label_algorithm = QLabel("Algorithm:")
        self.label_algorithm.setFixedWidth(120)  # Align label width for better alignment
        self.algorithmLayout.addWidget(self.label_algorithm)

        # Create a combo box for algorithm selection
        self.comboBox = QComboBox()
        self.comboBox.addItems([
            "Control_off_chip_routing",
            "Flipchip_routing_IBM",
            "Flipchip_routing"
        ])
        self.algorithmLayout.addWidget(self.comboBox)  # Add dropdown to layout

        self.mainLayout.addLayout(self.algorithmLayout)  # Add to main layout

    def createButtonLayout(self):
        """Create and set up the button layout"""
        buttonLayout = QHBoxLayout()
        buttonLayout.setSpacing(30)  # Spacing between buttons

        # Create buttons with custom spacing
        okButton = QPushButton("OK")
        cancelButton = QPushButton("Cancel")

        # Set button sizes
        okButton.setFixedSize(100, 40)  # Larger button size for better usability
        cancelButton.setFixedSize(100, 40)

        # Add buttons to layout
        buttonLayout.addStretch()  # Right-align buttons
        buttonLayout.addWidget(okButton)
        buttonLayout.addWidget(cancelButton)

        # Add button layout to the main layout
        self.mainLayout.addLayout(buttonLayout)

        # Connect button events
        okButton.clicked.connect(self.submitValues)  # Connect OK button
        cancelButton.clicked.connect(self.reject)  # Connect Cancel button

    def submitValues(self):
        """Process user input and return result"""
        chip_layer = self.lineEdit.text().strip()  # Get chip layer
        selected_algorithm = self.comboBox.currentText()  # Get selected algorithm

        if not chip_layer:  # Validate input
            QMessageBox.warning(self, "Input Error", "Please enter a chip layer.")  # Show error if empty
            return

        # Print the collected values
        print(f"Input Chip Layer: {chip_layer}")
        print("Selected Algorithm:", selected_algorithm)

        # Call the design routing method with gathered information
        self.design.routing(method=selected_algorithm, chip_name=chip_layer)
        self.designUpdated.emit(self.design)  # Emit design update signal
        self.accept()  # Close dialog

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    design = Design()  # Assuming Design is defined in your api
    dialog = Dialog_RAlgorithm(design=design)

    # Connect the design update signal
    def updateMainDesign(updated_design):
        design = updated_design
        print("Main window design has been updated.")

    dialog.designUpdated.connect(updateMainDesign)

    # Execute dialog and capture user action
    if dialog.exec() == QDialog.Accepted:
        # Automatically process parameters and exit after clicking OK
        pass

    sys.exit(app.exec_())