# signal_handler.py
from PyQt5.QtCore import pyqtSignal, QObject

class SignalHandler(QObject):
    current_design_changed = pyqtSignal(object)  # Define a signal to pass the reference of the current design

# Create a global signal handler instance
signal_handler = SignalHandler()