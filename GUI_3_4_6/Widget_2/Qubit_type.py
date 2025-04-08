import sys
from PyQt5 import QtCore
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QDialog, QHBoxLayout, QPushButton, QVBoxLayout, QLabel, QSizePolicy, \
    QSpacerItem, QMessageBox

from GUI_3_4_6.gui_modules.design_validator import design_validator
from api.design import Design


class Dialog_Selection(QDialog):
    designUpdated = QtCore.pyqtSignal(object)

    def __init__(self, design):
        super().__init__()

        self.design = design
        self.setWindowTitle("Select Qubit Type")
        self.setGeometry(100, 100, 400, 250)  # Set window size and initial position

        # Set the background color of the dialog
        self.setStyleSheet("background-color: #f0f8ff;")  # Light blue background

        # Set font for the dialog
        font = QFont("Segoe UI", 10)
        self.setFont(font)

        # Create main vertical layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 40, 20, 20)  # Set margins for the main layout

        # Create title label
        title_label = QLabel("Please select the type of qubit you want to generate:")
        title_label.setStyleSheet("font-size: 22px; font-weight: bold; color: black;")  # Set title color to black
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        title_label.setWordWrap(True)  # Enable word wrapping
        main_layout.addWidget(title_label)

        # Add a fixed spacer for aesthetics
        main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))  # Fixed height spacer

        # Create horizontal layout for buttons
        button_layout = QHBoxLayout()

        # Create buttons
        self.xmon_button = QPushButton("Xmon")
        self.transmon_button = QPushButton("Transmon")

        # Set improved button styles with a better font and padding
        button_style = """  
            QPushButton {  
                border: 2px solid #007BFF;   
                border-radius: 12px;   
                padding: 12px;   
                font-size: 16px;   
                background-color: #E7F9FF;   
                color: #007BFF;  
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;  
            }  
            QPushButton:hover {  
                background-color: #007BFF;   
                color: white;  
                transition: background-color 0.3s ease;  /* Smooth transition for hover effect */  
            }  
        """

        # Apply the style to buttons
        self.xmon_button.setStyleSheet(button_style)
        self.transmon_button.setStyleSheet(button_style)

        # Connect button click events
        self.xmon_button.clicked.connect(self.select_xmon)
        self.transmon_button.clicked.connect(self.select_transmon)

        # Add buttons to horizontal layout
        button_layout.addWidget(self.xmon_button)
        button_layout.addSpacerItem(
            QSpacerItem(30, 20, QSizePolicy.Fixed, QSizePolicy.Minimum))  # Fixed space between buttons
        button_layout.addWidget(self.transmon_button)

        # Add button layout to main layout
        main_layout.addLayout(button_layout)

        # Add a spacer to the bottom of the layout for aesthetics
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Set main layout
        self.setLayout(main_layout)

        # Set window display position
        self.move(400, 400)

    def select_xmon(self):
        print("You selected Xmon")
        # 检查 topology 是否存在
        if design_validator.is_component_empty(self.design, 'topology'):
            QMessageBox.warning(self, "Warning", "Topology does not exist or is not initialized.")
            return
        self.design.generate_qubits(topology=True, qubits_type='Xmon')
        self.designUpdated.emit(self.design)
        self.accept()

    def select_transmon(self):
        print("You selected Transmon")
        # 检查 topology 是否存在
        if design_validator.is_component_empty(self.design, 'topology'):
            QMessageBox.warning(self, "Warning", "Topology does not exist or is not initialized.")
            return
        self.design.generate_qubits(topology=True, qubits_type='Transmon')
        self.designUpdated.emit(self.design)
        self.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    design = Design()
    dialog = Dialog_Selection(design)
    dialog.exec_()