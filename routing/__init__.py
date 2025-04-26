#########################################################################
# File name: __init__.py
# Description: This module is used for the initialization of superconducting quantum chip wiring.
#             It includes library information maintenance, module information maintenance, and wiring-related operations.
#########################################################################

from routing import Control_off_chip
from routing import Flipchip
from routing import Flipchip_IBM

##############################################################################################################
# Operations related to wiring
##############################################################################################################
from base.branch_base import BranchBase
from addict import Dict
import copy, func_modules

def routing(**routing_ops):
    """
    The main wiring function.

    Input:
        routing_ops: A dictionary of wiring operation parameters.

    Output:
        Returns a deep copy of the wiring result.
    """
    rb = RoutingBranch(**routing_ops)
    return copy.deepcopy(rb.branch_process())

class RoutingBranch(BranchBase):
    def __init__(self, **branch_options):
        """
        Initialize the RoutingBranch class.

        Input:
            branch_options: A dictionary of wiring options.

        Exception:
            If gds_ops is not passed, a ValueError is thrown.
        """
        if "gds_ops" not in branch_options.keys():
            raise ValueError("RoutingBranch requires gds_ops to be passed!")

        if "method" not in branch_options.keys():
            self.method = "Control_off_chip_routing"
        else:
            self.method = branch_options["method"]
            del branch_options["method"]

        self.branch_options = Dict(branch_options)

        return

    def branch_process(self):
        """
        Process the wiring.

        Output:
            Returns a deep copy of the wiring result.
        """
        branch_options = copy.deepcopy(self.branch_options)
        hash_num = self.method

        # Error checking
        if not hasattr(self, hash_num):
            raise ValueError(f"No {hash_num} routing method available")

        result = getattr(self, hash_num)(branch_options)

        return copy.deepcopy(result)

    def Control_off_chip_routing(self, branch_options):
        """
        Control chip off-chip routing method.
        """
        coc = ControlOffChip(**branch_options)
        return copy.deepcopy(coc.branch_process())

    def Flipchip_routing_IBM(self, branch_options):
        """
        Flipchip_IBM routing method.
        """
        fci = FlipchipIBM(**branch_options)
        return copy.deepcopy(fci.branch_process())

    def Flipchip_routing(self, branch_options):
        """
        Flipchip routing method.
        """
        fcr = FlipchipRouting(**branch_options)
        return copy.deepcopy(fcr.branch_process())

class ControlOffChip(BranchBase):
    def gds_ops(self, branch_options):
        """
        Control chip off-chip routing operations.

        Input:
            branch_options: A dictionary of wiring options.

        Output:
            Returns the updated gds operation dictionary.
        """
        branch_options = copy.deepcopy(branch_options)
        gds_ops = copy.deepcopy(branch_options.gds_ops)
        # Interface
        qubits_ops = copy.deepcopy(gds_ops.qubits)
        rdls_ops = copy.deepcopy(gds_ops.readout_lines)
        chip_name = "chip0"
        chip_ops = gds_ops.chips[chip_name]
        pins_type = "LaunchPad"
        tmls_type = "TransmissionPath"
        # Input check
        if chip_ops == Dict():
            raise ValueError(f"No parameters found for chip {chip_name}!")
        # Perform operations
        pins_ops, tmls_ops = Control_off_chip.control_off_chip_routing(qubits_ops, rdls_ops, chip_ops, pins_type,
                                                                       tmls_type)
        gds_ops.pins = copy.deepcopy(pins_ops)
        gds_ops.transmission_lines = copy.deepcopy(tmls_ops)

        return copy.deepcopy(gds_ops)

    def chip_name__gds_ops(self, branch_options):
        """
        Perform control chip off-chip routing operations based on chip name.

        Input:
            branch_options: A dictionary of wiring options.

        Output:
            Returns the updated gds operation dictionary.
        """
        branch_options = copy.deepcopy(branch_options)
        gds_ops = copy.deepcopy(branch_options.gds_ops)
        # Interface
        qubits_ops = copy.deepcopy(gds_ops.qubits)
        rdls_ops = copy.deepcopy(gds_ops.readout_lines)
        chip_name = branch_options.chip_name
        chip_ops = gds_ops.chips[chip_name]
        pins_type = "LaunchPad"
        tmls_type = "TransmissionPath"
        # Input check
        if chip_ops == Dict():
            raise ValueError(f"No parameters found for chip {chip_name}!")
        # Perform operations
        pins_ops, tmls_ops = Control_off_chip.control_off_chip_routing(qubits_ops, rdls_ops, chip_ops, pins_type,
                                                                       tmls_type)
        gds_ops.pins = copy.deepcopy(pins_ops)
        gds_ops.transmission_lines = copy.deepcopy(tmls_ops)

        return copy.deepcopy(gds_ops)

