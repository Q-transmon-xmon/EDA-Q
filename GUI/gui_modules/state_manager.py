# state_manager.py
import os
import sys

# Get the directory where the current script is located
current_path = os.path.dirname(os.path.abspath(__file__))
GUI_PATH = os.path.dirname(current_path)
PROJ_PATH = os.path.dirname(GUI_PATH)

# Add paths
sys.path.append(GUI_PATH)
sys.path.append(PROJ_PATH)

from GUI.gui_modules.signal_handler import signal_handler
from GUI.gui_modules.global_parameters import designs  # Import the global designs dictionary

class StateManager:
    def __init__(self):
        self.current_design = None

    def set_current_design(self, design_name):
        """Set the current design and emit a signal."""
        if design_name in designs:
            self.current_design = designs[design_name][0]  # Get the design instance
            signal_handler.current_design_changed.emit(self.current_design)  # Trigger the signal
            print(f"Current design set to: {design_name}")
        else:
            print(f"Design '{design_name}' not found in designs dictionary.")

# Create a global state manager instance
state_manager = StateManager()