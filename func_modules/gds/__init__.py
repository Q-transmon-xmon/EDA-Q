import os
import copy
import toolbox

from func_modules.gds import gene_gds_ops

def generate_gds(**gene_ops):
    return copy.deepcopy(gene_gds_ops.gene_gds_ops(**gene_ops))