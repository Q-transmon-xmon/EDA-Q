import sys
from PySide6 import QtWidgets, QtCore
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QWidget
from PySide6.QtCore import QSettings, Signal
from api.design import Design


class Ui_Dialog_Node:
    def setupUi(self, Dialog_Node):
        if not Dialog_Node.objectName():
            Dialog_Node.setObjectName("Dialog_Node")
        Dialog_Node.resize(400, 250)

        # Set the font of the entire interface to Microsoft YaHei
        Dialog_Node.setFont(QFont("Microsoft YaHei", 10.5))
        # Create a main layout for centering
        self.mainLayout = QVBoxLayout(Dialog_Node)

        # Reserve space to center content vertically
        self.mainLayout.addStretch()

        # Create layout window component
        self.layoutWidget = QWidget(Dialog_Node)
        self.verticalLayout = QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setSpacing(15)  # Set the spacing between input boxes

        # Create labels and input boxes
        self.lineEdits = []
        self.createLabeledInput("Number of Qubits:")
        self.createLabeledInput("Rows:")
        self.createLabeledInput("Columns:")

        # Add intermediate components to the main layout
        self.mainLayout.addWidget(self.layoutWidget)

        # Create button and set alignment method
        self.buttonBox = QDialogButtonBox(Dialog_Node)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)  # Center the button
        self.buttonBox.setMinimumSize(0, 40)  # Set the minimum height of the button
        self.mainLayout.addWidget(self.buttonBox)

        # Reserve space to center content vertically
        self.mainLayout.addStretch()

        self.retranslateUi(Dialog_Node)

        # Connect signal and slot
        self.buttonBox.accepted.connect(lambda: Dialog_Node.Process_Node())
        self.buttonBox.accepted.connect(Dialog_Node.accept)
        self.buttonBox.rejected.connect(Dialog_Node.reject)

    def createLabeledInput(self, label_text):
        """Create a label and corresponding input box, and add them to the layout"""
        layout = QHBoxLayout()
        label = QLabel(label_text)
        line_edit = QLineEdit()

        layout.addWidget(label)
        layout.addWidget(line_edit)
        self.verticalLayout.addLayout(layout)
        self.lineEdits.append(line_edit)  # Save reference to input box

    def retranslateUi(self, Dialog_Node):
        _translate = QtCore.QCoreApplication.translate
        Dialog_Node.setWindowTitle(_translate("Dialog", "Generate Topology Nodes"))  # Set the window title here


class Dialog_Node(QDialog, Ui_Dialog_Node):
    # Define signal
    designUpdated = Signal(object)

    def __init__(self, design):
        super(Dialog_Node, self).__init__()
        self.setupUi(self)

        self.design = design  # Store the design object

        # QSettings used to save and load input data
        self.settings = QSettings("MyCompany", "MyApp")
        # self.loadPreviousInputs()

    # def loadPreviousInputs(self):
    #     """Load the last saved input content"""
    #     self.lineEdits[0].setText(self.settings.value("quantum_bits", "", type=str))
    #     self.lineEdits[1].setText(self.settings.value("rows", "", type=str))
    #     self.lineEdits[2].setText(self.settings.value("columns", "", type=str))

    def Process_Node(self):
        """Save the text of the input box to QSettings"""
        self.settings.setValue("quantum_bits", self.lineEdits[0].text())
        self.settings.setValue("rows", self.lineEdits[1].text())
        self.settings.setValue("columns", self.lineEdits[2].text())

        self.lineEdits[0].setText(self.settings.value("quantum_bits", "", type=str))
        self.lineEdits[1].setText(self.settings.value("rows", "", type=str))
        self.lineEdits[2].setText(self.settings.value("columns", "", type=str))

        totalnum = self.settings.value("quantum_bits", type=int)
        rows = self.settings.value("rows", "", type=int)
        cols = self.settings.value("columns", "", type=int)

        print(f"Number of Qubits: {totalnum}")
        print(f"Rows: {rows}")
        print(f"Columns: {cols}")

        # Design objects using storage
        self.design.generate_topology(topo_col=cols, topo_row=rows)
        # self.design.generate_random_edges()
        # self.design.topology.show_image()
        # Send a signal after the design update
        self.designUpdated.emit(self.design)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    design = Design()  # Instantiate 'Design' before passing to the dialog
    dialog = Dialog_Node(design=design)

    dialog.designUpdated.connect(lambda updated_design: print("Design update has been sent back to the main window!"))

    dialog.exec()  # Run the dialog

    sys.exit(app.exec())