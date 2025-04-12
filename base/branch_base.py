from addict import Dict
import toolbox
import copy

class BranchBase():
    """
    The BranchBase class, a base class for handling logic of different branches.
    Provides common functionalities such as branch processing and hash method generation.
    """

    def __init__(self, **branch_options):
        """
        Initializes the BranchBase object.

        Input:
            branch_options: dict, branch option parameters for initializing branch logic.

        Output:
            None
        """
        self.branch_options = Dict(branch_options)  # Store branch options as an accessible dictionary structure
        return

    def branch_process(self):
        """
        Executes the corresponding branch processing logic based on branch options.

        Logic:
            1. Generate a unique hash value based on the keys of `branch_options`.
            2. If the generated hash value is empty, return an empty dictionary.
            3. If the hash value is not defined as a class method, throw an exception.
            4. If the method corresponding to the hash value exists, call that method to execute branch logic.

        Input:
            None (operates based on class attribute `branch_options`).

        Output:
            result: dict, the result of branch processing (returned after a deep copy).

        Exception:
            ValueError: Thrown when the generated hash value is not defined as a class method.
        """
        # Extract branch options and generate a hash value
        branch_options = copy.deepcopy(self.branch_options)  # Deep copy branch options to prevent modification of original data
        hash_num = self.hash_method(list(branch_options.keys()))  # Generate hash value

        # If the hash value is empty, directly return an empty dictionary
        if hash_num == "":
            return Dict()
        
        # If the class does not have a method corresponding to the hash value, throw an exception
        if not hasattr(self, hash_num):
            raise ValueError("No method {} defined".format(hash_num))
        
        # Call the method corresponding to the hash value for branch processing
        result = getattr(self, hash_num)(branch_options)

        # Return a deep copy of the processing result
        return copy.deepcopy(result)

    def hash_method(self, options_name_list):
        """
        Generate a unique hash value based on the list of branch option names.

        Input:
            options_name_list: list, a list of branch option names.

        Output:
            hash_num: str, the generated hash value, used to identify the method name of branch logic.
        """
        # Use a utility function to sort and join the option name list into a string
        hash_num = toolbox.sort_and_join(options_name_list, join_tool="__")
        return hash_num

    def options(self, gene_ops):
        """
        Extract option parameters from an operation object.

        Input:
            gene_ops: object, an object containing option parameters.

        Output:
            options: dict, the extracted option parameters (returned after a deep copy).
        """
        return copy.deepcopy(gene_ops.options)  # Return a deep copy of option parameters