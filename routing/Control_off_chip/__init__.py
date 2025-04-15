#########################################################################
# File Name: __init__.py
# Description: Initialization module for simulating control lines and transmission lines of superconducting quantum chips.
#             Includes functions for copying qubit operation parameters, generating pins, and generating transmission lines.
#########################################################################

# Import necessary toolbox modules and other dependencies
import toolbox
import os, copy, func_modules
from addict import Dict
from routing.Control_off_chip import transmission_lines
from routing.Control_off_chip import pins

from routing.Control_off_chip import pins
from routing.Control_off_chip import transmission_lines

def control_off_chip_routing(qubits_ops, rdls_ops, chip_ops, pins_type, tmls_type):
    """
    Main function for simulating control and transmission line routing.

    Inputs:
        qubits_ops: Dictionary describing the operation parameters of qubits.
        rdls_ops: Dictionary describing the operation parameters of resistors.
        chip_ops: Dictionary describing the operation parameters of the chip.
        pins_type: String specifying the type of pins.
        tmls_type: String specifying the type of transmission lines.

    Outputs:
        pins_ops: Dictionary of generated pin operation parameters.
        tmls_ops: Dictionary of generated transmission line operation parameters.
    """
    # Deep copy qubit operation parameters, resistor operation parameters, and chip operation parameters
    qubits_ops = copy.deepcopy(qubits_ops)
    rdls_ops = copy.deepcopy(rdls_ops)
    chip_ops = copy.deepcopy(chip_ops)
    pins_type = pins_type
    tmls_type = tmls_type
    # Perform pin and transmission line generation operations
    pins_ops = generate_pins(qubits_ops, chip_ops, pins_type)
    tmls_ops = generate_tmls(qubits_ops, rdls_ops, pins_ops, tmls_type, chip_name=chip_ops.name)
    return copy.deepcopy(pins_ops), copy.deepcopy(tmls_ops)


def generate_pins(qubits_ops, chip_ops, pins_type):
    """
    Function to generate pin operation parameters.

    Inputs:
        qubits_ops: Dictionary describing the operation parameters of qubits.
        chip_ops: Dictionary describing the operation parameters of the chip.
        pins_type: String specifying the type of pins.

    Outputs:
        pins_ops: Dictionary of generated pin operation parameters.
    """
    qubits_ops = copy.deepcopy(qubits_ops)
    chip_ops = copy.deepcopy(chip_ops)

    pins_ops = pins.generate_pins(qubits_ops=qubits_ops,
                                  chip_ops=chip_ops,
                                  pins_type=pins_type)

    return copy.deepcopy(pins_ops)


def generate_tmls(qubits_ops, rdls_ops, pins_ops, tmls_type, chip_name):
    """
    Function to generate transmission line operation parameters.

    Inputs:
        qubits_ops: Dictionary describing the operation parameters of qubits.
        rdls_ops: Dictionary describing the operation parameters of resistors.
        pins_ops: Dictionary of generated pin operation parameters.
        tmls_type: String specifying the type of transmission lines.
        chip_name: String specifying the name of the chip.

    Outputs:
        tmls_ops: Dictionary of generated transmission line operation parameters.
    """
    tmls_ops = transmission_lines.generate_tmls(qubits_ops=qubits_ops,
                                                rdls_ops=rdls_ops,
                                                pins_ops=pins_ops,
                                                tmls_type=tmls_type,
                                                chip_name=chip_name)
    return copy.deepcopy(tmls_ops)