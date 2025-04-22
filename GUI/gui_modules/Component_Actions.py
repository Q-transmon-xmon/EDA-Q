import os

from PyQt5 import QtCore  # 直接导入 QtCore 模块
from PyQt5.QtCore import pyqtSignal, QObject, Qt  
from PyQt5.QtWidgets import (QDialog, QFormLayout, QLineEdit, QPushButton, QVBoxLayout, QLabel, QHBoxLayout, QMessageBox ,QFrame , QWidget)  
from PyQt5.QtGui import QFont  ,QPixmap
from addict import Dict  

from .global_state import global_state



class ComponentActions(QObject):  
    operation_completed = pyqtSignal(str)  # 操作完成信号  

    def __init__(self, current_design, parent=None):  
        super().__init__(parent)  
        self.current_design = current_design  # 存储当前设计  


    def show_param_window(self, fields, component_type , image_path):  
        """显示参数输入窗口"""
        # 检查路径是否存在
        print(111)
        if not os.path.exists(image_path):
            raise ValueError(f"Failed to find image path: {image_path}")
        dialog = QDialog()  
        if(component_type == 'ReadoutCavity' or component_type == 'ReadoutCavityFlipchip' or component_type == 'ReadoutCavityPlus'or component_type == 'CouplingCavity'):
            name = component_type.replace('Cavity' , 'Resonator')
            dialog.setWindowTitle(f"{name} Parameters")  
        else :
            dialog.setWindowTitle(f"{component_type} Parameters")  
        dialog.setMinimumSize(400, 300)  # 设置最小窗口大小  
        dialog.setFont(QFont("Arial", 10))  # 设置字体
        dialog_width = dialog.width()  

        layout = QVBoxLayout()  

        h_layout = QHBoxLayout()  

        # 图片
        if component_type == "AirBridge" or component_type == "AirbriageNb" or component_type == "IndiumBump" :
            image_label = QLabel()
            pixmap = QPixmap(image_path)  # 加载图片
            pixmap = pixmap.scaled(150 , 300 , aspectRatioMode=True)  # 设置图片缩放大小（可根据需要调整）
            image_label.setPixmap(pixmap)  # 设置图片
            image_label.setAlignment(Qt.AlignCenter)  # 居中对齐 

        else :
            image_label = QLabel()
            pixmap = QPixmap(image_path)  # 加载图片
            pixmap = pixmap.scaled(320 , 400, aspectRatioMode=True)  # 设置图片缩放大小（可根据需要调整）
            image_label.setPixmap(pixmap)  # 设置图片
            image_label.setAlignment(Qt.AlignCenter)  # 居中对齐 
            


        # 添加图片到水平布局
        h_layout.addWidget(image_label, alignment=Qt.AlignCenter)  # 居中图片

        '''
        # 添加分割线
        separator = QFrame()  
        separator.setFrameShape(QFrame.VLine)  # 设置为垂直线
        separator.setFrameShadow(QFrame.Sunken)  # 设置线的阴影
        separator.setMinimumHeight(400)  # 设置分割线的最小高度，使其与图片和表单一致
        h_layout.addWidget(separator)
        '''

        # 表单  
        form = QFormLayout()  
        self.inputs = {}  # 存储输入框  
        self.defaults = {}  # 存储默认值  
        for field, default in fields:  
            line_edit = QLineEdit()  
            line_edit.setPlaceholderText(str(default))  # 设置默认值为虚化显示  
            line_edit.setMinimumWidth(200)  
            form.addRow(f"{field}:", line_edit)  
            self.inputs[field] = line_edit  
            self.defaults[field] = default  # 保存默认值  

            # 安装事件过滤器  
            line_edit.installEventFilter(self)  

        form.setAlignment(Qt.AlignCenter)
        # 将表单添加到水平布局
        form_widget = QWidget()  # 创建一个 QWidget 来放置表单布局
        form_widget.setLayout(form)  # 设置表单布局
        h_layout.addWidget(form_widget ,alignment=Qt.AlignCenter)  # 将表单添加到水平布局

        layout.addLayout(h_layout , Qt.AlignCenter)  # 将水平布局添加到主布局

        # 按钮  
        btn_save = QPushButton("Save")  
        btn_cancel = QPushButton("Cancel")  
        btn_layout = QHBoxLayout()  
        btn_layout.addWidget(btn_save)  
        btn_layout.addWidget(btn_cancel)  

        layout.addLayout(btn_layout)  
        dialog.setLayout(layout)  

        # 连接信号  
        btn_save.clicked.connect(lambda: self.save_params(dialog, component_type))  
        btn_cancel.clicked.connect(dialog.reject)  

        # 重写事件过滤器  
        #dialog.eventFilter = self.create_event_filter(dialog)  

        dialog.exec_()  

    def eventFilter(self,obj, event):
        """创建事件过滤器"""
        #print(111)
        if event.type() == QtCore.QEvent.KeyPress :
            if event.key() == Qt.Key_Tab or event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                #print("Space key pressed!")
                for field, line_edit in self.inputs.items():
                    if line_edit is obj:  # 当前焦点在 line_edit 上
                        if line_edit.text().strip() == "":  # 如果为空
                            #print(str(self.defaults[field]))
                            line_edit.setText(str(self.defaults[field]))  # 填充默认值

                        # 跳转到下一个输入框
                        next_index = list(self.inputs.keys()).index(field) + 1
                        if next_index < len(self.inputs):
                            next_field = list(self.inputs.keys())[next_index]
                            self.inputs[next_field].setFocus()
                        return True  # 阻止事件继续传播
        return super().eventFilter(obj, event)  # 继续传播其他事件

       

    def save_params(self, dialog, component_type):  
        """保存参数并生成组件"""  
        #print('options')
        options = Dict()  
        for field, line_edit in self.inputs.items():  
            key = field.lower().replace(" ", "_")  
            value = line_edit.text().strip() or line_edit.placeholderText()  # 如果为空则使用默认值  
            try:  
                options[key] = eval(value)  # 尝试解析输入值  
            except:  
                options[key] = value  

        options["type"] = component_type  
        options["chip"] = "chip0"  # 默认芯片名称  
        options["outline"] = []  # 默认轮廓 

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
                print(f"{component_type} add successfully")  # 已有的输出信息

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

        


    # ==================== 组件方法 ====================  

  