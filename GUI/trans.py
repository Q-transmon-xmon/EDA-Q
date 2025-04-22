"""
图标颜色转换工具 (PyQt5 实现)
运行前安装依赖：pip install pyqt5
"""

import os
import sys
from PyQt5.QtGui import QColor, QPainter, QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication  # 添加QApplication


def convert_icon_color(input_path, output_path, target_color):
    """
    转换图标颜色
    :param input_path:  输入文件路径（PNG格式，白色图标）
    :param output_path: 输出文件路径
    :param target_color: 目标颜色（支持Qt颜色常量/QColor/十六进制）
    """
    # 加载原始图标
    pixmap = QPixmap(input_path)
    if pixmap.isNull():
        raise ValueError(f"无法加载输入文件，路径：{input_path}，请检查路径是否正确")

    # 创建临时画布
    colored_pixmap = QPixmap(pixmap.size())
    colored_pixmap.fill(Qt.transparent)

    # 颜色处理
    painter = QPainter(colored_pixmap)
    painter.drawPixmap(0, 0, pixmap)
    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)

    # 解析颜色参数
    if isinstance(target_color, str):
        if target_color.startswith("#"):  # 十六进制格式
            color = QColor(target_color)
        else:  # Qt颜色常量名
            color = getattr(Qt, target_color, Qt.black)
    elif isinstance(target_color, QColor):
        color = target_color
    else:
        raise ValueError("目标颜色格式不正确，必须是字符串或QColor对象")

    painter.fillRect(colored_pixmap.rect(), color)
    painter.end()

    # 保存文件
    if not colored_pixmap.save(output_path):
        raise RuntimeError(f"文件保存失败，路径：{output_path}，请检查输出路径是否有写入权限")


def convert_folder_icons(input_folder, output_folder, target_color):
    """
    批量转换文件夹中的所有PNG图标颜色
    :param input_folder: 输入文件夹路径
    :param output_folder: 输出文件夹路径
    :param target_color: 目标颜色（支持Qt颜色常量/QColor/十六进制）
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 遍历输入文件夹中的所有文件
    for filename in os.listdir(input_folder):
        if filename.endswith('.png'):
            input_file = os.path.join(input_folder, filename)
            output_file = os.path.join(output_folder, filename)  # 输出同名文件
            try:
                convert_icon_color(input_file, output_file, target_color)
                print(f"成功转换：{input_file} --> {output_file}")
            except Exception as e:
                print(f"转换错误：{input_file}，错误：{str(e)}")


def main():
    app = QApplication(sys.argv)  # 创建QApplication实例

    # 用户输入参数（可修改以下值）
    input_folder = "D:/work/QEDA_3/icons/toolbar"  # 输入文件夹路径
    output_folder = "D:/work/QEDA_3/icons/toolbar/output/"  # 输出文件夹路径
    target_color = "#00BFFF"  # 目标颜色（这里使用浅蓝色）

    # 执行转换
    convert_folder_icons(input_folder, output_folder, target_color)

    sys.exit(app.exec_())  # 完成后退出应用程序


if __name__ == "__main__":
    main()