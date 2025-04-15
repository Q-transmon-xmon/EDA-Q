import os
import copy
import toolbox

from func_modules.tag import gene_tag_ops

def generate_tag(**gene_ops):
    return copy.deepcopy(gene_tag_ops.gene_tag_ops(**gene_ops))