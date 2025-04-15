import os
import copy
import toolbox

from func_modules.equ_circ import gene_ec_ops

def generate_equivalent_circuit(**gene_ops):
    return copy.deepcopy(gene_ec_ops.gene_ec_ops(**gene_ops))