class FlipchipIBM(BranchBase):
    def gds_ops(self, branch_options):
        """
        IBM Flipchip routing operations.

        Input:
            branch_options: A dictionary of wiring options.

        Output:
            Returns the updated gds operation dictionary.
        """
        branch_options = copy.deepcopy(branch_options)
        gds_ops = copy.deepcopy(branch_options.gds_ops)
        # Interface
        qubits_ops = copy.deepcopy(gds_ops.qubits)
        chip_ops = gds_ops.chips["chip0"]
        pins_type = "LaunchPad"
        ctls_type = "ChargeLine"
        # Input check
        if chip_ops == Dict():
            raise ValueError(f"No parameters found for chip {chip_name}!")
        # Generate
        pins_ops, ctls_ops = Flipchip_IBM.flipchiproutingibm(qubits_ops=qubits_ops,
                                                             chip_ops=chip_ops,
                                                             pins_type=pins_type,
                                                             ctls_type=ctls_type)

        gds_ops.pins = copy.deepcopy(pins_ops)
        gds_ops.control_lines = copy.deepcopy(ctls_ops)

        return copy.deepcopy(gds_ops)

    def chip_name__gds_ops(self, branch_options):
        """
        Perform IBM Flipchip routing operations based on chip name.

        Input:
            branch_options: A dictionary of wiring options.

        Output:
            Returns the updated gds operation dictionary.
        """
        branch_options = copy.deepcopy(branch_options)
        gds_ops = copy.deepcopy(branch_options.gds_ops)
        chip_name = copy.deepcopy(branch_options.chip_name)
        # Interface
        qubits_ops = copy.deepcopy(gds_ops.qubits)
        chip_ops = gds_ops.chips[chip_name]
        pins_type = "LaunchPad"
        ctls_type = "ChargeLine"
        # Input check
        if chip_ops == Dict():
            raise ValueError(f"No parameters found for chip {chip_name}!")
        # Generate
        pins_ops, ctls_ops = Flipchip_IBM.flipchiproutingibm(qubits_ops=qubits_ops,
                                                             chip_ops=chip_ops,
                                                             pins_type=pins_type,
                                                             ctls_type=ctls_type)

        gds_ops.pins = copy.deepcopy(pins_ops)
        gds_ops.control_lines = copy.deepcopy(ctls_ops)

        return copy.deepcopy(gds_ops)

    def chip_name__ctls_type__gds_ops(self, branch_options):
        """
        Perform IBM Flipchip routing operations based on chip name and control line type.

        Input:
            branch_options: A dictionary of wiring options.

        Output:
            Returns the updated gds operation dictionary.
        """
        branch_options = copy.deepcopy(branch_options)
        gds_ops = copy.deepcopy(branch_options.gds_ops)
        chip_name = branch_options.chip_name
        ctls_type = branch_options.ctls_type
        # Interface
        qubits_ops = copy.deepcopy(gds_ops.qubits)
        chip_ops = gds_ops.chips[chip_name]
        pins_type = "LaunchPad"
        ctls_type = ctls_type
        # Input check
        if chip_ops == Dict():
            raise ValueError(f"No parameters found for chip {chip_name}!")
        # Generate
        pins_ops, ctls_ops = Flipchip_IBM.flipchiproutingibm(qubits_ops=qubits_ops,
                                                             chip_ops=chip_ops,
                                                             pins_type=pins_type,
                                                             ctls_type=ctls_type)

        gds_ops.pins = copy.deepcopy(pins_ops)
        gds_ops.control_lines = copy.deepcopy(ctls_ops)

        return copy.deepcopy(gds_ops)

