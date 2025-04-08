import sys
from addict import Dict  
from PyQt5 import QtCore, QtWidgets  
from PyQt5.QtCore import QCoreApplication, QSettings  
from PyQt5.QtGui import QFont  
from PyQt5.QtWidgets import (QDialog, QDialogButtonBox, QHBoxLayout,  
                             QLabel, QLineEdit, QRadioButton,  
                             QVBoxLayout, QWidget)  

from api.design import Design  


class Ui_Dialog_ChipLayer(QWidget):  # Change from QDialog to QWidget  
    def setupUi(self, Dialog_ChipLayer):  
        if not Dialog_ChipLayer.objectName():  
            Dialog_ChipLayer.setObjectName("Dialog_ChipLayer")  
        Dialog_ChipLayer.resize(450, 400)  # Adjust the height to fit the new labels  
        Dialog_ChipLayer.setFont(QFont("Microsoft YaHei", 10))  # Set the main font  

        # Main Layout  
        self.mainLayout = QVBoxLayout(Dialog_ChipLayer)  

        # Title label  
        titleLabel = QLabel("Chip Layer Configuration")  
        titleLabel.setFont(QFont("Arial", 14, QFont.Bold))  
        titleLabel.setAlignment(QtCore.Qt.AlignCenter)  
        self.mainLayout.addWidget(titleLabel)  

        # Instructions label  
        instructionsLabel = QLabel("Please enter the details below. Use 'Tab' to set defaults:")  
        instructionsLabel.setWordWrap(True)  
        instructionsLabel.setAlignment(QtCore.Qt.AlignCenter)  
        self.mainLayout.addWidget(instructionsLabel)  

        # Create parameter input layout  
        self.layoutWidget = QWidget(Dialog_ChipLayer)  
        self.verticalLayout = QVBoxLayout(self.layoutWidget)  
        self.mainLayout.addWidget(self.layoutWidget)  

        # Create chip layer name input box  
        layout_h = QHBoxLayout()  
        self.chip_name_label = QLabel("Chip Layer Name:")  
        self.chip_name_input = QLineEdit()  
        self.chip_name_input.setPlaceholderText("e.g. chip0")  
        layout_h.addWidget(self.chip_name_label)  
        layout_h.addWidget(self.chip_name_input)  
        self.verticalLayout.addLayout(layout_h)  

        # Create radio buttons  
        layout_h = QHBoxLayout()  
        label = QLabel("Chip Layer Parameters:")  
        self.radioButton_define = QRadioButton("Custom")  
        self.radioButton_adapt = QRadioButton("Adaptive Distance Parameter")  
        layout_h.addWidget(label)  
        layout_h.addWidget(self.radioButton_define)  
        layout_h.addWidget(self.radioButton_adapt)  
        self.verticalLayout.addLayout(layout_h)  

        # Create parameter input boxes for coordinates as tuples  
        layout_h = QHBoxLayout()  
        self.start_pos_label = QLabel("Start Position (x,y):")  
        self.start_pos_input = QLineEdit()  
        self.start_pos_input.setPlaceholderText("(-2000, -2000)")  
        layout_h.addWidget(self.start_pos_label)  
        layout_h.addWidget(self.start_pos_input)  
        self.verticalLayout.addLayout(layout_h)  

        layout_h = QHBoxLayout()  
        self.end_pos_label = QLabel("End Position (x,y):")  
        self.end_pos_input = QLineEdit()  
        self.end_pos_input.setPlaceholderText("(2000, 2000)")  
        layout_h.addWidget(self.end_pos_label)  
        layout_h.addWidget(self.end_pos_input)  
        self.verticalLayout.addLayout(layout_h)  

        layout_h = QHBoxLayout()  
        self.distance_label = QLabel("Distance:")  
        self.distance_input = QLineEdit()  
        self.distance_input.setPlaceholderText("2000")  
        layout_h.addWidget(self.distance_label)  
        layout_h.addWidget(self.distance_input)  
        self.verticalLayout.addLayout(layout_h)  

        # Create buttons layout  
        buttonLayout = QHBoxLayout()  
        self.buttonBox = QDialogButtonBox(Dialog_ChipLayer)  
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)  
        self.buttonBox.button(QDialogButtonBox.Ok).setText("Add")  # Change Ok button to Add  
        buttonLayout.addWidget(self.buttonBox)  
        self.deleteButton = QtWidgets.QPushButton("Delete", Dialog_ChipLayer)  
        buttonLayout.addWidget(self.deleteButton)  
        self.mainLayout.addLayout(buttonLayout)  

        self.retranslateUi(Dialog_ChipLayer)  

        # Connect signals and slots  
        self.buttonBox.accepted.connect(Dialog_ChipLayer.accept)  
        self.buttonBox.rejected.connect(Dialog_ChipLayer.reject)  

        # Connect custom radio button state change signal  
        self.radioButton_define.toggled.connect(self.toggleInputs)  
        self.radioButton_adapt.toggled.connect(self.toggleInputs)  

        # Install event filters for each QLineEdit  
        self.start_pos_input.installEventFilter(self)  
        self.end_pos_input.installEventFilter(self)  
        self.chip_name_input.installEventFilter(self)  
        self.distance_input.installEventFilter(self)  

    def eventFilter(self, source, event):  
        if event.type() == QtCore.QEvent.KeyPress and event.key() == QtCore.Qt.Key_Tab:  
            # Check which input field is focused and fill defaults  
            if source == self.chip_name_input:  
                self.chip_name_input.setText("chip0")  # Default value for chip name  
                self.end_pos_input.setFocus()  # Move focus to End Position  
                return True  
            elif source == self.start_pos_input:  
                self.start_pos_input.setText("(-2000, -2000)")  # Default start position  
                self.end_pos_input.setFocus()  # Move focus to End Position  
                return True  
            elif source == self.end_pos_input:  
                self.end_pos_input.setText("(2000, 2000)")  # Default end position  
                self.distance_input.setFocus()  # Move focus to Distance  
                return True  
            elif source == self.distance_input:  
                self.distance_input.setText("2000")  # Default distance  
                self.buttonBox.button(QDialogButtonBox.Ok).setFocus()  # Move focus to OK button  
                return True  
        return super(Ui_Dialog_ChipLayer, self).eventFilter(source, event)  

    def toggleInputs(self):  
        if self.radioButton_define.isChecked():  
            self.start_pos_label.setVisible(True)  
            self.start_pos_input.setVisible(True)  
            self.end_pos_label.setVisible(True)  
            self.end_pos_input.setVisible(True)  
            self.distance_label.setVisible(False)  
            self.distance_input.setVisible(False)  
        elif self.radioButton_adapt.isChecked():  
            self.start_pos_label.setVisible(False)  
            self.start_pos_input.setVisible(False)  
            self.end_pos_label.setVisible(False)  
            self.end_pos_input.setVisible(False)  
            self.distance_label.setVisible(True)  
            self.distance_input.setVisible(True)  
        else:  
            self.start_pos_label.setVisible(False)  
            self.start_pos_input.setVisible(False)  
            self.end_pos_label.setVisible(False)  
            self.end_pos_input.setVisible(False)  
            self.distance_label.setVisible(False)  
            self.distance_input.setVisible(False)  

    def retranslateUi(self, Dialog_ChipLayer):  
        Dialog_ChipLayer.setWindowTitle(QCoreApplication.translate("Dialog_ChipLayer", "Generate Chip Layer"))  


