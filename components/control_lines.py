from base.cmpnts_base import CmpntsBase
from addict import Dict
import func_modules
import copy

class ControlLines(CmpntsBase):
    """
    ControlLines class, inherited from CmpntsBase, used for managing and operating control line components.
    """

    def __init__(self, **init_ops):
        """
        Initialize the ControlLines object.

        Input:
            init_ops: dict, parameters required for initialization.

        Output:
            None
        """
        self.initialization(**init_ops)  # Call initialization method
        return
    
    def initialization(self, **init_ops):
        """
        Initialize the set of control line components.

        Input:
            init_ops: dict, parameters for generating control line components.

        Output:
            None
        """
        # Initialize component name list
        self.cmpnt_name_list = []
        # Call the function module to generate options for control line components
        options = func_modules.ctls.generate_control_lines(**init_ops)
        self.inject_options(options)  # Inject generated parameters
        return
    
    def mirror_ControlLine(self, name_list):
        """
        Mirror the specified control line components (horizontal mirroring).

        Input:
            name_list: list, contains the names of control lines that need to be mirrored.

        Output:
            None
        """
        # Get the parameters of the current control line components
        ctls_ops = self.options
        for name in name_list:
            # Generate new names for the mirrored control lines
            new_name = name + "_mirror"
            ctl_ops = copy.deepcopy(ctls_ops[name])  # Get the parameters of the original control line
            new_ctl_ops = copy.deepcopy(ctl_ops)  # Create a copy of the mirrored control line parameters
            new_ctl_ops.name = new_name  # Set a new name for the mirrored control line

            # Mirror the path of the control line
            path = copy.deepcopy(ctl_ops.path)
            new_path = []
            for pos in path:
                new_pos = (-pos[0], pos[1])  # Horizontal mirror operation
                new_path.append(copy.deepcopy(new_pos))
            new_ctl_ops.path = copy.deepcopy(new_path)  # Update the path of the mirrored control line

            # Add the mirrored control line parameters to the component collection
            ctls_ops[new_name] = copy.deepcopy(new_ctl_ops)

        # Inject updated control line component parameters
        self.inject_options(ctls_ops)
        return
