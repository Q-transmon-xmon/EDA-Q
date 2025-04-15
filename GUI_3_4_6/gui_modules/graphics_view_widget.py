import sys
import tkinter as tk
import gdspy
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PyQt5.QtGui import QWindow
from PyQt5.QtCore import QTimer

# --- Step 1: Intercept the creation process of gdspy's LayoutViewer ---
original_LayoutViewer = gdspy.LayoutViewer


class PatchedLayoutViewer(original_LayoutViewer):
    def __init__(self, *args, **kwargs):
        # Forcefully hide the Tkinter main window (to prevent it from popping up)
        self._tk_root = tk.Tk()
        self._tk_root.withdraw()
        # Call the original LayoutViewer initialization
        super().__init__(*args, **kwargs)
        # Get the actual Toplevel window used
        self.tk_top = self.root  # gdspy uses Toplevel internally
        self.tk_top.deiconify()  # Allow display (controlled by Qt later)


# Temporarily replace gdspy's LayoutViewer class
gdspy.LayoutViewer = PatchedLayoutViewer


# --- Step 2: Create a PyQt5 window and embed the gdspy window ---
class GDSViewerIntegration(QMainWindow):
    def __init__(self, gds_instance):
        super().__init__()
        self.gds_instance = gds_instance
        self.init_ui()

    def init_ui(self):
        # Set up the main window
        self.setWindowTitle("GDS Viewer in PyQt5")
        container = QWidget()
        self.setCentralWidget(container)
        layout = QVBoxLayout(container)

        # Call the original function to generate the gdspy window (intercepted by the monkey patch)
        self.gds_instance.show_gds()
        viewer = self.gds_instance.viewer  # Assume the viewer attribute saves the instance

        # Get the Tkinter window handle
        hwnd = int(viewer.tk_top.frame(), 16)  # Key: Get the Toplevel handle

        # Embed into the Qt window
        qwindow = QWindow.fromWinId(hwnd)
        widget = QWidget.createWindowContainer(qwindow, self)
        layout.addWidget(widget)

        # Resize the window
        self.resize(800, 600)

        # Periodically process Tkinter events
        self.timer = QTimer()
        self.timer.timeout.connect(viewer.tk_top.update)
        self.timer.start(20)  # Trigger every 20ms


# --- Example usage ---
class MyGDSClass:
    def __init__(self):
        self.lib = gdspy.GdsLibrary()
        self.viewer = None  # To save the gdspy viewer instance

    def draw_gds(self):
        # Example: Create a simple structure
        cell = self.lib.new_cell('MAIN')
        cell.add(gdspy.Rectangle((0, 0), (1000, 1000)))

    def show_gds(self):
        self.draw_gds()
        # Create Viewer and save the instance
        self.viewer = gdspy.LayoutViewer(library=self.lib)  # Modified by the monkey patch


if __name__ == "__main__":
    app = QApplication(sys.argv)
    my_gds = MyGDSClass()
    window = GDSViewerIntegration(my_gds)
    window.show()
    sys.exit(app.exec_())