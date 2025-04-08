import os
import copy
import toolbox

from func_modules.ctls import gene_ctls_ops
from func_modules.ctls import primitives

############################################################################################
# 修改控制线的参数
############################################################################################

from addict import Dict
import toolbox
import copy
from library import control_lines as ctls_lib

def set_types(ctls_ops, ctls_type):
    """修改控制线类型

    输入：
        ctls: 控制线参数
        type: 要修改的控制线的类型
    
    输出:
        ctls: 修改控制线类型后的参数
    """

    # 接口
    ctls_ops = copy.deepcopy(ctls_ops)

    # 逐个修改控制线类型
    for k, v in ctls_ops.items():
        ctls_ops[k].type = ctls_type
    
    return copy.deepcopy(ctls_ops)

def set_chips(ctls_ops, chip_name: str = None):
    """设置每个控制线的芯片信息

    输入：
        ctls_ops: 控制线的参数
        chip_name: 控制线所在芯片的名称
    
    输出：
        ctls_ops: 设置芯片信息后的控制线参数
    """

    # 接口
    ctls_ops = Dict(ctls_ops)
    
    # 逐个设置芯片信息
    for ctl_name, ctl_ops in ctls_ops.items():
        ctls_ops[ctl_name].chip = chip_name

    return copy.deepcopy(ctls_ops)

def soak_ctls(ctls_ops):
    copy.deepcopy(ctls_ops)
    for ctl_name, ctl_ops in ctls_ops.items():
        ctl_inst = getattr(ctls_lib, ctl_ops.type)(options=ctl_ops)
        ctls_ops[ctl_name] = copy.deepcopy(ctl_inst.options)
    return copy.deepcopy(ctls_ops)

def generate_control_lines(**gene_ops):
    return copy.deepcopy(gene_ctls_ops.gene_ctls_ops(**gene_ops))

def find_ctl_name(ctls_ops, qubit_ops):
    ctls_ops = copy.deepcopy(ctls_ops)
    qubit_ops = copy.deepcopy(qubit_ops)
 
    result = None

    for ctl_name, ctl_ops in ctls_ops.items():
        if ctl_ops.start_pos in qubit_ops.control_pins:
            result = ctl_name
            break
    if result is None:
        raise ValueError("找不到{}对应的控制线！".format(qubit_ops.name))
    return result