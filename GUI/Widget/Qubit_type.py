import sys
from PySide6 import QtCore
from PySide6.QtWidgets import QApplication, QDialog, QHBoxLayout, QPushButton, QVBoxLayout
from api.design import Design

class SelectionDialog(QDialog):
    designUpdated = QtCore.Signal(object)

    def __init__(self, design):
        super().__init__()
        self.design = design
        self.setWindowTitle("选择量子比特类型")
        self.setGeometry(100, 100, 300, 100)  # Set window size and initial position

        # Create main vertical layout
        main_layout = QVBoxLayout()

        # Create horizontal layout
        button_layout = QHBoxLayout()

        # create button
        self.xmon_button = QPushButton("Xmon")
        self.transmon_button = QPushButton("Transmon")

        # Set button style to box type
        self.xmon_button.setStyleSheet("border: 2px solid black; border-radius: 0px; padding: 10px;")
        self.transmon_button.setStyleSheet("border: 2px solid black; border-radius: 0px; padding: 10px;")

        # Connection button click event
        self.xmon_button.clicked.connect(self.select_xmon)
        self.transmon_button.clicked.connect(self.select_transmon)

        # Add buttons to horizontal layout
        button_layout.addWidget(self.xmon_button)
        button_layout.addWidget(self.transmon_button)

        # Add horizontal layout to the main layout
        main_layout.addLayout(button_layout)

        # Set the main layout
        self.setLayout(main_layout)

        # Set window display position
        self.move(400, 400)  # Set the top left corner position of the window to (200, 200)

    def select_xmon(self):
        print("您选择了 Xmon")
        self.design.generate_qubits(topology=True, qubits_type='Xmon')
        self.designUpdated.emit(self.design)  # Send design update signal
        self.accept()  # close dialog boxes

    def select_transmon(self):
        print("您选择了 Transmon")
        self.design.generate_qubits(topology=True, qubits_type='Transmon')
        self.designUpdated.emit(self.design)
        self.accept()  # close dialog boxes

if __name__ == "__main__":
    app = QApplication(sys.argv)
    design = Design()  # create Design example
    dialog = SelectionDialog(design)  # support design Instance passed to SelectionDialog
    dialog.exec()