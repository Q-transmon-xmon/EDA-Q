import os
import sys
import pandas as pd
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QTableWidget,
    QTableWidgetItem, QLabel, QComboBox, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class DataFrameDisplay(QMainWindow):
    def __init__(self, file_path):
        super().__init__()
        self.setWindowTitle("Matrix Display")
        self.resize(1200, 800)

        # 设置全局字体
        font = QFont("Microsoft YaHei", 10)
        QApplication.instance().setFont(font)

        # 创建中心部件和主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)  # 设置边距
        main_layout.setSpacing(20)  # 设置组件间距

        # 下拉菜单
        self.matrix_selector = QComboBox()
        self.matrix_selector.setStyleSheet("""  
            QComboBox {  
                padding: 5px;  
                font-size: 14px;  
                min-width: 200px;  
                max-width: 400px;  
            }  
        """)
        self.matrix_selector.currentIndexChanged.connect(self.display_selected_matrix)
        selector_container = QWidget()
        selector_layout = QHBoxLayout(selector_container)
        selector_layout.addWidget(self.matrix_selector, alignment=Qt.AlignCenter)
        main_layout.addWidget(selector_container)

        # 元数据标签
        self.metadata_label = QLabel()
        self.metadata_label.setStyleSheet("""  
            QLabel {  
                background-color: #f5f5f5;  
                padding: 20px;  
                border: 1px solid #ccc;  
                font-size: 12px;  
                line-height: 2;  
                min-height: 100px;  
            }   
        """)
        self.metadata_label.setAlignment(Qt.AlignCenter)
        self.metadata_label.setWordWrap(True)
        self.metadata_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        main_layout.addWidget(self.metadata_label, 1)  # 1表示伸展因子

        # 表格控件
        self.table_widget = QTableWidget()
        self.table_widget.setStyleSheet("""  
            QTableWidget {  
                border: 1px solid #ccc;  
                font-size: 12px;  
                min-width: 600px;  
                min-height: 400px;  
            }  
            QHeaderView::section {  
                background-color: #f0f0f0;  
                padding: 5px;  
                border: 1px solid #ccc;  
            }  
        """)
        self.table_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_layout.addWidget(self.table_widget, 4)  # 4表示伸展因子，使表格占据更多空间

        # 加载文件
        self.matrices = {}
        self.load_file(file_path)

    def load_file(self, file_path):
        """加载文件并显示内容"""
        if os.path.exists(file_path):
            try:
                metadata, matrices = self.parse_file(file_path)
                self.display_metadata(metadata)
                self.matrices = matrices
                self.matrix_selector.clear()
                self.matrix_selector.addItems(matrices.keys())
                if matrices:
                    self.display_selected_matrix()
            except Exception as e:
                print(f"文件读取失败: {e}")
        else:
            print(f"文件 {file_path} 不存在")

    def parse_file(self, file_path):
        with open(file_path, 'r') as file:
            lines = file.readlines()

        metadata_lines = []
        matrices = {}
        current_matrix_name = None
        matrix_start_index = None
        column_names = []

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            if line.endswith("Matrix"):
                if current_matrix_name and matrix_start_index is not None:
                    data = self.extract_matrix_data(lines, matrix_start_index, i, column_names)
                    matrices[current_matrix_name] = data

                current_matrix_name = line
                matrix_start_index = i + 2
                column_names = lines[i + 1].strip().split("\t")
            elif current_matrix_name is None:
                metadata_lines.append(line)

        if current_matrix_name and matrix_start_index is not None:
            data = self.extract_matrix_data(lines, matrix_start_index, len(lines), column_names)
            matrices[current_matrix_name] = data

        return "\n".join(metadata_lines), matrices

    def extract_matrix_data(self, lines, start_index, end_index, column_names):
        data = []
        for line in lines[start_index:end_index]:
            if line.strip():
                data.append(line.strip().split("\t"))

        df = pd.DataFrame(data)
        df.columns = ["Index"] + column_names
        df.set_index("Index", inplace=True)
        return df

    def display_metadata(self, metadata):
        self.metadata_label.setText(metadata)

    def display_selected_matrix(self):
        selected_matrix = self.matrix_selector.currentText()
        if selected_matrix in self.matrices:
            self.display_dataframe(self.matrices[selected_matrix])

    def display_dataframe(self, dataframe):
        self.table_widget.clear()
        self.table_widget.setRowCount(dataframe.shape[0])
        self.table_widget.setColumnCount(dataframe.shape[1])

        # 设置表头
        self.table_widget.setHorizontalHeaderLabels(dataframe.columns.tolist())
        self.table_widget.setVerticalHeaderLabels(dataframe.index.tolist())

        # 填充数据
        for i in range(dataframe.shape[0]):
            for j in range(dataframe.shape[1]):
                value = round(float(dataframe.iat[i, j]), 3)
                item = QTableWidgetItem(f"{value:.3f}")
                item.setTextAlignment(Qt.AlignCenter)
                self.table_widget.setItem(i, j, item)

        # 调整表格大小
        self.table_widget.resizeColumnsToContents()
        self.table_widget.resizeRowsToContents()

        # 确保表格填充可用空间
        header_width = self.table_widget.verticalHeader().width()
        header_height = self.table_widget.horizontalHeader().height()
        table_width = self.table_widget.contentsRect().width()
        table_height = self.table_widget.contentsRect().height()

        # 计算并设置列宽
        available_width = table_width - header_width
        column_count = self.table_widget.columnCount()
        if column_count > 0:
            column_width = max(100, available_width // column_count)
            for col in range(column_count):
                self.table_widget.setColumnWidth(col, column_width)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    fixed_file_path = "C:/sim_proj/transmon_sim/capacitance_matrix.txt"
    window = DataFrameDisplay(fixed_file_path)
    window.show()
    sys.exit(app.exec())