from base.gds_base import GdsBase
from addict import Dict
import copy

class LibraryBase(GdsBase):
    """
    LibraryBase serves as the base class for each component, providing common methods including parameter extraction, injection, and modification.
    """

    def __init__(self, options=Dict()):
        """
        Initializes the LibraryBase object.

        Input:
            options: dict, the initialization parameter dictionary, default is empty.

        Output:
            None
        """
        self.initialization(options)  # Call the initialization method
        return

    def initialization(self, options=Dict()):
        """
        Initializes the object's parameters and calculates common parameters.

        Input:
            options: dict, the initialization parameter dictionary, default is empty.

        Output:
            None
        """
        # Set default parameters
        for op_name, op in self.default_options.items():
            super().__setattr__(op_name, op)

        # Save the list of parameter names
        self.op_name_list = list(self.__dict__.keys())

        # Inject parameters and calculate common parameters
        self.inject_options(Dict(options))
        self.calc_general_ops()  # Calculate common parameters
        return

    def extract_options(self):
        """
        Extracts all parameters of the current object.

        Input:
            None

        Output:
            options: dict, a dictionary containing all current parameters.
        """
        options = Dict()
        # Iterate over the list of parameter names and extract corresponding attributes
        for op_name in self.op_name_list:
            op = getattr(self, op_name)
            options[op_name] = copy.deepcopy(op)  # Deep copy parameter values
        return copy.deepcopy(options)  # Return a deep copy of the parameter dictionary

    def inject_options(self, options):
        """
        Injects parameters into the object, only covering existing parameters.

        Input:
            options: dict, the parameter dictionary to be injected.

        Output:
            None
        """
        for k, v in options.items():
            if k in self.op_name_list:  # If the parameter name is in the defined parameter list
                super().__setattr__(k, copy.deepcopy(v))  # Set parameter value
        return

    def change_option(self, op_name, op_value):
        """
        Modifies the value of a single parameter.

        Input:
            op_name: str, the name of the parameter to be modified.
            op_value: any type, the new parameter value.

        Output:
            None

        Exception:
            ValueError: Throws an exception when the parameter name does not exist.
        """
        if not hasattr(self, op_name):  # Check if the parameter exists
            raise ValueError("There is no parameter named {}".format(op_name))
        setattr(self, op_name, op_value)  # Modify the parameter value
        return

    def change_options(self, new_options):
        """
        Modifies the values of multiple parameters.

        Input:
            new_options: dict, a dictionary containing the names and values of the parameters to be modified.

        Output:
            None

        Exception:
            ValueError: Throws an exception when some parameter names do not exist.
        """
        new_options = copy.deepcopy(new_options)  # Deep copy new parameters
        options = copy.deepcopy(self.options)  # Extract a deep copy of current parameters
        
        # Iterate over the new parameter dictionary, check and update parameters
        for op_name, op_value in new_options.items():
            if not hasattr(self, op_name):  # Check if the parameter exists
                raise ValueError("{} has no parameter named {}".format(self.name, op_name))
            options[op_name] = copy.deepcopy(op_value)  # Update parameter value

        # Inject the updated parameters
        self.inject_options(options)
        return