class Dialog_ChipLayer(QDialog, Ui_Dialog_ChipLayer):  
    designUpdated = QtCore.pyqtSignal(object)  

    def __init__(self, design):  
        super(Dialog_ChipLayer, self).__init__()  
        self.setupUi(self)  
        self.design = design  
        self.settings = QSettings("MyCompany", "MyApp")  
        self.buttonBox.accepted.connect(self.processChipLayer)  
        self.deleteButton.clicked.connect(self.deleteChipLayer)  
        self.toggleInputs()  

    def processCustomSettings(self):  
        start_pos_text = self.start_pos_input.text()  
        end_pos_text = self.end_pos_input.text()  
        layer_name = self.chip_name_input.text() or "chip0"  

        try:  
            start_pos = eval(start_pos_text)  
            end_pos = eval(end_pos_text)  
            if not (isinstance(start_pos, tuple) and len(start_pos) == 2 and  
                    isinstance(end_pos, tuple) and len(end_pos) == 2):  
                raise ValueError  
        except (SyntaxError, ValueError):  
            print("Invalid input for coordinates. Please use proper tuple format like (x, y).")  
            return  

        options = Dict(  
            name=layer_name,  
            type="RecChip",  
            start_pos=start_pos,  
            end_pos=end_pos  
        )  
        
        self.design.gds.chips.add(options)  
        print(f"Chip added: {options}")  

    def processAdaptiveSettings(self):  
        layer_name = self.chip_name_input.text()  
        distance = int(self.distance_input.text())  
        print(f"Adaptive Mode: Layer Name: {layer_name}, Distance: {distance}")  
        self.design.generate_chip(chip_name=layer_name, dist=distance, qubits=True)  

    def processChipLayer(self):  
        self.settings.setValue("layer_name", self.chip_name_input.text())  
        self.settings.setValue("param_start_pos", self.start_pos_input.text())  
        self.settings.setValue("param_end_pos", self.end_pos_input.text())  
        self.settings.setValue("distance", self.distance_input.text())  
        self.settings.setValue("is_custom", self.radioButton_define.isChecked())  

        if self.radioButton_define.isChecked():  
            self.processCustomSettings()  
        elif self.radioButton_adapt.isChecked():  
            self.processAdaptiveSettings()  

        self.designUpdated.emit(self.design)  
        self.accept()  

    def deleteChipLayer(self):  
        layer_name = self.chip_name_input.text()  
        print(f"Deleting {layer_name}")  
        self.design.gds.chips.clear()  
        self.designUpdated.emit(self.design)  
        self.reject()  


if __name__ == "__main__":  
    app = QtWidgets.QApplication(sys.argv)  
    design = Design()  
    dialog = Dialog_ChipLayer(design=design)  
    dialog.designUpdated.connect(lambda updated_design: print("Chip layer design has been updated"))  
    dialog.exec_()  
    sys.exit(app.exec_())  