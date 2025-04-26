from base.cmpnts_base import CmpntsBase
from addict import Dict
import func_modules
import copy

class ControlLines(CmpntsBase):
    """
    ControlLinesclass，Inherited fromCmpntsBase，Used for managing and operating control line components。
    """

    def __init__(self, **init_ops):
        """
        initializationControlLinesobject。

        input：
            init_ops: dict，initialization所需的参数。

        output：
            not have
        """
        self.initialization(**init_ops)  # Call initialization method
        return
    
    def initialization(self, **init_ops):
        """
        Initialize the set of control line components。

        input：
            init_ops: dict，Generate initialization parameters for control line components。

        output：
            not have
        """
        # Initialize component name list
        self.cmpnt_name_list = []
        # Options for calling functional modules to generate control line components
        options = func_modules.ctls.generate_control_lines(**init_ops)
        self.inject_options(options)  # Inject generated parameters
        return
    
    def mirror_ControlLine(self, name_list):
        """
        Mirror the specified control line components（Horizontal mirroring）。

        input：
            name_list: list，Contains a list of control line names that need to be mirrored。

        output：
            not have
        """
        # Get the parameters of the current control line component
        ctls_ops = self.options
        for name in name_list:
            # Generate new names for the mirrored control lines
            new_name = name + "_mirror"
            ctl_ops = copy.deepcopy(ctls_ops[name])  # Obtain the parameters of the original control line
            new_ctl_ops = copy.deepcopy(ctl_ops)  # Create a parameter copy of the mirror control line
            new_ctl_ops.name = new_name  # Set a new name for the mirror control line

            # Mirror the path of the control line
            path = copy.deepcopy(ctl_ops.path)
            new_path = []
            for pos in path:
                new_pos = (-pos[0], pos[1])  # Horizontal mirror operation
                new_path.append(copy.deepcopy(new_pos))
            new_ctl_ops.path = copy.deepcopy(new_path)  # Update the path of the image

            # Add the mirrored control line parameters to the component collection
            ctls_ops[new_name] = copy.deepcopy(new_ctl_ops)

        # Inject updated control line component parameters
        self.inject_options(ctls_ops)
        return
