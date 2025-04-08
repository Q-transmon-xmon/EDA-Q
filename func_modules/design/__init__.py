import os
import copy
import toolbox

from func_modules.design import gene_design_ops

def generate_design(**gene_ops):
    return copy.deepcopy(gene_design_ops.gene_design_ops(**gene_ops))