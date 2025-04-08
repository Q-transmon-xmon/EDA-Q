#################################################################
#The Tag class is used for managing and operating on tag objects.
#################################################################

from addict import Dict
from base.base import Base
import copy
import func_modules

class Tag(Base):
    """
    The Tag class is used for managing and operating on tag objects.
    """

    def __init__(self, **init_ops):
        """
        Initializes the Tag object.

        Input:
            init_ops: dict, containing parameters for initializing the tag object.

        Output:
            None
        """
        self.initialization(**init_ops)
        return

    def initialization(self, **init_ops):
        """
        Initializes the Tag object, including setting the parameter list and injecting options.

        Input:
            init_ops: dict, containing initialization parameters for generating tags.

        Output:
            None
        """
        # Save the list of current object attribute names
        self.op_name_list = list(self.__dict__.keys())
        # Call the module to generate tag options
        options = func_modules.tag.generate_tag(**init_ops)
        self.inject_options(options)  # Inject the generated options into the object
        return

    def inject_options(self, options):
        """
        Inject option parameters into the Tag object.

        Input:
            options: dict, containing option parameters to be injected.

        Output:
            None
        """
        # Logic not implemented yet, to be supplemented with specific implementation of injecting options
        return

    def extract_options(self):
        """
        Extract option parameters from the object.

        Input:
            None

        Output:
            options: Dict, containing all option parameters of the current object.
        """
        options = Dict()
        # Iterate over the attribute name list and retrieve related options from the object
        for op_name in self.op_name_list:
            options[op_name] = getattr(self, op_name).options
        return copy.deepcopy(options)  # Return a deep copy of the options