import os
import copy
import toolbox

from func_modules.cpls import gene_cpls_ops
from func_modules.cpls import primitives

############################################################################################
# 和耦合线有关的参数处理
############################################################################################
from func_modules.cpls import primitives
from addict import Dict

def generate_coupling_lines(**gene_ops):
    """根据拓扑信息和qubits给出的cp_pins生成耦合线
    
    输入：
        qubits: qubits参数
        topology: 拓扑信息
        cp_type: 生成的耦合类型
        chip: 生成耦合的层
    输出： 
        cpls_ops: 耦合线参数
    """
    return copy.deepcopy(gene_cpls_ops.gene_cpls_ops(**gene_ops))

def soak_cpls(cpl_ops):
    """用类补充参数

    输入：
        cpl_ops: 待补全的耦合线参数

    输出：
        cpl_ops: 补全后的耦合线参数
    """
    cpl_ops = primitives.soak_cpls(coupling_lines=cpl_ops)
    return copy.deepcopy(cpl_ops)

def set_chips(cpls_ops, chip_name: str = None):
    """设置耦合线的芯片信息

    输入：
        cpls_ops: 耦合线参数
        chip_name: 要设置的芯片名称

    输出： 
        cpls_ops: 设置芯片名称后的耦合线参数
    """
    cpls_ops = primitives.set_chips(cpls_ops=cpls_ops, chip_name=chip_name)
    return copy.deepcopy(cpls_ops)

def set_types(cpls_ops, type):
    """设置耦合线的类型

    输入： 
        cpls: 耦合线参数
        type: 目标类型

    输出：
        cpls: 修改类型后的耦合先参数
    """
    cpls_ops = primitives.set_types(cpls=cpls_ops, type=type)
    return copy.deepcopy(cpls_ops)

def add_cpl(q0_ops: str = None,
            q0_pin_num: int = 0,
            q1_ops: str = None,
            q1_pin_num: int = 0,
            cp_type: str = "CouplingLineStraight", 
            chip: str = "chip0", 
            geometric_ops: Dict = Dict()):
    cpl_ops = primitives.add_cpl(q0_ops=q0_ops,
                                 q0_pin_num=q0_pin_num,
                                 q1_ops=q1_ops,
                                 q1_pin_num=q1_pin_num,
                                 cp_type=cp_type,
                                 chip=chip,
                                 geometric_ops=geometric_ops)
    return copy.deepcopy(cpl_ops)