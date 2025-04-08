import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QGridLayout, QPushButton, QMessageBox
from api.design import Design


class Ui_Dialog:
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setMinimumSize(480, 300)  # Set a minimum size for the dialog
        Dialog.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)  # Allow resizing

        # Set the entire interface font to Microsoft YaHei
        font = QFont("Microsoft YaHei")
        font.setPointSize(10)  # Set font size
        Dialog.setFont(font)

        # Create a grid layout to arrange widgets
        self.gridLayout = QGridLayout(Dialog)
        self.gridLayout.setSpacing(15)  # Space between widgets
        self.gridLayout.setContentsMargins(20, 20, 20, 20)  # Set margins for the layout

        # Title
        title_label = QLabel("Topology Edge Generation", Dialog)
        title_label.setAlignment(QtCore.Qt.AlignCenter)  # Center aligned
        title_label.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))  # Bold title
        self.gridLayout.addWidget(title_label, 0, 0, 1, 2)  # Span two columns

        # Instruction text with word wrapping
        instruction_label = QLabel("Please enter the names of the nodes for the edges you want to change:")
        instruction_label.setAlignment(QtCore.Qt.AlignCenter)  # Center aligned
        instruction_label.setWordWrap(True)  # Enable word wrap
        self.gridLayout.addWidget(instruction_label, 1, 0, 1, 2)  # Span two columns

        # Input fields
        self.label = QLabel("q0 Name:", Dialog)
        self.gridLayout.addWidget(self.label, 2, 0)  # Positioning label in the grid
        self.lineEdit = QLineEdit(Dialog)
        self.lineEdit.setPlaceholderText("q0")  # Set placeholder for default value
        self.gridLayout.addWidget(self.lineEdit, 2, 1)  # Positioning input in the grid

        self.label_2 = QLabel("q1 Name:", Dialog)
        self.gridLayout.addWidget(self.label_2, 3, 0)  # Positioning label in the grid
        self.lineEdit_2 = QLineEdit(Dialog)
        self.lineEdit_2.setPlaceholderText("q1")  # Set placeholder for default value
        self.gridLayout.addWidget(self.lineEdit_2, 3, 1)  # Positioning input in the grid

        # Create a button layout
        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.pushButton = QPushButton("Add", Dialog)
        self.pushButton.setStyleSheet("background-color: #28a745; color: white; font-weight: bold;")
        self.pushButton.setFixedWidth(80)  # Fixed width for the button
        self.buttonLayout.addWidget(self.pushButton)

        self.pushButton_2 = QPushButton("Delete", Dialog)
        self.pushButton_2.setStyleSheet("background-color: #dc3545; color: white; font-weight: bold;")
        self.pushButton_2.setFixedWidth(80)  # Fixed width for the button
        self.buttonLayout.addWidget(self.pushButton_2)

        self.gridLayout.addLayout(self.buttonLayout, 4, 0, 1, 2)  # Span buttons across two columns

        # Update window title
        self.retranslateUi(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Topology Edge Generation"))  # Set window title


class Dialog_CustomEdge(QDialog, Ui_Dialog):
    # Define a signal to notify external when the design is updated
    designUpdated = QtCore.pyqtSignal(object)

    def __init__(self, design, parent=None):
        super(Dialog_CustomEdge, self).__init__(parent)
        self.setupUi(self)
        self.design = design  # Store the design object

        # Connect buttons to respective methods
        self.pushButton.clicked.connect(self.add_edge)
        self.pushButton_2.clicked.connect(self.delete_edge)

    def add_edge(self):
        q0_name = self.lineEdit.text()
        q1_name = self.lineEdit_2.text()

        # Check if qubit names are valid
        if not self.validate_qubit_names(q0_name, q1_name):
            return

        # Logic to add edge using the design object
        print(f"Adding edge between {q0_name} and {q1_name}")
        self.design.topology.add_edge(q0_name, q1_name)

        # Emit signal after design update
        self.designUpdated.emit(self.design)

    def delete_edge(self):
        q0_name = self.lineEdit.text()
        q1_name = self.lineEdit_2.text()

        # Check if qubit names are valid
        if not self.validate_qubit_names(q0_name, q1_name):
            return

        # Logic to delete edge using the design object
        print(f"Deleting edge between {q0_name} and {q1_name}")
        self.design.topology.remove_edge([q0_name, q1_name])

        # Emit signal after design update
        self.designUpdated.emit(self.design)

    def validate_qubit_names(self, q0_name, q1_name):
        # Ensure qubit names are not empty
        if not q0_name or not q1_name:
            QMessageBox.critical(self, "Error", "Qubit name(s) must not be empty. Please enter valid names.")
            return False

        # Check if qubit names exist in the topology
        valid_qubits = self.design.topology.positions.keys()
        if q0_name not in valid_qubits or q1_name not in valid_qubits:
            QMessageBox.critical(self, "Error", "Invalid qubit name(s). Please enter valid qubit names.")
            return False

        return True


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    design = Design()  # Instance of design object
    dialog = Dialog_CustomEdge(design=design)

    # Connect signal to function that handles design updates
    def updateMainDesign(updated_design):
        print("Main design has been updated")

    dialog.designUpdated.connect(updateMainDesign)
    dialog.exec_()  # Use exec_() in PyQt5

    sys.exit(app.exec_())