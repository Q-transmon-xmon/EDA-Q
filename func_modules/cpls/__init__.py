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
    """Based on topology information andqubitsgivencp_pinsGenerate coupling lines
    
    input：
        qubits: qubitsparameter
        topology: Topology information
        cp_type: Generated coupling types
        chip: Generate coupled layers
    output： 
        cpls_ops: coupling lines' parameters.
    """
    return copy.deepcopy(gene_cpls_ops.gene_cpls_ops(**gene_ops))

def soak_cpls(cpl_ops):
    """Supplement parameters with classes

    input：
        cpl_ops: Coupling line parameters to be completed

    output：
        cpl_ops: Completed coupling line parameters
    """
    cpl_ops = primitives.soak_cpls(coupling_lines=cpl_ops)
    return copy.deepcopy(cpl_ops)

def set_chips(cpls_ops, chip_name: str = None):
    """Set chip information for coupling lines

    input：
        cpls_ops: Coupling line parameters
        chip_name: The chip name to be set

    output： 
        cpls_ops: Set the Coupling line parameters after the chip name.
    """
    cpls_ops = primitives.set_chips(cpls_ops=cpls_ops, chip_name=chip_name)
    return copy.deepcopy(cpls_ops)

def set_types(cpls_ops, type):
    """Set the type of coupling line

    input： 
        cpls: Coupling line parameters
        type: target type

    output：
        cpls: Coupling parameters after modifying the type
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
    cpl_ops = primitives.add_cpl(q0_ops=q0_ops,
                                 q0_pin_num=q0_pin_num,
                                 q1_ops=q1_ops,
                                 q1_pin_num=q1_pin_num,
                                 cp_type=cp_type,
                                 chip=chip,
                                 geometric_ops=geometric_ops)
    return copy.deepcopy(cpl_ops)