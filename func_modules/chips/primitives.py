############################################################################################
# Parameter processing related to chips
############################################################################################

from addict import Dict
import toolbox
import copy
from library import chips as chips_lib

def qubits_to_size(qubits, origin_chips, dist: float = 4000):
    """
    Adjust the chip size based on qubits information.

    Input:
        qubits: qubits parameters
        origin_chips: original chip parameters
    
    Output:
        chips: chip parameters after size adjustment
    """
    # Interface
    qubits = copy.deepcopy(qubits)
    origin_chips = copy.deepcopy(origin_chips)

    # Adjust size
    x_list = []
    y_list = []
    chips = copy.deepcopy(origin_chips)
    for qubit_name, qubit_options in qubits.items():
        x_list.append(qubit_options.gds_pos[0])
        y_list.append(qubit_options.gds_pos[1])
    xmin = min(x_list)
    ymin = min(y_list)
    xmax = max(x_list)
    ymax = max(y_list)
    start_pos = [xmin - dist, ymin - dist]
    end_pos = [xmax + dist, ymax + dist]
    # Adjust all chips
    for chip_name, chip_options in chips.items():
        chips[chip_name].start_pos = start_pos
        chips[chip_name].end_pos = end_pos

    return copy.deepcopy(chips)

def qubits_add_chips(qubits, chips):
    """
    Supplement missing chips based on qubits information.

    Input:
        qubits: qubits parameters
        chips: chips parameters

    Output:
        chips: chips parameters after supplementation
    """
    # Interface
    qubits = copy.deepcopy(qubits)
    chips = copy.deepcopy(chips)

    # Check and add in sequence
    for q_name, q_op in qubits.items():
        if q_op.chip not in chips.keys():
            chips[q_op.chip].name = q_op.chip
            chips[q_op.chip].start_pos = [0, 0]

    return copy.deepcopy(chips)

def tmls_add_chips(tmls, chips):
    """
    Supplement missing chips based on tmls information.

    Input:
        tmls: tmls parameters
        chips: chips parameters

    Output:
        chips: chips parameters after supplementation
    """
    # Interface
    tmls = copy.deepcopy(tmls)
    chips = copy.deepcopy(chips)

    # Check and add in sequence
    for q_name, q_op in tmls.items():
        if q_op.chip not in chips.keys():
            chips[q_op.chip].start_pos = [0, 0]

    return copy.deepcopy(chips)

def pins_add_chips(pins, chips):
    """
    Supplement missing chips based on pins information.

    Input:
        pins: pins parameters
        chips: chips parameters

    Output:
        chips: chips parameters after supplementation
    """
    # Interface
    pins = copy.deepcopy(pins)
    chips = copy.deepcopy(chips)

    # Check and add in sequence
    for pin_name, pin_op in pins.items():
        if pin_op.chip not in chips.keys():
            chips[pin_op.chip].start_pos = [0, 0]

    return copy.deepcopy(chips)

def cpls_add_chips(cpls, chips):
    """
    Supplement missing chips based on cpls information.

    Input:
        cpls: cpls parameters
        chips: chips parameters

    Output:
        chips: chips parameters after supplementation
    """
    # Interface
    cpls = copy.deepcopy(cpls)
    chips = copy.deepcopy(chips)

    # Check and add in sequence
    for cpl_name, cpl_op in cpls.items():
        if cpl_op.chip not in chips.keys():
            chips[cpl_op.chip].start_pos = [0, 0]

    return copy.deepcopy(chips)

def ctls_add_chips(ctls, chips):
    """
    Supplement missing chips based on ctls information.

    Input:
        ctls: ctls parameters
        chips: chips parameters

    Output:
        chips: chips parameters after supplementation
    """
    # Interface
    ctls = copy.deepcopy(ctls)
    chips = copy.deepcopy(chips)

    # Check and add in sequence
    for ctl_name, ctl_op in ctls.items():
        if ctl_op.chip not in chips.keys():
            chips[ctl_op.chip].start_pos = [0, 0]

    return copy.deepcopy(chips)

def copy_start_and_end(chips, chip_name):
    """
    Modify the start and end points of all chips based on one chip.

    Input:
        chips: chips parameters
        chip_name: the name of the chip to copy from
    """
    # Interface
    chips = Dict(chips)

    # Copy in sequence
    for c_name, c_ops in chips.items():
        chips[c_name].start_pos = copy.deepcopy(chips[chip_name].start_pos)
        chips[c_name].end_pos = copy.deepcopy(chips[chip_name].end_pos)

    return copy.deepcopy(chips)

def set_name(chips, origin_name, new_name):
    """
    Modify the name of a chip.

    Input:
        origin_name: original name
        new_name: new name

    Output:
        chips: chips parameters after renaming a chip
    """
    # Interface
    chips = copy.deepcopy(chips)

    # Rename
    chip_ops  = chips[origin_name]
    chips.pop(origin_name)
    chip_ops.name = new_name
    chips[new_name] = chip_ops

    return copy.deepcopy(chips)

def copy_chip(chips, chip_name, origin_chip_name: str = None):
    """
    Add a new chip based on a template chip.

    Input:
        chips: chips parameters
        chip_name: the name of the chip to add
        origin_chip_name: the name of the template chip; if empty, create a chip with default parameters

    Output:
        chips: chips parameters after adding a chip
    """
    # Interface
    chips = copy.deepcopy(chips)

    if origin_chip_name is not None:
        if chips[origin_chip_name] == Dict():
            raise ValueError("Does not exist {}, cannot create {}".format(origin_chip_name, chip_name))
        chips[chip_name] = copy.deepcopy(chips[origin_chip_name])
        chips[chip_name].name = chip_name
    if origin_chip_name is None:
        chips[chip_name].name = chip_name
        chips[chip_name].start_pos = [0, 0]
        chips[chip_name].end_pos = [500, 500]
        
    return copy.deepcopy(chips)

def get_max_width(chips):
    """
    Obtain the maximum chip width.

    Input:
        chips: chip parameters

    Output:
        max_width: maximum width
    """
    # Interface
    chips = copy.deepcopy(chips)

    # Input check
    if chips == Dict():
        return None
    
    # Get maximum width
    max_width = 0
    for chip_name, chip_ops in chips.items():
        width = abs(chip_ops.end_pos[0] - chip_ops.start_pos[0])
        max_width = max(max_width, width)
    
    return max_width