import os
import copy
import toolbox

from func_modules.tmls import gene_tmls_ops
from func_modules.tmls import primitives

from components.transmission_lines import TransmissionLines
from library import transmission_lines as tmls_lib

def set_chips(tmls_ops, chip_name):
    tmls_ops = copy.deepcopy(tmls_ops)
    for tml_name, tml_ops in tmls_ops.items():
        tmls_ops[tml_name].chip = chip_name
    return copy.deepcopy(tmls_ops)

def set_types(tmls_ops, tmls_type):
    tmls_ops = copy.deepcopy(tmls_ops)
    for tml_name, tml_ops in tmls_ops.items():
        tmls_ops[tml_name].type = tmls_type
    return copy.deepcopy(tmls_ops)

def soak_tmls(tmls_ops):
    tmls_inst = TransmissionLines(options = tmls_ops)
    return copy.deepcopy(tmls_inst.options)

def soak_tml(tml_ops):
    tml_inst = getattr(tmls_lib, tml_ops.type)(tml_ops)
    return copy.deepcopy(tml_inst.options)

def generate_transmission_lines(**gene_ops):
    return copy.deepcopy(gene_tmls_ops.gene_tmls_ops(**gene_ops))