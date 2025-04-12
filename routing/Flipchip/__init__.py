#########################################################################
# File Name: __init__.py
# Description: Initialization module for superconducting quantum chip routing.
#              Includes functionality for generating control lines, pins, and transmission lines.
#########################################################################

# Import necessary routing modules
from routing.Flipchip import control_lines
from routing.Flipchip import pins
from routing.Flipchip import transmission_lines
from routing.Flipchip import calc_chip_size
import copy
import toolbox
import func_modules
from addict import Dict


def flipchip_routing(qubits_ops, rdls_ops, chip_ops, pins_type, tmls_type, ctls_type, pins_geometric_ops):
    """
    Main function for quantum chip routing.

    Args:
        qubits_ops: Dictionary describing qubit operation parameters.
        rdls_ops: Dictionary describing readout line operation parameters.
        chip_ops: Dictionary describing chip operation parameters.
        pins_type: String specifying the type of pins.
        tmls_type: String specifying the type of transmission lines.
        ctls_type: String specifying the type of control lines.
        pins_geometric_ops: Dictionary describing geometric operation parameters for pins.

    Returns:
        pins_ops: Dictionary containing pin operation parameters.
        tmls_ops: Dictionary containing transmission line operation parameters.
        ctls_ops: Dictionary containing control line operation parameters.
        new_chip_ops: Dictionary containing updated chip operation parameters.
    """
    # Generate pin operation parameters and update chip operation parameters
    pins_ops, new_chip_ops = generate_pins(qubits_ops=qubits_ops,
                                           rdls_ops=rdls_ops,
                                           chip_ops=chip_ops,
                                           pins_type=pins_type,
                                           pins_geometric_ops=pins_geometric_ops)
    # Generate transmission line operation parameters
    tmls_ops = generate_transmission_lines(qubits_ops=qubits_ops,
                                           rdls_ops=rdls_ops,
                                           chip_ops=new_chip_ops,
                                           pins_ops=pins_ops,
                                           tmls_type=tmls_type)
    # Generate control line operation parameters
    ctls_ops = generate_control_lines(qubits_ops=qubits_ops,
                                      rdls_ops=rdls_ops,
                                      chip_ops=new_chip_ops,
                                      pins_ops=pins_ops,
                                      ctls_type=ctls_type)
    return copy.deepcopy(pins_ops), copy.deepcopy(tmls_ops), copy.deepcopy(ctls_ops), copy.deepcopy(new_chip_ops)


def calculate_chip_size(qubits_ops, rdls_ops, pins_geometric_ops):
    """
    Function to calculate the chip size.

    Args:
        qubits_ops: Dictionary describing qubit operation parameters.
        rdls_ops: Dictionary describing readout line operation parameters.
        pins_geometric_ops: Dictionary describing geometric operation parameters for pins.

    Returns:
        start_pos: Tuple representing the starting position of the chip.
        end_pos: Tuple representing the ending position of the chip.
    """
    start_pos, end_pos = calc_chip_size.calc_chip_size(qubits_ops, rdls_ops, pins_geometric_ops)
    return copy.deepcopy(start_pos), copy.deepcopy(end_pos)


def generate_pins(qubits_ops, rdls_ops, chip_ops, pins_type, pins_geometric_ops):
    """
    Function to generate pin operation parameters.

    Args:
        qubits_ops: Dictionary describing qubit operation parameters.
        rdls_ops: Dictionary describing readout line operation parameters.
        chip_ops: Dictionary describing chip operation parameters.
        pins_type: String specifying the type of pins.
        pins_geometric_ops: Dictionary describing geometric operation parameters for pins.

    Returns:
        pins_ops: Dictionary containing pin operation parameters.
        chip_ops: Dictionary containing updated chip operation parameters.
    """
    qubits_ops = copy.deepcopy(qubits_ops)
    rdls_ops = copy.deepcopy(rdls_ops)
    chip_ops = copy.deepcopy(chip_ops)
    pins_geometric_ops = copy.deepcopy(pins_geometric_ops)

    qubits_ops = convert_qubits_ops_format(qubits_ops, rdls_ops)

    pins_ops, chip_ops = pins.generate_pins(qubits=qubits_ops,
                                            readout_lines=rdls_ops,
                                            chip=chip_ops,
                                            pins_geometric_ops=pins_geometric_ops)
    pins_ops = func_modules.pins.set_types(pins_ops, pins_type=pins_type)
    pins_ops = func_modules.pins.set_chips(pins_ops, chip_name=chip_ops.name)
    return copy.deepcopy(pins_ops), copy.deepcopy(chip_ops)


