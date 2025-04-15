import os
import copy
import toolbox

from func_modules.crosvs import gene_crosvs_ops
from func_modules.crosvs import primitives

import copy

def generate_cross_overs(**gene_ops):
    return copy.deepcopy(gene_crosvs_ops.gene_crosvs_ops(**gene_ops))