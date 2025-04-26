from base.cmpnts_base import CmpntsBase
from addict import Dict
import func_modules

class AirBridges(CmpntsBase):
    """
    AirBridgesclass，Inherited fromCmpntsBase，Used for managing and operating air bridge components（AirBridge）。
    """

    def __init__(self, **init_ops):
        """
        initializationAirBridgesobject。

        input：
            init_ops: dict，initialization所需的参数。

        output：
            not have
        """
        self.initialization(**init_ops)  # Call initialization method
        return
    
    def initialization(self, **init_ops):
        """
        Initialize the collection of air bridge components。

        input：
            init_ops: dict，Generate initialization parameters for air bridge components。

        output：
            not have
        """
        # Initialize component name list
        self.cmpnt_name_list = []
        # Call the function module to generate parameters for the air bridge component
        options = func_modules.tmls.generate_transmission_lines(**init_ops)
        self.inject_options(options)  # Inject generated parameters
        return
    
    def counts(self):
        """
        Count the current number of air bridge components。

        input：
            not have

        output：
            count: int，The current quantity of air bridge components。
        """
        ops = self.options  # Extract current component parameters
        return len(ops)  # Return the number of components
