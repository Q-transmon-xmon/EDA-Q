import os
import copy
import toolbox

from func_modules.indium_bumps import gene_indium_bumps_ops
from func_modules.indium_bumps import indium_primitive


from addict import Dict
import toolbox
import copy

def generate_indium_bumps(**gene_ops):
    return copy.deepcopy(gene_indium_bumps_ops.generate_indium_bumps_ops(**gene_ops))