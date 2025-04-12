# main.py
import sys

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication
from main_window import MainWindow
from app_controller import AppController

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))

    window = MainWindow()
    controller = AppController(window)  # 注入依赖

    window.show()
    sys.exit(app.exec_())