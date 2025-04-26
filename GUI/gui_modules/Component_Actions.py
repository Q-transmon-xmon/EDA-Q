import os

from PyQt5 import QtCore  # Directly import QtCore module
from PyQt5.QtCore import pyqtSignal, QObject, Qt  
from PyQt5.QtWidgets import (QDialog, QFormLayout, QLineEdit, QPushButton, QVBoxLayout, QLabel, QHBoxLayout, QMessageBox ,QFrame , QWidget)  
from PyQt5.QtGui import QFont  ,QPixmap
from addict import Dict  

from .global_state import global_state



class ComponentActions(QObject):  
    operation_completed = pyqtSignal(str)  # Operation completion signal  

    def __init__(self, current_design, parent=None):  
        super().__init__(parent)  
        self.current_design = current_design  # Store the current design  


    def show_param_window(self, fields, component_type , image_path):  
        """Display parameter input window"""
        # Check if the path exists
        print(111)
        if not os.path.exists(image_path):
            raise ValueError(f"Failed to find image path: {image_path}")
        dialog = QDialog()  
        if(component_type == 'ReadoutCavity' or component_type == 'ReadoutCavityFlipchip' or component_type == 'ReadoutCavityPlus'or component_type == 'CouplingCavity'):
            name = component_type.replace('Cavity' , 'Resonator')
            dialog.setWindowTitle(f"{name} Parameters")  
        else :
            dialog.setWindowTitle(f"{component_type} Parameters")  
        dialog.setMinimumSize(400, 300)  # Set minimum window size  
        dialog.setFont(QFont("Arial", 10))  # set font
        dialog_width = dialog.width()  

        layout = QVBoxLayout()  

        h_layout = QHBoxLayout()  

        # picture
        if component_type == "AirBridge" or component_type == "AirbriageNb" or component_type == "IndiumBump" :
            image_label = QLabel()
            pixmap = QPixmap(image_path)  # load picture
            pixmap = pixmap.scaled(150 , 300 , aspectRatioMode=True)  # Set image zoom size（Can be adjusted as needed）
            image_label.setPixmap(pixmap)  # Set Picture
            image_label.setAlignment(Qt.AlignCenter)  # center aligned 

        else :
            image_label = QLabel()
            pixmap = QPixmap(image_path)  # load picture
            pixmap = pixmap.scaled(320 , 400, aspectRatioMode=True)  # Set image zoom size（Can be adjusted as needed）
            image_label.setPixmap(pixmap)  # Set Picture
            image_label.setAlignment(Qt.AlignCenter)  # center aligned 
            


        # Add images to horizontal layout
        h_layout.addWidget(image_label, alignment=Qt.AlignCenter)  # Center picture 

        '''
        # Add dividing line
        separator = QFrame()  
        separator.setFrameShape(QFrame.VLine)  # Set as vertical line
        separator.setFrameShadow(QFrame.Sunken)  # Set the shadow of the line
        separator.setMinimumHeight(400)  # Set the minimum height of the dividing line,Make it consistent with the images and forms
        h_layout.addWidget(separator)
        '''

        # FORM  
        form = QFormLayout()  
        self.inputs = {}  # Storage input box  
        self.defaults = {}  # Store default values  
        for field, default in fields:  
            line_edit = QLineEdit()  
            line_edit.setPlaceholderText(str(default))  # Set default value to virtual display  
            line_edit.setMinimumWidth(200)  
            form.addRow(f"{field}:", line_edit)  
            self.inputs[field] = line_edit  
            self.defaults[field] = default  # Save default values  

            # Install event filter  
            line_edit.installEventFilter(self)  

        form.setAlignment(Qt.AlignCenter)
        # Add the form to the horizontal layout
        form_widget = QWidget()  # Create a QWidget To place the form layout
        form_widget.setLayout(form)  # Set form layout
        h_layout.addWidget(form_widget ,alignment=Qt.AlignCenter)  # Add the form to the horizontal layout

        layout.addLayout(h_layout , Qt.AlignCenter)  # Add horizontal layout to the main layout

        # button  
        btn_save = QPushButton("Save")  
        btn_cancel = QPushButton("Cancel")  
        btn_layout = QHBoxLayout()  
        btn_layout.addWidget(btn_save)  
        btn_layout.addWidget(btn_cancel)  

        layout.addLayout(btn_layout)  
        dialog.setLayout(layout)  

        # joining signal  
        btn_save.clicked.connect(lambda: self.save_params(dialog, component_type))  
        btn_cancel.clicked.connect(dialog.reject)  

        # Rewrite event filter  
        #dialog.eventFilter = self.create_event_filter(dialog)  

        dialog.exec_()  

    def eventFilter(self,obj, event):
        """Create event filter"""
        #print(111)
        if event.type() == QtCore.QEvent.KeyPress :
            if event.key() == Qt.Key_Tab or event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                #print("Space key pressed!")
                for field, line_edit in self.inputs.items():
                    if line_edit is obj:  # The current focus is on line_edit upper
                        if line_edit.text().strip() == "":  # If it is empty
                            #print(str(self.defaults[field]))
                            line_edit.setText(str(self.defaults[field]))  # Fill in default values

                        # Jump to the next input box
                        next_index = list(self.inputs.keys()).index(field) + 1
                        if next_index < len(self.inputs):
                            next_field = list(self.inputs.keys())[next_index]
                            self.inputs[next_field].setFocus()
                        return True  # Prevent the event from continuing to spread
        return super().eventFilter(obj, event)  # Continue to spread other events

       

    def save_params(self, dialog, component_type):  
        """Save parameters and generate components"""  
        #print('options')
        options = Dict()  
        for field, line_edit in self.inputs.items():  
            key = field.lower().replace(" ", "_")  
            value = line_edit.text().strip() or line_edit.placeholderText()  # If empty, use default value  
            try:  
                options[key] = eval(value)  # Attempt to parse input values  
            except:  
                options[key] = value  

        options["type"] = component_type  
        options["chip"] = "chip0"  # Default chip name  
        options["outline"] = []  # Default contour 

        if(component_type == 'CouplerBase' or component_type == 'CouplingCavity' or component_type == 'CouplingLineStraight'):
            options['chip'] = 'main'

        #print(options)

        current_name = global_state.get_current_design_name()
        #print(dir(self))
        print('current_name:' , current_name)
        self.current_design = global_state.get_design(current_name)
        #print(dir(self.current_design.gds))
        #help(self.current_design.gds)


        try:
            if component_type == "AirBridge":
                self.current_design.gds.others.add(options)
                print(f"{component_type} add successfully")
                
            elif component_type == "AirbriageNb":
                self.current_design.gds.others.add(options)
                print(f"{component_type} add successfully")
                
            elif component_type == "ChargeLine":
                self.current_design.gds.control_lines.add(options)
                print(f"{component_type} add successfully")
                
            elif component_type == "ControlLineCircle":
                self.current_design.gds.control_lines.add(options)
                print(f"{component_type} add successfully")
                
            elif component_type == "ControlLineWidthDiff":
                self.current_design.gds.control_lines.add(options)
                print(f"{component_type} add successfully")
                
            elif component_type == "CouplerBase":
                #from library.coupling_lines.coupler_base import CouplerBase  
                #CouplerBase(options)
                self.current_design.gds.coupling_lines.add(options)
                print(f"{component_type} add successfully")
                
            elif component_type == "CouplingCavity":
                #from library.coupling_lines.coupling_cavity import CouplingCavity  
                #CouplingCavity(options)
                self.current_design.gds.coupling_lines.add(options)
                print(f"{component_type} add successfully")
                
            elif component_type == "CouplingLineStraight":
                #from library.coupling_lines.coupling_line_straight import CouplingLineStraight  
                #CouplingLineStraight(options)
                self.current_design.gds.coupling_lines.add(options)
                print(f"{component_type} add successfully")
                
            elif component_type == "IndiumBump":
                self.current_design.gds.others.add(options)
                print(f"{component_type} add successfully")
                
            elif component_type == "LaunchPad":
                self.current_design.gds.pins.add(options)
                print(f"{component_type} add successfully")
                
            elif component_type == "Transmon":
                self.current_design.gds.qubits.add(options)
                print(f"{component_type} add successfully")  # Existing output information

            elif component_type == "Xmon":
                self.current_design.gds.qubits.add(options)
                print(f"{component_type} add successfully")
                
            elif component_type == "ReadoutArrow":
                self.current_design.gds.readout_lines.add(options)
                print(f"{component_type} add successfully")
                
            elif component_type == "ReadoutArrowPlus":
                self.current_design.gds.readout_lines.add(options)
                print(f"{component_type} add successfully")
                
            elif component_type == "ReadoutCavity":
                self.current_design.gds.readout_lines.add(options)
                print(f"{component_type} add successfully")
                
            elif component_type == "ReadoutCavityFlipchip":
                self.current_design.gds.readout_lines.add(options)
                print(f"{component_type} add successfully")
                
            elif component_type == "ReadoutCavityPlus":
                self.current_design.gds.readout_lines.add(options)
                print(f"{component_type} add successfully")
                
            elif component_type == "TransmissionPath":
                self.current_design.gds.transmission_lines.add(options)
                print(f"{component_type} add successfully")

            global_state.update_design(design_name=current_name,updated_design=self.current_design)
            #self.operation_completed.emit(f"{component_type} add successfully")
            dialog.accept()
        except Exception as e:
            QMessageBox.critical(dialog, "Error", f"operation Exception: {str(e)}")

        


    # ==================== component method ====================  

  