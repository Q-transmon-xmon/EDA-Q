import os
import copy
import toolbox

from func_modules.ctls import gene_ctls_ops
from func_modules.ctls import primitives

############################################################################################
# Modify the parameters of the control line
############################################################################################

from addict import Dict
import toolbox
import copy
from library import control_lines as ctls_lib

def set_types(ctls_ops, ctls_type):
    """Modify control line type

    input：
        ctls: Control line parameters
        type: The type of control line to be modified
    
    output:
        ctls: Modify control line type后的参数
    """

    # interface
    ctls_ops = copy.deepcopy(ctls_ops)

    # Modify control line types one by one
    for k, v in ctls_ops.items():
        ctls_ops[k].type = ctls_type
    
    return copy.deepcopy(ctls_ops)

def set_chips(ctls_ops, chip_name: str = None):
    """Set the chip information for each control line

    input：
        ctls_ops: Parameters of control lines
        chip_name: Name of the chip where the control line is located
    
    output：
        ctls_ops: Control line parameters after setting chip information
    """

    # interface
    ctls_ops = Dict(ctls_ops)
    
    # Set chip information one by one
    for ctl_name, ctl_ops in ctls_ops.items():
        ctls_ops[ctl_name].chip = chip_name

    return copy.deepcopy(ctls_ops)

def soak_ctls(ctls_ops):
    copy.deepcopy(ctls_ops)
    for ctl_name, ctl_ops in ctls_ops.items():
        ctl_inst = getattr(ctls_lib, ctl_ops.type)(options=ctl_ops)
        ctls_ops[ctl_name] = copy.deepcopy(ctl_inst.options)
    return copy.deepcopy(ctls_ops)

def generate_control_lines(**gene_ops):
    return copy.deepcopy(gene_ctls_ops.gene_ctls_ops(**gene_ops))

def find_ctl_name(ctls_ops, qubit_ops):
    ctls_ops = copy.deepcopy(ctls_ops)
    qubit_ops = copy.deepcopy(qubit_ops)
 
    result = None

    for ctl_name, ctl_ops in ctls_ops.items():
        if ctl_ops.start_pos in qubit_ops.control_pins:
            result = ctl_name
            break
    if result is None:
        raise ValueError("找不到{}对应的控制线！".format(qubit_ops.name))
    return result