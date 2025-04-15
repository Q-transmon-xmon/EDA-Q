############################################################################################
# Transmission line related parameter processing
############################################################################################

from addict import Dict
import toolbox
import copy
from library import transmission_lines

def soak(transmission_lines):
    """Complete the transmission line parameters based on the class.

    Input:
        transmission_lines: transmission line parameters
    
    Output:
        transmission_lines: completed transmission line parameters
    """

    # Interface
    transmission_lines = copy.deepcopy(transmission_lines)

    # Obtain the TransmissionLines instance
    tmls = transmission_lines.TransmissionLines(transmission_lines)

    # Update parameters in sequence
    for tml_name, tml_options in transmission_lines.items():
        tml_inst = getattr(tmls, tml_name)
        transmission_lines[tml_name] = tml_inst.options

    return copy.deepcopy(transmission_lines)

# def Control_off_chip_transmission_lines(topo_poss, qubits, readout_lines, pins, chip):
#     """Generate transmission lines using the Control_off_chip strategy.

#     Input:
#         topo_poss: topological positions
#         qubits: qubits parameters (processed by dehy)
#         readout_lines: readout line parameters
#         pins: pins parameters
#         chip: the chip where the transmission lines are generated

#     Output:
#         transmission_lines: generated transmission line parameters    
#     """

#     # Interface
#     topo_poss = copy.deepcopy(topo_poss)
#     qubits = copy.deepcopy(qubits)
#     readout_lines = copy.deepcopy(readout_lines)
#     pins = copy.deepcopy(pins)
#     chip = copy.deepcopy(chip)

#     # Generate transmission lines
#     transmission_lines = Control_off_chip_routing.generate_transmission_lines(topo_poss, qubits, readout_lines, pins)
    
#     # Set the chip layer for the transmission lines
#     transmission_lines = set_chips(transmission_lines, chip.name)

#     # Output inspection
#     # tmls = TransmissionLines(transmission_lines)
#     # try:
#     #     tmls.show_gds()
#     # except:
#     #     raise ValueError("Unable to successfully generate the GDS layout!")

#     return copy.deepcopy(transmission_lines)

# def Flipchip_routing(topo_poss, qubits, readout_lines, pins, chip):
#     """Generate transmission lines using the Flipchip_routing strategy.

#     Input:
#         topo_poss: topological positions
#         qubits: qubits parameters (processed by dehy)
#         readout_lines: readout line parameters
#         pins: pins parameters
#         chip: the chip where the transmission lines are generated

#     Output:
#         transmission_lines: generated transmission line parameters    
#     """

#     # Interface
#     topo_poss = copy.deepcopy(topo_poss)
#     qubits = copy.deepcopy(qubits)
#     readout_lines = copy.deepcopy(readout_lines)
#     pins = copy.deepcopy(pins)
#     chip = copy.deepcopy(chip)

#     # Generate transmission lines
#     transmission_lines = Control_off_chip_routing.generate_transmission_lines(topo_poss, 
#                                                                               qubits, 
#                                                                               readout_lines, 
#                                                                               pins, 
#                                                                               chip)
    
#     # Set the chip layer for the transmission lines
#     transmission_lines = set_chips(transmission_lines, chip.name)

#     # Output inspection
#     # tmls = TransmissionLines(transmission_lines)
#     # try:
#     #     tmls.show_gds()
#     # except:
#     #     raise ValueError("Unable to successfully generate the GDS layout!")

#     return copy.deepcopy(transmission_lines)


def set_chips(tmls_ops, chip_name):
    """Set the chip layer information for the transmission lines.

    Input:
        tmls_ops: transmission line parameters
        chip_name: the name of the chip where the transmission lines are located
    
    Output:
        tmls_ops: transmission line parameters with chip information set
    """

    # Interface
    tmls_ops = copy.deepcopy(tmls_ops)

    # Set the chip information in sequence
    for k, v in tmls_ops.items():
        tmls_ops[k].chip = chip_name
        
    return copy.deepcopy(tmls_ops)
