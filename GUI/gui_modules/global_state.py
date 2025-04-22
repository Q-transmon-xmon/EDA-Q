import os
import sys
# Get the directory where the current script is located
current_path = os.path.dirname(os.path.abspath(__file__))
GUI_PATH = os.path.dirname(current_path)
PROJ_PATH = os.path.dirname(GUI_PATH)

# Add paths
sys.path.append(GUI_PATH)
sys.path.append(PROJ_PATH)

from typing import Optional, Tuple, Dict, List
from PyQt5.QtCore import pyqtSignal, QObject
import GUI.gui_modules.global_parameters as gp  # Access global variables via module name
from api.design import Design

class GlobalState(QObject):
    """Global state management class (singleton pattern), encapsulating all global data operations"""

    # Signal definitions
    design_created = pyqtSignal(str)
    design_renamed = pyqtSignal(str, str)
    design_removed = pyqtSignal(str)
    design_metadata_updated = pyqtSignal(str)
    current_design_changed = pyqtSignal(str)
    design_updated = pyqtSignal(str)
    design_path_updated = pyqtSignal(str, str)  # Design path updated: (design_name, new_path)

    # History for undo/redo functionality
    history_stack = []
    redo_stack = []

    def __init__(self):
        super().__init__()

    # --------------------------
    # Design name operations
    # --------------------------
    def get_current_design_name(self) -> Optional[str]:
        """Get the current design name"""
        return gp.current_design_name

    def get_all_design_names(self) -> List[str]:
        """Get list of all design names"""
        return list(gp.global_designs.keys())

    def design_exists(self, name: str) -> bool:
        """Check if a design exists"""
        return name in gp.global_designs

    # --------------------------
    # Design instance operations
    # --------------------------
    def get_design(self, name: str) -> Optional[Design]:
        """Get design instance by name"""
        if not self.design_exists(name):
            return None
        return gp.global_designs[name][0]

    def get_design_metadata(self, name: str) -> Optional[Tuple[Design, str]]:
        """Get design metadata (instance + path)"""
        return gp.global_designs.get(name, None)

    # --------------------------
    # State modification operations
    # --------------------------
    def update_current_design_name(self, design_name: str) -> None:
        """Update current design name (with validation)"""
        if design_name is None or self.design_exists(design_name):
            if gp.current_design_name != design_name:
                gp.current_design_name = design_name
                self.current_design_changed.emit(design_name)
        else:
            raise ValueError(f"Invalid design name: {design_name}")

    def create_design(self, name: str, path: Optional[str] = None) -> None:
        """Create new design (with conflict check)"""
        if self.design_exists(name):
            raise ValueError(f"Design '{name}' already exists")
        gp.global_designs[name] = (Design(), path)
        self.history_stack.append(('create', name))
        self.design_created.emit(name)
        self.update_current_design_name(name)

    def rename_design(self, old_name: str, new_name: str) -> None:
        """Rename a design (atomic operation)"""
        if not self.design_exists(old_name):
            raise KeyError(f"Design '{old_name}' does not exist")
        if self.design_exists(new_name):
            raise ValueError(f"Name '{new_name}' is already occupied")

        data = gp.global_designs.pop(old_name)
        gp.global_designs[new_name] = data

        if gp.current_design_name == old_name:
            gp.current_design_name = new_name
            self.current_design_changed.emit(new_name)
        self.design_renamed.emit(old_name, new_name)

    def delete_design(self, name: str) -> None:
        """Delete a design (safe operation)"""
        if not self.design_exists(name):
            raise KeyError(f"Design '{name}' does not exist")

        del gp.global_designs[name]
        self.history_stack.append(('delete', name))
        self.design_removed.emit(name)

        if gp.current_design_name == name:
            gp.current_design_name = None
            self.current_design_changed.emit(None)

    def update_design(self, design_name: str, updated_design: Design) -> None:
        """Update design instance (preserve path)"""
        if not self.design_exists(design_name):
            raise KeyError(f"Design '{design_name}' does not exist")

        old_path = gp.global_designs[design_name][1]
        gp.global_designs[design_name] = (updated_design, old_path)
        self.design_updated.emit(design_name)

    def update_design_path(self, design_name: str, new_path: str) -> None:
        """
        Update design storage path
        Args:
            design_name: design name
            new_path: must be a valid file path
        """
        if not self.design_exists(design_name):
            raise KeyError(f"Design '{design_name}' does not exist")

        if not os.path.isabs(new_path):
            raise ValueError("Path must be absolute")

        # Preserve design instance and update path
        old_design = gp.global_designs[design_name][0]
        gp.global_designs[design_name] = (old_design, new_path)
        self.design_path_updated.emit(design_name, new_path)

    def save_design(self, design_name: str, path: Optional[str] = None) -> None:
        """
        Save design to specified path as a txt file (persist to filesystem)
        Args:
            design_name: design name
            path: optional path. If None, use current storage path
        """
        design = self.get_design(design_name)
        if not design:
            raise KeyError(f"Design '{design_name}' does not exist")

        # Determine final path
        final_path = path or gp.global_designs[design_name][1]
        if not final_path:
            raise ValueError("Must provide save path")

        # Ensure the file has a .txt extension
        root, ext = os.path.splitext(final_path)
        if ext.lower() != '.txt':
            final_path = root + '.txt'

        # Save design content to txt file
        try:
            with open(final_path, 'w') as file:
                # Assuming design has __str__ method or adjust this to get the content
                file.write(str(design))
        except IOError as e:
            raise IOError(f"Failed to save design to {final_path}: {e}")

        # Update storage path if new path provided
        if path is not None:
            self.update_design_path(design_name, final_path)  # Update with the final path
        else:
            self.design_metadata_updated.emit(design_name)

    def save_current_design(self, path: Optional[str] = None) -> None:
        """
        Save current design (convenience method)
        Args:
            path: optional path. If None, use current storage path
        """
        current_name = self.get_current_design_name()
        if not current_name:
            raise ValueError("No active design currently")
        self.save_design(current_name, path)

    # --------------------------
    # Undo/Redo operations
    # --------------------------
    def can_undo(self) -> bool:
        """Check if there are actions to undo"""
        return len(self.history_stack) > 0

    def can_redo(self) -> bool:
        """Check if there are actions to redo"""
        return len(self.redo_stack) > 0

    def undo(self) -> None:
        """Undo the last action"""
        if not self.can_undo():
            raise Exception("No actions to undo")

        action, name = self.history_stack.pop()
        if action == 'create':
            self.delete_design(name)
        elif action == 'delete':
            # Logic to restore the deleted design (requires keeping track of its data)
            raise NotImplementedError("Restore logic for deleted design needs to be implemented")

    def redo(self) -> None:
        """Redo the last undone action"""
        if not self.can_redo():
            raise Exception("No actions to redo")

        action, name = self.redo_stack.pop()
        if action == 'create':
            self.create_design(name)
        elif action == 'delete':
            # Logic to re-delete the design (requires keeping track of its data)
            raise NotImplementedError("Re-delete logic for design needs to be implemented")

# Singleton instance
global_state = GlobalState()