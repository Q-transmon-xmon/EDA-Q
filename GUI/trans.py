"""
Icon color conversion tool (PyQt5 achieve)
Install dependencies before running: pip install pyqt5
"""

import os
import sys
from PyQt5.QtGui import QColor, QPainter, QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication


def convert_icon_color(input_path, output_path, target_color):
    """
    Convert icon color
    :param input_path: Input file path (PNG format, White Icon)
    :param output_path: Output file path
    :param target_color: Target Color (supports Qt color constant/QColor/hexadecimal)
    """
    # Load original icon
    pixmap = QPixmap(input_path)
    if pixmap.isNull():
        raise ValueError(f"Failed to load input file, path: {input_path}. Please check the path.")

    # Create a temporary canvas
    colored_pixmap = QPixmap(pixmap.size())
    colored_pixmap.fill(Qt.transparent)

    # Color processing
    painter = QPainter(colored_pixmap)
    painter.drawPixmap(0, 0, pixmap)
    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)

    # Analyze color parameters
    if isinstance(target_color, str):
        if target_color.startswith("#"):  # Hexadecimal format
            color = QColor(target_color)
        else:  # Qt color constant name
            color = getattr(Qt, target_color, Qt.black)
    elif isinstance(target_color, QColor):
        color = target_color
    else:
        raise ValueError("Invalid target color format. Must be a string or QColor object.")

    painter.fillRect(colored_pixmap.rect(), color)
    painter.end()

    # Save the file
    if not colored_pixmap.save(output_path):
        raise RuntimeError(f"Failed to save file, path: {output_path}. Please check if the output path is writable.")


def convert_folder_icons(input_folder, output_folder, target_color):
    """
    Batch convert all PNG icons in the folder to the target color
    :param input_folder: Input folder path
    :param output_folder: Output folder path
    :param target_color: Target Color (supports Qt color constant/QColor/hexadecimal)
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
                print(f"Successfully converted: {input_file} --> {output_file}")
            except Exception as e:
                print(f"Conversion error: {input_file}, Error: {str(e)}")


def main():
    app = QApplication(sys.argv)  # Create a QApplication instance

    # User input parameters (The following values can be modified)
    input_folder = "D:/work/QEDA_3/icons/toolbar"  # Input folder path
    output_folder = "D:/work/QEDA_3/icons/toolbar/output/"  # Output folder path
    target_color = "#00BFFF"  # Target Color (Light blue is used here)

    # Perform conversion
    convert_folder_icons(input_folder, output_folder, target_color)

    sys.exit(app.exec_())  # Exit the application after completion


if __name__ == "__main__":
    main()