class FlipchipRouting(BranchBase):
    def gds_ops(self, branch_ops):
        """
        Perform Flipchip routing operations.

        Input:
            branch_ops: A dictionary of wiring operation parameters.

        Output:
            Returns the updated gds operation dictionary.
        """
        branch_ops = copy.deepcopy(branch_ops)
        gds_ops = copy.deepcopy(branch_ops.gds_ops)
        chip_name = "chip0"
        # Interface
        from library import pins
        qubits_ops = copy.deepcopy(gds_ops.qubits)
        rdls_ops = copy.deepcopy(gds_ops.readout_lines)
        chip_ops = copy.deepcopy(gds_ops.chips[chip_name])
        pins_type = "LaunchPad"
        tmls_type = "TransmissionPath"
        ctls_type = "ChargeLine"
        pins_geometric_ops = copy.deepcopy(getattr(pins, pins_type).default_options)
        # Input check
        if chip_ops == Dict():
            raise ValueError(f"Missing {chip_name}!")
        # Generate
        pins_ops, tmls_ops, ctls_ops, new_chip_ops = Flipchip.flipchip_routing(qubits_ops=qubits_ops,
                                                                               rdls_ops=rdls_ops,
                                                                               chip_ops=chip_ops,
                                                                               pins_type=pins_type,
                                                                               tmls_type=tmls_type,
                                                                               ctls_type=ctls_type,
                                                                               pins_geometric_ops=pins_geometric_ops)

        gds_ops.pins = copy.deepcopy(pins_ops)
        gds_ops.transmission_lines = copy.deepcopy(tmls_ops)
        gds_ops.control_lines = copy.deepcopy(ctls_ops)
        # gds_ops.chips[chip_name] = copy.deepcopy(new_chip_ops)

        return copy.deepcopy(gds_ops)

    def chip_name__gds_ops(self, branch_ops):
        """
        Perform Flipchip routing operations based on chip name.

        Input:
            branch_ops: A dictionary of wiring operation parameters.

        Output:
            Returns the updated gds operation dictionary.
        """
        branch_ops = copy.deepcopy(branch_ops)
        gds_ops = copy.deepcopy(branch_ops.gds_ops)
        chip_name = branch_ops.chip_name
        # Interface
        from library import pins
        qubits_ops = copy.deepcopy(gds_ops.qubits)
        rdls_ops = copy.deepcopy(gds_ops.readout_lines)
        chip_ops = copy.deepcopy(gds_ops.chips[chip_name])
        pins_type = "LaunchPad"
        tmls_type = "TransmissionPath"
        ctls_type = "ChargeLine"
        pins_geometric_ops = copy.deepcopy(getattr(pins, pins_type).default_options)
        # Input check
        if chip_ops == Dict():
            raise ValueError(f"Missing {chip_name}!")
        # Generate
        pins_ops, tmls_ops, ctls_ops, new_chip_ops = Flipchip.flipchip_routing(qubits_ops=qubits_ops,
                                                                               rdls_ops=rdls_ops,
                                                                               chip_ops=chip_ops,
                                                                               pins_type=pins_type,
                                                                               tmls_type=tmls_type,
                                                                               ctls_type=ctls_type,
                                                                               pins_geometric_ops=pins_geometric_ops)

        gds_ops.pins = copy.deepcopy(pins_ops)
        gds_ops.transmission_lines = copy.deepcopy(tmls_ops)
        gds_ops.control_lines = copy.deepcopy(ctls_ops)
        gds_ops.chips[chip_name] = copy.deepcopy(new_chip_ops)

        return copy.deepcopy(gds_ops)

    def chip_name__ctls_type__gds_ops__pins_type__tmls_type(self, branch_ops):
        """
        Perform Flipchip routing operations based on chip name, control line type, pin type, and transmission line type.

        Input:
            branch_ops: A dictionary of wiring operation parameters.

        Output:
            Returns the updated gds operation dictionary.
        """
        branch_ops = copy.deepcopy(branch_ops)
        gds_ops = copy.deepcopy(branch_ops.gds_ops)
        chip_name = branch_ops.chip_name
        # Interface
        qubits_ops = copy.deepcopy(gds_ops.qubits)
        rdls_ops = copy.deepcopy(gds_ops.readout_lines)
        chip_ops = copy.deepcopy(gds_ops.chips[chip_name])
        pins_type = branch_ops.pins_type
        tmls_type = branch_ops.tmls_type
        ctls_type = branch_ops.ctls_type
        pins_geometric_ops = copy.deepcopy(branch_ops.pins_geometric_ops)
        # Input check
        if chip_ops == Dict():
            raise ValueError(f"Missing {chip_name}!")
        # Generate
        pins_ops, tmls_ops, ctls_ops, new_chip_ops = Flipchip.flipchip_routing(qubits_ops=qubits_ops,
                                                                               rdls_ops=rdls_ops,
                                                                               chip_ops=chip_ops,
                                                                               pins_type=pins_type,
                                                                               tmls_type=tmls_type,
                                                                               ctls_type=ctls_type,
                                                                               pins_geometric_ops=pins_geometric_ops)

        gds_ops.pins = copy.deepcopy(pins_ops)
        gds_ops.transmission_lines = copy.deepcopy(tmls_ops)
        gds_ops.control_lines = copy.deepcopy(ctls_ops)
        # gds_ops.chips[chip_name] = copy.deepcopy(new_chip_ops)

        return copy.deepcopy(gds_ops)

class zhuanxiang156(BranchBase):
    def __init__(self, **branch_options):
        """
        Initialize the zhuanxiang156 class.

        Input:
            branch_options: A dictionary of branching options.
        """
        super().__init__(**branch_options)

def new_routing_method(gds_ops):
    ################################ 
    # update gds options (your code)
    ################################
    return gds_ops