def generate_control_lines(qubits_ops, rdls_ops, pins_ops, chip_ops, ctls_type):
    """
    Function to generate control line operation parameters.

    Args:
        qubits_ops: Dictionary describing qubit operation parameters.
        rdls_ops: Dictionary describing readout line operation parameters.
        pins_ops: Dictionary containing pin operation parameters.
        chip_ops: Dictionary describing chip operation parameters.
        ctls_type: String specifying the type of control lines.

    Returns:
        ctls_ops: Dictionary containing control line operation parameters.
    """
    qubits_ops = copy.deepcopy(qubits_ops)
    rdls_ops = copy.deepcopy(rdls_ops)
    pins_ops = copy.deepcopy(pins_ops)
    chip_ops = copy.deepcopy(chip_ops)

    qubits_ops = convert_qubits_ops_format(qubits_ops, rdls_ops)

    ctls_ops = control_lines.generate_control_lines(qubits=qubits_ops,
                                                    readout_lines=rdls_ops,
                                                    pins=pins_ops,
                                                    chip=chip_ops)
    ctls_ops = func_modules.ctls.set_types(ctls_ops=ctls_ops, ctls_type=ctls_type)
    ctls_ops = func_modules.ctls.set_chips(ctls_ops=ctls_ops, chip_name=chip_ops.name)
    return copy.deepcopy(ctls_ops)


def generate_transmission_lines(qubits_ops, rdls_ops, chip_ops, pins_ops, tmls_type):
    """
    Function to generate transmission line operation parameters.

    Args:
        qubits_ops: Dictionary describing qubit operation parameters.
        rdls_ops: Dictionary describing readout line operation parameters.
        chip_ops: Dictionary describing chip operation parameters.
        pins_ops: Dictionary containing pin operation parameters.
        tmls_type: String specifying the type of transmission lines.

    Returns:
        tmls_ops: Dictionary containing transmission line operation parameters.
    """
    qubits_ops = copy.deepcopy(qubits_ops)
    rdls_ops = copy.deepcopy(rdls_ops)
    chip_ops = copy.deepcopy(chip_ops)
    pins_ops = copy.deepcopy(pins_ops)

    qubits_ops = convert_qubits_ops_format(qubits_ops, rdls_ops)

    tmls_ops = transmission_lines.generate_transmission_lines(qubits=qubits_ops,
                                                              readout_lines=rdls_ops,
                                                              pins=pins_ops,
                                                              chip=chip_ops)
    tmls_ops = func_modules.tmls.set_types(tmls_ops=tmls_ops, tmls_type=tmls_type)
    tmls_ops = func_modules.tmls.set_chips(tmls_ops=tmls_ops, chip_name=chip_ops.name)
    return copy.deepcopy(tmls_ops)


def convert_qubits_ops_format(qubits_ops, rdls_ops):
    """
    Function to convert qubit operation parameter format.

    Args:
        qubits_ops: Dictionary describing qubit operation parameters.
        rdls_ops: Dictionary describing readout line operation parameters.

    Returns:
        qubits_ops: Dictionary containing converted qubit operation parameters.
    """
    qubits_ops = copy.deepcopy(qubits_ops)
    for q_name, q_ops in qubits_ops.items():
        coupling_pins = Dict()
        coupling_pins.top = toolbox.find_topmost_coordinate(list(q_ops.control_pins))
        coupling_pins.bot = toolbox.find_botmost_coordinate(list(q_ops.control_pins))
        coupling_pins.left = toolbox.find_botmost_coordinate(list(q_ops.control_pins))
        coupling_pins.right = toolbox.find_rightmost_coordinate(list(q_ops.control_pins))
        control_pins = [q_ops.control_pins[0]]

        readout_line = func_modules.rdls.find_rdl_name(rdls_ops, q_ops)

        coupling_qubits = Dict()
        coupling_qubits.top = None
        coupling_qubits.bot = None
        coupling_qubits.left = None
        coupling_qubits.right = None

        q_ops.coupling_pins = copy.deepcopy(coupling_pins)
        q_ops.control_pins = copy.deepcopy(control_pins)
        q_ops.readout_line = copy.deepcopy(readout_line)
        q_ops.coupling_qubits = copy.deepcopy(coupling_qubits)
        qubits_ops[q_name] = copy.deepcopy(q_ops)

    return copy.deepcopy(qubits_ops)