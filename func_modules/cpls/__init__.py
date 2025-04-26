import os
import copy
import toolbox

from func_modules.cpls import gene_cpls_ops
from func_modules.cpls import primitives

############################################################################################
# Parameter processing related to coupling lines
############################################################################################
from func_modules.cpls import primitives
from addict import Dict

def generate_coupling_lines(**gene_ops):
    """Generate coupling lines based on topology information and qubits' given cp_pins.

    Input:
        qubits: Qubit parameters.
        topology: Topology information.
        cp_type: Type of coupling to generate.
        chip: Chip layer to generate the coupling on.

    Output:
        cpls_ops: Coupling line parameters.
    """
    return copy.deepcopy(gene_cpls_ops.gene_cpls_ops(**gene_ops))

def soak_cpls(cpl_ops):
    """Supplement parameters with default values.

    Input:
        cpl_ops: Coupling line parameters to be completed.

    Output:
        cpl_ops: Completed coupling line parameters.
    """
    cpl_ops = primitives.soak_cpls(coupling_lines=cpl_ops)
    return copy.deepcopy(cpl_ops)

def set_chips(cpls_ops, chip_name: str = None):
    """Set chip information for coupling lines.

    Input:
        cpls_ops: Coupling line parameters.
        chip_name: The chip name to be set.

    Output:
        cpls_ops: Coupling line parameters with the updated chip name.
    """
    cpls_ops = primitives.set_chips(cpls_ops=cpls_ops, chip_name=chip_name)
    return copy.deepcopy(cpls_ops)

def set_types(cpls_ops, type):
    """Set the type of coupling line.

    Input:
        cpls: Coupling line parameters.
        type: Target type to set.

    Output:
        cpls: Coupling line parameters with the updated type.
    """
    cpls_ops = primitives.set_types(cpls=cpls_ops, type=type)
    return copy.deepcopy(cpls_ops)

def add_cpl(q0_ops: str = None,
            q0_pin_num: int = 0,
            q1_ops: str = None,
            q1_pin_num: int = 0,
            cp_type: str = "CouplingLineStraight", 
            chip: str = "chip0", 
            geometric_ops: Dict = Dict()):
    """Add a coupling line between two qubits.

    Input:
        q0_ops: Name of the first qubit.
        q0_pin_num: Pin number of the first qubit.
        q1_ops: Name of the second qubit.
        q1_pin_num: Pin number of the second qubit.
        cp_type: Type of coupling line (default: "CouplingLineStraight").
        chip: Chip layer for the coupling line (default: "chip0").
        geometric_ops: Geometric parameters for the coupling line.

    Output:
        cpl_ops: Coupling line parameters for the newly added coupling.
    """
    cpl_ops = primitives.add_cpl(q0_ops=q0_ops,
                                 q0_pin_num=q0_pin_num,
                                 q1_ops=q1_ops,
                                 q1_pin_num=q1_pin_num,
                                 cp_type=cp_type,
                                 chip=chip,
                                 geometric_ops=geometric_ops)
    return copy.deepcopy(cpl_ops)
