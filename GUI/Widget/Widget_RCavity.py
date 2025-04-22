import sys
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import QCoreApplication, QMetaObject, QSettings, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QDialog, QDialogButtonBox, QHBoxLayout, QLabel,
                               QLineEdit, QVBoxLayout, QMessageBox, QFrame)
from addict import Dict
from api.design import Design


class Ui_Dialog_Rcavity(object):
    def setupUi(self, Dialog_Rcavity):
        if not Dialog_Rcavity.objectName():
            Dialog_Rcavity.setObjectName("Dialog_Rcavity")
        Dialog_Rcavity.resize(600, 500)
        # 设置整个界面的字体为微软雅黑
        Dialog_Rcavity.setFont(QFont("Microsoft YaHei", 10.5))
        self.verticalLayout = QVBoxLayout(Dialog_Rcavity)
        self.verticalLayout.setContentsMargins(10, 10, 10, 10)

        # 创建 rdls_type 输入框
        self.rdlsLayout = QHBoxLayout()
        self.rdlsLabel = QLabel("读取腔类型：")
        self.rdlsLineEdit = QLineEdit()
        self.rdlsLineEdit.setText("ReadoutCavity")  # 设置默认值
        self.rdlsLayout.addWidget(self.rdlsLabel)
        self.rdlsLayout.addWidget(self.rdlsLineEdit)
        self.verticalLayout.addLayout(self.rdlsLayout)

        # 创建芯片层名称输入框
        self.chipLayerLayout = QHBoxLayout()  # 新增布局
        self.chipLayerLabel = QLabel("芯片层名称：")  # 新增标签
        self.chipLayerLineEdit = QLineEdit()  # 新增输入框
        self.chipLayerLineEdit.setText("chip0")  # 设置默认值
        self.chipLayerLayout.addWidget(self.chipLayerLabel)  # 添加标签到布局
        self.chipLayerLayout.addWidget(self.chipLayerLineEdit)  # 添加输入框到布局
        self.verticalLayout.addLayout(self.chipLayerLayout)  # 将布局添加到主布局

        # 创建一个灰色框架用于显示字典部分
        self.dictFrame = QFrame(Dialog_Rcavity)
        self.dictFrame.setFrameShape(QFrame.StyledPanel)
        self.dictFrame.setStyleSheet("QFrame { border: 2px solid gray; border-radius: 5px; }")
        self.dictFrameLayout = QVBoxLayout(self.dictFrame)
        self.dictFrameLayout.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout.addWidget(self.dictFrame)

        # 创建按钮框并添加到布局中
        self.buttonBox = QDialogButtonBox(Dialog_Rcavity)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.verticalLayout.addWidget(self.buttonBox)

        # 初始化存储输入框和标签的列表
        self.lineEdits = []  # 存储 QLineEdit 的列表
        self.labels = []  # 存储标签的列表

        self.retranslateUi(Dialog_Rcavity)
        QMetaObject.connectSlotsByName(Dialog_Rcavity)

    def addInputField(self, label_text, default_value=None):
        """添加标签和输入框到字典框中"""
        horizontalLayout = QHBoxLayout()
        label = QLabel(label_text)
        line_edit = QLineEdit()
        if default_value is not None:
            line_edit.setText(str(default_value))  # 设置默认值
        horizontalLayout.addWidget(label)
        horizontalLayout.addWidget(line_edit)
        self.dictFrameLayout.addLayout(horizontalLayout)  # 添加到字典框的布局中
        self.lineEdits.append(line_edit)  # 保存输入框的引用
        self.labels.append(label_text)  # 保存标签的引用

    def retranslateUi(self, Dialog_Rcavity):
        Dialog_Rcavity.setWindowTitle(QCoreApplication.translate("Dialog_Rcavity", "生成读取腔"))


