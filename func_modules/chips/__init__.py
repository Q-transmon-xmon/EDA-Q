import os, copy
import toolbox

from func_modules.chips import gene_chip_ops
from func_modules.chips import gene_chips_ops
from func_modules.chips import primitives

#####################################################################################################
# functional module 
#####################################################################################################
from addict import Dict
from library import chips as chips_lib

def qubits_to_size(qubits_ops, chips_ops, dist: float = 4000):
    new_chips_ops = primitives.qubits_to_size(qubtis=qubits_ops,
                                      origin_chips=chips_ops,
                                      dist=dist)
    return copy.deepcopy(new_chips_ops)

def qubits_add_chips(qubits_ops, chips_ops):
    new_chips_ops = primitives.qubits_add_chips(qubits=qubits_ops,
                                                chips=chips_ops)
    return copy.deepcopy(new_chips_ops)

def tmls_add_chips(tmls_ops, chips_ops):
    new_chips_ops = primitives.qubits_add_chips(tmls=tmls_ops,
                                                chips=chips_ops)
    return copy.deepcopy(new_chips_ops)

def pins_add_chips(pins_ops, chips_ops):
    new_chips_ops = primitives.qubits_add_chips(pins=pins_ops,
                                                chips=chips_ops)
    return copy.deepcopy(new_chips_ops)

def cpls_add_chips(cpls_ops, chips_ops):
    new_chips_ops = primitives.qubits_add_chips(cpls=cpls_ops,
                                                chips=chips_ops)
    return copy.deepcopy(new_chips_ops)

def ctls_add_chips(ctls_ops, chips_ops):
    new_chips_ops = primitives.qubits_add_chips(ctls=ctls_ops,
                                                chips=chips_ops)
    return copy.deepcopy(new_chips_ops)

def copy_start_and_end(chips_ops, chip_name):
    new_chips_ops = primitives.copy_start_and_end(chips=chips_ops,
                                                  chip_name=chip_name)
    return copy.deepcopy(new_chips_ops)

def set_name(chips_ops, origin_name, new_name):
    new_chips_ops = primitives.set_name(chips=chips_ops, origin_name=origin_name, new_name=new_name)
    return copy.deepcopy(new_chips_ops)

def copy_chip(old_chip_ops, new_chip_name):
    new_chip_ops = copy.deepcopy(old_chip_ops)
    new_chip_ops.name = new_chip_name
    return copy.deepcopy(new_chip_ops)

def get_max_width(chips_ops):
    max_width = primitives.get_max_width(chips=chips_ops)
    return max_width

def soak_chip(chip_ops):
    chip_inst = getattr(chips_lib, chip_ops.type)(options=chip_ops)
    return copy.deepcopy(chip_inst.options)

def soak_chips(chips_ops):
    chips_ops = copy.deepcopy(chips_ops)
    for chip_name, chip_ops in chips_ops.items():
        chip_inst = getattr(chips_lib, chip_ops.type)(options=chip_ops)
        chips_ops[chip_name] = copy.deepcopy(chip_inst.options)
    return copy.deepcopy(chips_ops)

def generate_chip_ops(**gene_ops):
    # forward compatibility
    return copy.deepcopy(gene_chip_ops.gene_chip_ops(**gene_ops))

def generate_chip(**gene_ops):
    return copy.deepcopy(gene_chip_ops.gene_chip_ops(**gene_ops))

def generate_chips(**gene_ops):
    chips_ops = gene_chips_ops.gene_chips_ops(**gene_ops)
    return copy.deepcopy(chips_ops)