"""
Icon color conversion tool (PyQt5 achieve)
Install dependencies before running：pip install pyqt5
"""

import os
import sys
from PyQt5.QtGui import QColor, QPainter, QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication  # addQApplication


def convert_icon_color(input_path, output_path, target_color):
    """
    Convert icon color
    :param input_path:  Enter file path（PNGformat，White Icon）
    :param output_path: Output file path
    :param target_color: Target Color（supportQtcolor constant/QColor/hexadecimal）
    """
    # Load original icon
    pixmap = QPixmap(input_path)
    if pixmap.isNull():
        raise ValueError(f"无法加载输入文件，路径：{input_path}，请检查路径是否正确")

    # Create a temporary canvas
    colored_pixmap = QPixmap(pixmap.size())
    colored_pixmap.fill(Qt.transparent)

    # color processing
    painter = QPainter(colored_pixmap)
    painter.drawPixmap(0, 0, pixmap)
    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)

    # Analyze color parameters
    if isinstance(target_color, str):
        if target_color.startswith("#"):  # hexadecimal format
            color = QColor(target_color)
        else:  # QtColor constant name
            color = getattr(Qt, target_color, Qt.black)
    elif isinstance(target_color, QColor):
        color = target_color
    else:
        raise ValueError("目标颜色格式不正确，必须是字符串或QColor对象")

    painter.fillRect(colored_pixmap.rect(), color)
    painter.end()

    # save the file
    if not colored_pixmap.save(output_path):
        raise RuntimeError(f"文件保存失败，路径：{output_path}，请检查输出路径是否有写入权限")


def convert_folder_icons(input_folder, output_folder, target_color):
    """
    Batch convert all files in the folderPNGIcon color
    :param input_folder: Enter folder path
    :param output_folder: Output folder path
    :param target_color: Target Color（supportQtcolor constant/QColor/hexadecimal）
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Traverse all files in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith('.png'):
            input_file = os.path.join(input_folder, filename)
            output_file = os.path.join(output_folder, filename)  # Output file with the same name
            try:
                convert_icon_color(input_file, output_file, target_color)
                print(f"成功转换：{input_file} --> {output_file}")
            except Exception as e:
                print(f"转换错误：{input_file}，错误：{str(e)}")


def main():
    app = QApplication(sys.argv)  # createQApplicationexample

    # User input parameters（The following values can be modified）
    input_folder = "D:/work/QEDA_3/icons/toolbar"  # Enter folder path
    output_folder = "D:/work/QEDA_3/icons/toolbar/output/"  # Output folder path
    target_color = "#00BFFF"  # Target Color（We use light blue here）

    # Perform conversion
    convert_folder_icons(input_folder, output_folder, target_color)

    sys.exit(app.exec_())  # Exit the application after completion


if __name__ == "__main__":
    main()