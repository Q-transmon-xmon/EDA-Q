# ledit_launcher.py
import os
import platform
import shutil
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QDialog, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import QProcess, QSettings


class LedItController:
    """
    A controller class for managing the LedIt executable and its configuration.
    This class handles the initialization, configuration, and launching of the LedIt executable.
    """

    def __init__(self, parent=None):
        """
        Initializes the LedItController instance.

        :param parent: The parent widget (optional).
        """
        self.parent = parent
        self.process = QProcess()
        self.settings = QSettings("MyApp", "LedItLauncher")
        self.ledit_path = None

    def initialize(self):
        """
        Initializes the configuration and checks if LedIt is already configured.
        If not, it prompts the user to configure it.

        :return: True if LedIt is configured, False otherwise.
        """
        self.ledit_path = self.settings.value("leditPath", "")

        if not self._validate_path():
            return self._handle_missing_config()
        return True

    def _handle_missing_config(self):
        """
        Handles the case where LedIt is not configured.
        Prompts the user to configure LedIt and returns whether the configuration was successful.

        :return: True if the user configured LedIt, False otherwise.
        """
        dialog = QDialog(self.parent)
        dialog.setWindowTitle("LedIt Configuration Required")

        layout = QVBoxLayout()
        message = QLabel("LedIt executable is not configured. Would you like to configure it now?")
        layout.addWidget(message)

        btn_configure = QPushButton("Configure Now")
        btn_cancel = QPushButton("Cancel")

        btn_configure.clicked.connect(lambda: self._configure_and_close(dialog))
        btn_cancel.clicked.connect(dialog.reject)

        layout.addWidget(btn_configure)
        layout.addWidget(btn_cancel)
        dialog.setLayout(layout)

        return dialog.exec_() == QDialog.Accepted

    def _configure_and_close(self, dialog):
        """
        Configures the LedIt path and closes the dialog if successful.

        :param dialog: The dialog to close.
        """
        if self._request_path():
            dialog.accept()
        else:
            # If the user cancels, keep the dialog open
            pass

    def _validate_path(self):
        """
        Validates the LedIt executable path.
        Checks if the path exists, is an executable file, and has the correct permissions.

        :return: True if the path is valid, False otherwise.
        """
        if not self.ledit_path:
            return False

        if not os.path.exists(self.ledit_path):
            return False

        if platform.system() == "Windows":
            return self.ledit_path.lower().endswith((".exe", ".bat"))

        return os.access(self.ledit_path, os.X_OK)

    def _request_path(self):
        """
        Prompts the user to select the LedIt executable path.
        Validates the selected path and saves it if valid.

        :return: True if the path was successfully set, False otherwise.
        """
        filter_str = "Executable Files (*.exe *.bat)" if platform.system() == "Windows" else "All Files (*)"
        default_dir = os.path.expanduser("~")

        path, _ = QFileDialog.getOpenFileName(
            self.parent,
            "Select LedIt Executable",
            default_dir,
            filter_str
        )

        if not path:
            return False

        if self._set_path(path):
            QMessageBox.information(self.parent,
                                    "Configuration Saved",
                                    "LedIt path has been successfully configured")
            return True

        QMessageBox.warning(self.parent,
                            "Invalid Path",
                            "The selected file is not a valid LedIt executable")
        return False

    def _set_path(self, path):
        """
        Sets and saves the LedIt executable path.
        Ensures the file has the correct permissions on Unix systems.

        :param path: The path to the LedIt executable.
        :return: True if the path was successfully set, False otherwise.
        """
        try:
            # Ensure executable permissions on Unix systems
            if platform.system() != "Windows":
                os.chmod(path, 0o755)

            if self._validate_executable(path):
                self.ledit_path = path
                self.settings.setValue("leditPath", path)
                return True
        except Exception as e:
            print(f"Error setting path: {str(e)}")
        return False

    def _validate_executable(self, path):
        """
        Performs a deep validation of the LedIt executable.
        Checks if the file exists, is an executable file, and has the correct permissions.

        :param path: The path to the LedIt executable.
        :return: True if the executable is valid, False otherwise.
        """
        try:
            # Check if the file exists and is an executable file
            if not os.path.isfile(path):
                return False

            # Check file extension on Windows
            if platform.system() == "Windows":
                return path.lower().endswith((".exe", ".bat"))

            # Check execution permissions on Unix
            return os.access(path, os.X_OK)
        except Exception as e:
            print(f"Validation error: {str(e)}")
            return False

    def launch_ledit(self):
        """
        Launches the LedIt executable.
        Initializes the configuration and starts the LedIt process.
        """
        if not self.initialize():
            return

        self.process = QProcess(self.parent)
        self.process.errorOccurred.connect(self._handle_error)
        self.process.finished.connect(self._handle_finish)

        command = self._format_command()
        self.process.start(command)

    def _format_command(self):
        """
        Formats the command to launch LedIt, handling cross-platform differences.
        :return: The formatted command string.
        """
        if platform.system() == "Windows":
            return f'"{self.ledit_path}"'
        return self.ledit_path

    def _handle_error(self, error):
        """
        Handles errors that occur during the LedIt process launch.
        Displays an error message and suggests reconfiguration.

        :param error: The error that occurred.
        """
        QMessageBox.critical(self.parent,
                             "Process Error",
                             f"Failed to start LedIt: {self.process.errorString()}")
        # Suggest reconfiguration
        self.settings.remove("leditPath")

    def _handle_finish(self, exit_code, exit_status):
        """
        Handles the completion of the LedIt process.
        Displays a warning message if LedIt exits with a non-zero exit code.

        :param exit_code: The exit code of the LedIt process.
        :param exit_status: The exit status of the LedIt process.
        """
        if exit_code != 0:
            QMessageBox.warning(self.parent,
                                "Process Finished",
                                f"LedIt exited with code: {exit_code}")


def launch_ledit(parent=None):
    """
    A convenience function to launch LedIt.
    Creates a LedItController instance and calls the launch_ledit method.

    :param parent: The parent widget (optional).
    """
    controller = LedItController(parent)
    controller.launch_ledit()