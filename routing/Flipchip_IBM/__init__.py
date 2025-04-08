#########################################################################
# File Name: __init__.py
# Description: Initializes the Flip Chip IBM routing process module.
#              Includes functionality for dynamically importing modules and executing the routing process.
#########################################################################

import toolbox
import os, copy
from addict import Dict

from routing.Flipchip_IBM import control_lines
from routing.Flipchip_IBM import pins

def flipchiproutingibm(qubits_ops, chip_ops, pins_type, ctls_type):
    """
    Main function to execute the Flip Chip IBM routing process.

    Args:
        qubits_ops: Dictionary describing the operation parameters of qubits.
        chip_ops: Dictionary describing the operation parameters of the chip.
        pins_type: String specifying the type of pins.
        ctls_type: String specifying the type of control lines.

    Returns:
        pins_ops: Dictionary containing the operation parameters of the pins.
        ctls_ops: Dictionary containing the operation parameters of the control lines.
    """
    # Deep copy input parameters to avoid modifying the original data
    qubits_ops = copy.deepcopy(qubits_ops)
    chip_ops = copy.deepcopy(chip_ops)

    # Generate pin operation parameters
    pins_ops = generate_pins(qubits_ops, chip_ops, pins_type)

    # Generate control line operation parameters
    ctls_ops = generate_ctls(qubits_ops, pins_ops, chip_ops.name, ctls_type)

    # Return deep copies of the pin and control line operation parameters
    return copy.deepcopy(pins_ops), copy.deepcopy(ctls_ops)


def generate_pins(qubits_ops, chip_ops, pins_type):
    """
    Main function to generate pins.

    Args:
        qubits_ops: Dictionary describing the operation parameters of qubits.
        chip_ops: Dictionary describing the operation parameters of the chip.
        pins_type: String specifying the type of pins.

    Returns:
        pins_ops: Dictionary containing the operation parameters of the pins.
    """
    pins_ops = pins.generate_pins(qubits_ops=qubits_ops,
                                  chip_ops=chip_ops,
                                  pins_type=pins_type)
    return copy.deepcopy(pins_ops)


def generate_ctls(qubits_ops, pins_ops, chip_name, ctls_type):
    """
    Main function to generate control lines.

    Args:
        qubits_ops: Dictionary describing the operation parameters of qubits.
        pins_ops: Dictionary containing the operation parameters of the pins.
        chip_name: String specifying the name of the chip.
        ctls_type: String specifying the type of control lines.

    Returns:
        ctls_ops: Dictionary containing the operation parameters of the control lines.
    """
    ctls_ops = control_lines.generate_ctls(qubits_ops=qubits_ops,
                                           pins_ops=pins_ops,
                                           chip_name=chip_name,
                                           ctls_type=ctls_type)
    return copy.deepcopy(ctls_ops)