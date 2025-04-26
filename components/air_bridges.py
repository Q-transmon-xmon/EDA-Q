from base.cmpnts_base import CmpntsBase
from addict import Dict
import func_modules

class AirBridges(CmpntsBase):
    """
    AirBridges class, inherited from CmpntsBase, used for managing and operating air bridge components (AirBridge).
    """

    def __init__(self, **init_ops):
        """
        Initialize the AirBridges object.

        Input:
            init_ops: dict, parameters required for initialization.

        Output:
            None
        """
        self.initialization(**init_ops)  # Call initialization method
        return
    
    def initialization(self, **init_ops):
        """
        Initialize the collection of air bridge components.

        Input:
            init_ops: dict, parameters for generating air bridge components.

        Output:
            None
        """
        # Initialize component name list
        self.cmpnt_name_list = []
        # Call the function module to generate parameters for the air bridge component
        options = func_modules.tmls.generate_transmission_lines(**init_ops)
        self.inject_options(options)  # Inject generated parameters
        return
    
    def counts(self):
        """
        Count the current number of air bridge components.

        Input:
            None

        Output:
            count: int, the current quantity of air bridge components.
        """
        ops = self.options  # Extract current component parameters
        return len(ops)  # Return the number of components