class Dialog_RCavity(QtWidgets.QDialog, Ui_Dialog_Rcavity):
    designUpdated = QtCore.Signal(object)

    def __init__(self, design):
        super().__init__()
        self.setupUi(self)
        self.design = design
        self.settings = QSettings("MyCompany", "MyApp")

        # 定义 geometric_options 的默认值
        self.geometric_options = Dict(
            coupling_length=300,  # 耦合线长度
            width=10,  # 耦合线宽度
            gap=5,  # 耦合线刻蚀宽度
            outline=[],  # 外轮廓
            height=600,  # cpw 高度
            finger_length=100,  # 手指长度
            finger_orientation=90,  # 手指方向
            start_dir="top",  # cpw 初始拐弯方向
            start_length=30,  # 靠近量子比特处直线长度
            length=3000,  # 耦合线总长度
            space_dist=60,  # 相邻拐弯处的距离
            radius=30,  # 耦合线拐角半径
            cpw_orientation=90  # cpw 朝向
        )
        self.input_types = []  # 存储每个参数的类型
        self.loadPreviousInput()
        self.buttonBox.accepted.connect(self.process_RCavity)
        self.buttonBox.rejected.connect(self.reject)

    def loadPreviousInput(self):
        """动态加载 geometric_options 字典中的所有内容，并显示默认值"""
        self.lineEdits = []  # 清空输入框列表
        self.labels = []  # 清空标签列表
        self.input_types = []  # 清空输入类型列表

        for key, default_value in self.geometric_options.items():
            # 动态添加标签和输入框
            label_text = f"{key.replace('_', ' ').capitalize()}："  # 格式化标签文本
            self.addInputField(label_text, default_value)

            # 保存默认值到 QSettings，如果没有保存过，则使用默认值
            value = self.settings.value(key, default_value)
            try:
                # 尝试将值转换为默认值的类型
                converted_value = type(default_value)(value)
                self.lineEdits[-1].setText(str(converted_value))  # 设置输入框的默认值
            except (ValueError, TypeError):
                self.lineEdits[-1].setText(str(default_value))  # 如果转换失败，使用默认值

            # 保存标签和输入类型
            self.input_types.append(type(default_value))

    def process_RCavity(self):
        """处理用户输入并生成 geometric_options 字典"""
        geometric_options = Dict()
        valid_input = True

        # 获取 rdls_type 的值
        rdls_type = self.rdlsLineEdit.text()  # 获取 rdls_type 的值
        chip_layer_name = self.chipLayerLineEdit.text()  # 获取芯片层名称的值

        for i, label in enumerate(self.labels):
            key = label[:-1].replace(' ', '_').lower()  # 将标签转换为字典的键
            value_str = self.lineEdits[i].text()
            expected_type = self.input_types[i]

            try:
                # 根据类型转换输入值
                if expected_type == list:
                    # 如果是列表类型，尝试解析为 Python 列表
                    converted_value = eval(value_str)
                    if not isinstance(converted_value, list):
                        raise ValueError("输入值不是有效的列表")
                else:
                    converted_value = expected_type(value_str)

                geometric_options[key] = converted_value  # 保存到字典中
            except (ValueError, SyntaxError) as e:
                QMessageBox.warning(self, "无效输入", f"{label} 输入无效: {e}")
                valid_input = False
                break

        if valid_input:
            # 保存到 QSettings
            for key, value in geometric_options.items():
                self.settings.setValue(key, value)

            # 调用设计生成方法
            self.design.generate_readout_lines(qubits=True, rdls_type=rdls_type, chip_name=chip_layer_name, geometric_options=geometric_options)

            # 发出设计更新信号
            self.designUpdated.emit(self.design)
            self.accept()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    design = Design()
    design.generate_topology(topo_col=4, topo_row=4)
    design.generate_qubits(topology=True, qubits_type='Xmon')
    dialog = Dialog_RCavity(design)

    def updateMainDesign(updated_design):
        print("主窗口设计已更新")

    dialog.designUpdated.connect(updateMainDesign)
    design.gds.show_svg()
    if dialog.exec() == QDialog.Accepted:
        pass
    sys.exit(app.exec())