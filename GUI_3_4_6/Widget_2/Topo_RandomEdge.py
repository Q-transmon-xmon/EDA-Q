from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QFont
from api.design import Design
import sys


class Dialog_RandomEdge(QtWidgets.QDialog):
    # Define a signal to notify external when the design is updated
    designUpdated = QtCore.pyqtSignal(object)

    def __init__(self, design, parent=None):
        super(Dialog_RandomEdge, self).__init__(parent)
        self.design = design
        self.num = None  # Initialize num variable
        self.setupUi()

    def setupUi(self):
        self.setObjectName("Dialog")

        # Set initial window size and minimum/maximum sizes
        self.resize(480, 300)
        self.setMinimumSize(300, 100)  # Set minimum size
        self.setMaximumSize(600, 300)  # Optional: Set maximum size

        # Set the font for the entire interface
        font = QFont("Microsoft YaHei")
        font.setPointSize(10)  # Set font size
        self.setFont(font)

        # Use a vertical layout
        layout = QtWidgets.QVBoxLayout(self)  # Main layout

        # Title
        title_label = QtWidgets.QLabel("Topology Edge Generation", self)
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        title_label.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        layout.addWidget(title_label)

        # Instruction
        instruction_label = QtWidgets.QLabel("Please enter the number of edges you want to generate randomly:", self)
        instruction_label.setAlignment(QtCore.Qt.AlignCenter)
        instruction_label.setWordWrap(True)  # Enable word wrap for longer text
        layout.addWidget(instruction_label)

        # Input row
        self.widget = QtWidgets.QWidget(self)
        self.widget.setObjectName("widget")

        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout.setContentsMargins(10, 10, 10, 10)  # Add margins for neatness
        self.horizontalLayout.setObjectName("horizontalLayout")

        # Line edit with placeholder text
        self.lineEdit = QtWidgets.QLineEdit(self.widget)
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit.setPlaceholderText("Enter number of edges")  # Placeholder
        self.lineEdit.installEventFilter(self)  # Install event filter for handling Tab key
        self.horizontalLayout.addWidget(self.lineEdit)

        # Add input row to main layout
        layout.addWidget(self.widget)

        # Button box
        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        layout.addWidget(self.buttonBox)  # Add button box to main layout

        # Set layout spacing for better aesthetics
        layout.setSpacing(10)

        self.retranslateUi()

        # Connect button signals to slots
        self.buttonBox.accepted.connect(self.checkInputs)  # Connect to checkInputs
        self.buttonBox.rejected.connect(self.reject)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Dialog", "Random Edge Design"))

    def eventFilter(self, source, event):
        """Handle Tab key event to set default value and switch focus"""
        if event.type() == QtCore.QEvent.KeyPress and event.key() == QtCore.Qt.Key_Tab:
            # Check if the line edit has focus
            if source is self.lineEdit:
                input_text = self.lineEdit.text().strip()
                if input_text == "":
                    self.lineEdit.setText(self.lineEdit.placeholderText())  # Set default value
                return True  # Prevent further processing of the Tab key
        return super().eventFilter(source, event)

    def checkInputs(self):
        """Check the value in the line edit and process the random edge generation"""
        try:
            input_text = self.lineEdit.text().strip()
            if not input_text:  # Check for empty input
                raise ValueError("Input cannot be empty.")  # Raise error if empty

            self.num = int(input_text)  # Convert input to integer
            if self.num <= 0:
                raise ValueError("The number of edges must be greater than zero.")

            self.design.topology.generate_random_edges(self.num)

            # Emit signal to notify the main window of the design update
            self.designUpdated.emit(self.design)

            # Close the dialog
            self.accept()

        except ValueError as e:
            QtWidgets.QMessageBox.warning(self, "Input Error", str(e))  # Show error message


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    # Assume there is a design object
    design = Design()  # Replace this with the actual design object
    dialog = Dialog_RandomEdge(design)

    # Connect signal to a function to handle design updates
    dialog.designUpdated.connect(lambda updated_design: print("Design update received in the main window!"))
    dialog.exec_()  # Show the dialog

    sys.exit(app.exec_())