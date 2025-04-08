import os
import copy
import toolbox

from func_modules.rdls import gene_rdls
from func_modules.rdls import primitives

def generate_readout_lines(**init_ops):
    rdls_ops = gene_rdls.gene_rdls(**init_ops)
    return copy.deepcopy(rdls_ops)

def find_rdl_name(rdls_ops, qubit_ops):
    rdl_name_result = None

    for rdl_name, rdl_ops in rdls_ops.items():
        if rdl_ops.start_pos in qubit_ops.readout_pins:
            rdl_name_result = rdl_ops.name

    if rdl_name_result is None:
        raise ValueError("找不到{}对应的读取腔！".format(qubit_ops.name))
    
    # print("-------------------------------------------------------------------")
    # toolbox.show_options(qubit_ops)
    # print("rdl_name = {}".format(rdl_name_result))
    # print("-------------------------------------------------------------------")
    
    return rdl_name_result