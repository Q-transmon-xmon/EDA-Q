####################################
#Base class providing general methods
####################################

from addict import Dict
import copy, gdspy
import toolbox

class Base():
    """
    Base class providing general methods, including displaying parameters and importing/exporting functionalities.
    All subclasses inherit from this class and must implement necessary methods (such as `extract_options` and `inject_options`).
    """
    def __init__(self):
        """
        Initializes the Base class.

        Input:
            None

        Output:
            None
        """
        return

    def show_options(self):
        """
        Displays all parameters of the current object.

        Note:
            Depends on the `extract_options` method, which must be implemented by subclasses to extract parameters.

        Input:
            None

        Output:
            None (parameters are printed using `toolbox.show_options`).
        """
        options = self.extract_options()  # Extract all parameters of the current object
        toolbox.show_options(options)  # Call the utility class to display parameters
        return

    def show_names(self):
        """
        Displays the list of parameter names of the current object.

        Note:
            Depends on the `extract_options` method, which must be implemented by subclasses to extract parameters.

        Input:
            None

        Output:
            None (parameter names are printed using `toolbox.show_options`).
        """
        options = self.extract_options()  # Extract all parameters of the current object
        toolbox.show_options(list(options.keys()))  # Display the list of parameter names
        return

    def export_options(self, path):
        """
        Exports the current object's parameters to a specified path.

        Input:
            path: str, the path to export the file.

        Output:
            None (parameters are saved to the specified path).
        """
        options = self.extract_options()  # Extract all parameters of the current object
        toolbox.export_options(data=options, path=path)  # Call the utility class to save parameters to a file
        return

    def import_options(self, path):
        """
        Imports parameters from a specified path and injects them into the current object.

        Input:
            path: str, the path to the parameter file.

        Output:
            options: dict, the imported parameters.
        """
        options = toolbox.import_options(path)  # Import parameters from the path
        self.inject_options(options)  # Inject the imported parameters into the current object
        return copy.deepcopy(options)  # Return the imported parameters (deep copy)

    @property
    def options(self):
        """
        Property method that returns a snapshot of the current object's parameters.

        Input:
            None

        Output:
            options: dict, the current object's parameters (deep copy).
        """
        options = self.extract_options()  # Extract all parameters of the current object
        return copy.deepcopy(options)  # Return a deep copy of the parameters