import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QDialog, QDialogButtonBox, QLabel,
                             QLineEdit, QVBoxLayout, QHBoxLayout, QMessageBox)
from PyQt5.QtCore import QSettings, pyqtSignal, Qt


class BaseModifierDialog(QDialog):
    """
    Abstract base dialog for parameter modification with enhanced navigation and validation

    Signals:
    - designUpdated(object): Emitted when modifications are successfully applied

    Subclasses must implement:
    - process_values(values): Process validated input values

    Features:
    - Tab navigation with smart default filling
    - Input validation framework
    - Settings persistence
    - Accessibility support
    """

    designUpdated = pyqtSignal(object)

    def __init__(self, design, title, defaults, input_labels):
        super().__init__()
        self.design = design
        self.settings = QSettings("MyCompany", "QCModifier")
        self.defaults = defaults
        self.input_labels = input_labels

        # UI initialization
        self.setFont(QFont("Arial", 10))
        self.setup_ui(title)
        self.load_settings()

    def setup_ui(self, title):
        """Initialize UI components with proper layout and accessibility"""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setAccessibleName("Dialog Title")
        layout.addWidget(title_label)

        # Input fields
        self.line_edits = []
        for idx, (label, default) in enumerate(zip(self.input_labels, self.defaults)):
            row = QHBoxLayout()
            row.setSpacing(10)

            lbl = QLabel(label)
            lbl.setAccessibleName(f"{label.strip(':')} Label")

            le = QLineEdit()
            le.setPlaceholderText(str(default))
            le.setProperty("default_value", default)
            le.setAccessibleDescription(f"Input field for {label.strip(':')}")
            le.installEventFilter(self)
            le.returnPressed.connect(self.validate_inputs)

            row.addWidget(lbl)
            row.addWidget(le)
            layout.addLayout(row)
            self.line_edits.append(le)

            if idx == 0:
                le.setFocus()

        # Buttons
        self.buttonBox = QDialogButtonBox()
        self.buttonBox.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        ok_btn = self.buttonBox.button(QDialogButtonBox.Ok)
        ok_btn.setAccessibleName("Confirm Button")
        cancel_btn = self.buttonBox.button(QDialogButtonBox.Cancel)
        cancel_btn.setAccessibleName("Cancel Button")

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.buttonBox)
        layout.addLayout(button_layout)

        # Signals
        self.buttonBox.accepted.connect(self.validate_inputs)
        self.buttonBox.rejected.connect(self.reject)

        # Window configuration
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.adjustSize()

    def eventFilter(self, source, event):
        """Handle Tab key event logic"""
        if event.type() == QtCore.QEvent.KeyPress and event.key() == Qt.Key_Tab:
            current_index = self.line_edits.index(source)
            self._handle_tab_navigation(current_index)
            return True  # Prevent the event from propagating further
        return super().eventFilter(source, event)

    def _handle_tab_navigation(self, current_index):
        """Handle Tab key navigation and default value filling"""
        # Fill the default value for the current line
        current_le = self.line_edits[current_index]
        if not current_le.text().strip():
            current_le.setText(current_le.property("default_value"))

        # Calculate the next focus position
        next_index = current_index + 1
        if next_index >= len(self.line_edits):
            next_index = 0  # Loop the focus

        # Set focus and select text
        next_le = self.line_edits[next_index]
        next_le.setFocus()
        next_le.selectAll()


    def validate_inputs(self):
        """Comprehensive validation workflow"""
        try:
            # Collect values with fallback to defaults
            values = [
                le.text().strip() or le.property("default_value")
                for le in self.line_edits
            ]

            # Process and persist
            if self.process_values(values):
                self.save_settings()
                return True

        except ValueError as ve:
            self.show_error("Input Error", f"Validation Error:\n{str(ve)}")
        except RuntimeError as re:
            self.show_error("System Error", f"Operation Failed:\n{str(re)}")
        except Exception as e:
            self.show_error("Unexpected Error", f"An error occurred:\n{str(e)}")

        return False

    def show_error(self, title, message):
        """Standardized error display"""
        QMessageBox.critical(
            self,
            title,
            message,
            QMessageBox.Ok
        )

    def load_settings(self):
        """Load settings with class-specific and field-specific keys"""
        class_name = self.__class__.__name__
        for i, le in enumerate(self.line_edits):
            # 生成带标签的键名 示例: "CapacitanceModifier/Qubit Name"
            field_key = self.input_labels[i].replace(':', '').strip()
            key = f"{class_name}/{field_key}"
            le.setText(self.settings.value(key, ""))

    def save_settings(self):
        """Save settings with contextual keys"""
        class_name = self.__class__.__name__
        for i, le in enumerate(self.line_edits):
            field_key = self.input_labels[i].replace(':', '').strip()
            key = f"{class_name}/{field_key}"

            # 仅保存有效输入
            value = le.text().strip()
            default = str(le.property("default_value"))
            self.settings.setValue(key, value if value != default else "")

    def process_values(self, values):
        """Abstract method for value processing (MUST be implemented by subclasses)"""
        raise NotImplementedError

#
# # Example Implementation
# class SampleDialog(BaseModifierDialog):
#     """Concrete implementation example"""
#
#     def process_values(self, values):
#         # Demo processing logic
#         if not all(values):
#             raise ValueError("All fields must contain valid values")
#
#         QMessageBox.information(
#             self,
#             "Success",
#             f"Parameters received:\n{', '.join(values)}",
#             QMessageBox.Ok
#         )
#         return True
#
#
# if __name__ == "__main__":
#     app = QtWidgets.QApplication(sys.argv)
#     dialog = SampleDialog(
#         design=None,
#         title="Parameter Editor",
#         defaults=["Test1", "100"],
#         input_labels=["Parameter 1:", "Value 2:"]
#     )
#     dialog.exec_()
#     sys.exit(app.exec_())