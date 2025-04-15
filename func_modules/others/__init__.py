import os
import copy
import toolbox

from func_modules.others import air_bridge_primitive
from func_modules.others import gene_others_ops
from func_modules.others import indium_primitive


from addict import Dict
import toolbox
import copy
from library import others as others_lib

def generate_others(**gene_ops):
    return copy.deepcopy(gene_others_ops.gene_others_ops(**gene_ops))