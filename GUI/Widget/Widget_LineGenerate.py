import sys
import os

# Retrieve the directory where the current script is located
current_path = os.path.dirname(os.path.abspath(__file__))
GUI_PATH = os.path.dirname(current_path)
PROJ_PATH = os.path.dirname(GUI_PATH)

# Add path
sys.path.append(GUI_PATH)
sys.path.append(PROJ_PATH)

from PySide6 import QtWidgets, QtCore
from PySide6.QtGui import QFont
from api.design import Design
from GUI.Widget.Generate_Ctls import Dialog_ctls
from GUI.Widget.Generate_Cpls import Dialog_cpls
from GUI.Widget.Generate_Crosvs import Dialog_crosvs
from GUI.Widget.Generate_Tmls import Dialog_tmls
class Dialog_Line(QtWidgets.QDialog):
    # Define a signal for design updates
    designUpdated = QtCore.Signal(object)

    def __init__(self, design):
        super().__init__()
        self.setWindowTitle("Line Options")
        self.design = design
        # Set window size and position
        self.setGeometry(500, 300, 380, 320)  # Adjust the height to fit the new button
        # Set the font of the entire interface to Microsoft Yahei
        self.setFont(QFont("Microsoft YaHei", 11))
        # Create main grid layout
        layout = QtWidgets.QGridLayout()

        # create button
        self.control_lines_button = QtWidgets.QPushButton("Control_lines")
        self.coupling_lines_button = QtWidgets.QPushButton("Coupling_lines")
        self.cross_overs_button = QtWidgets.QPushButton("Cross_Overs")
        self.transmission_lines_button = QtWidgets.QPushButton("Transmission_lines")  # Add button

        # Set the button color to light gray
        self.control_lines_button.setStyleSheet("background-color: lightgray;")
        self.coupling_lines_button.setStyleSheet("background-color: lightgray;")
        self.cross_overs_button.setStyleSheet("background-color: lightgray;")
        self.transmission_lines_button.setStyleSheet("background-color: lightgray;")  # Set new button color

        # Set button size
        self.control_lines_button.setFixedSize(200, 40)
        self.coupling_lines_button.setFixedSize(200, 40)
        self.cross_overs_button.setFixedSize(200, 40)
        self.transmission_lines_button.setFixedSize(200, 40)  # Set new button size


        # Add the button to the layout and center it
        layout.addWidget(self.control_lines_button, 0, 0, alignment=QtCore.Qt.AlignCenter)
        layout.addWidget(self.coupling_lines_button, 1, 0, alignment=QtCore.Qt.AlignCenter)
        layout.addWidget(self.cross_overs_button, 2, 0, alignment=QtCore.Qt.AlignCenter)
        layout.addWidget(self.transmission_lines_button, 3, 0, alignment=QtCore.Qt.AlignCenter)  # Add a new button to the layout

        # Set the horizontal and vertical spacing of the layout
        layout.setVerticalSpacing(15)

        # Set the main layout
        self.setLayout(layout)

        # Connect button click event to processing function
        self.control_lines_button.clicked.connect(self.handle_control_lines)
        self.coupling_lines_button.clicked.connect(self.handle_coupling_lines)
        self.cross_overs_button.clicked.connect(self.handle_cross_overs)
        self.transmission_lines_button.clicked.connect(self.handle_transmission_lines)  # Connect the new button to the processing function

    def handle_control_lines(self):
        print("Handling Control Lines")
        Dialog_control = Dialog_ctls(self.design)
        Dialog_control.designUpdated.connect(self.updateDesign)
        Dialog_control.exec()
        self.designUpdated.emit(self.design)  # Send design update signal


    def handle_coupling_lines(self):
        print("Handling Coupling Lines")
        Dialog_coupling = Dialog_cpls(self.design)
        Dialog_coupling.designUpdated.connect(self.updateDesign)
        Dialog_coupling.exec()
        self.designUpdated.emit(self.design)


    def handle_cross_overs(self):
        print("Handling Cross Overs")
        Dialog_cross = Dialog_crosvs(self.design)
        Dialog_cross.designUpdated.connect(self.updateDesign)
        Dialog_cross.exec()
        self.designUpdated.emit(self.design)


    def handle_transmission_lines(self):  # Add processing function
        print("Handling Transmission Lines")
        Dialog_transmission = Dialog_tmls(self.design)
        Dialog_transmission.designUpdated.connect(self.updateDesign)
        Dialog_transmission.exec()
        self.designUpdated.emit(self.design)  # Send design update signal


    def updateDesign(self, updated_design):
        self.design = updated_design
        print("LineGenerate中的设计已更新")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    design = Design()
    # Create and display a dialog box
    dialog = Dialog_Line(design=design)
    # Connect the design update signal to the processing function
    dialog.designUpdated.connect(lambda updated_design: print("Design updated:", updated_design))
    dialog.show()

    sys.exit(app.exec())