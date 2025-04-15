import os
import copy
import toolbox

from func_modules.qubits import gene_qubits
from func_modules.qubits import primitives

############################################################################################
# 和跨线有关的参数处理
############################################################################################

from addict import Dict
from library import qubits
from cmpnt_frame.qubit import Qubit as Qubit_frame
import toolbox
import copy

def soak_qubit(qubit_ops):
    """根据类补全qubit参数

    输入：
        options: qubit参数

    输出：
        options: 补全后的qubit参数
    """
    qubit_ops = primitives.soak_qubit(qubit_ops=qubit_ops)
    return copy.deepcopy(qubit_ops)

def soak_qubits(qubits_ops):
    """根据类补全qubits参数

    输入：
        qubits_op: qubits参数

    输出：
        qubits_op: 补全后的qubit参数
    """
    qubits_ops=  primitives.soak_qubits(qubits_ops=qubits_ops)
    return copy.deepcopy(qubits_ops)

def check_cp_info(qubits):
    """检查每个qubit耦合的那个qubit是否存在，如果不存在就删除这个耦合信息

    输入：
        qubits: qubits参数

    输出：
        qubits: 处理耦合信息后的qubis参数
    """

    # 接口
    qubits = copy.deepcopy(qubits)

    # 依次每个qubit判断
    for q_name, q_op in qubits.items():
        for cp_dir, cp_q_name in q_op.coupling_qubits.items():
            if cp_q_name is None:
                continue
            if cp_q_name not in qubits.keys():
                qubits[q_name].coupling_qubits[cp_dir] = None
                print("{} 不存在，删除耦合信息".format(cp_q_name))

    return copy.deepcopy(qubits)

def change_qubits_type(qubits_ops, qubits_type):
    """设置qubits的类型

    输入： 
        qubits: qubits参数
        type: 目标类型

    输出：
        qubits: 修改类型后的耦合先参数
    """

    # 接口
    copy.deepcopy(qubits_ops)

    qubits_ops = primitives.dehy_qubits(qubits_ops)
    qubits_ops = primitives.set_qubits_type(qubits_ops, qubits_type)
    qubits_ops = primitives.soak_qubits(qubits_ops)

    return copy.deepcopy(qubits_ops)

def reset_cp_info(qubits):
    """重置qubits耦合信息
    
    输入：
        qubits: qubits参数

    输出：
        qubits: 重置耦合信息后的qubits参数
    """

    # 接口
    qubits = Dict(qubits)

    # 重置耦合信息
    coupling_qubits = Dict(
        top = None,
        bot = None,
        left = None,
        right = None
    )
    for q_name, q_ops in qubits.items():
        qubits[q_name].coupling_qubits = copy.deepcopy(coupling_qubits)

    return copy.deepcopy(qubits)

def topo_to_cp_info(qubits, topology):
    """根据拓扑信息补充qubit的耦合信息

    输入：
        qubits: qubits参数
        topology: 拓扑参数

    输出：  
        qubits: 补充耦合信息后的qubits参数
    """

    # 接口
    qubits = copy.deepcopy(qubits)

    # 补充耦合信息
    for edge in topology.edges:
        q0 = edge[0]
        q1 = edge[1]
        dir = toolbox.jg_dir(topology.positions[q0], topology.positions[q1])
        qubits[q1].coupling_qubits[dir] = q0
        dir = toolbox.jg_dir(topology.positions[q1], topology.positions[q0])
        qubits[q0].coupling_qubits[dir] = q1

    return copy.deepcopy(qubits)

def add_rd_info(qubits, readout_lines):
    """添加读取腔信息
    
    输入：
        qubits: qubits参数
        readout_lines: 读取腔参数
    
    输出：
        qubits: 补充读取腔信息后的qubits参数
    """

    # 接口
    qubits = copy.deepcopy(qubits)
    readout_lines = copy.deepcopy(readout_lines)

    # 依次补充读取腔信息
    for rd_name, rd_op in readout_lines.items():
        q_name = rd_op.qubit_connect
        if q_name == Dict():
            raise ValueError("没有与{}相连的qubit".format(rd_name))
        if q_name not in qubits:
            raise ValueError("与{}相连的qubit: {} 不存在！".format(rd_name, q_name))
        qubits[q_name].readout_line = rd_name

    return copy.deepcopy(qubits)

def dehy_qubits(qubits_ops):
    """将qubits参数简化成每个qubit类类型通用的参数

    输入：
        qubits_ops: 简化前qubits参数
    
    输出：
        new_qubits_ops: 简化后qubits参数
    """
    return copy.deepcopy(primitives.dehy_qubits(qubits_ops))

def set_chips(qubits, chip_name):
    """设置qubits的芯片信息

    输入：
        qubits: qubits参数
        chip_name: 要设置的芯片名称

    输出： 
        qubits: 设置芯片名称后的耦合线参数
    """

    # 接口
    copy.deepcopy(qubits)

    # 依次设置芯片
    for k, v in qubits.items():
        qubits[k].chip = chip_name

    return copy.deepcopy(qubits)

def set_chip(qubit, chip_name):
    """设置单个qubit的芯片
    
    输入：
        qubit: qubit的参数
        chip_name: 要设置的芯片名称

    输出： 
        qubit: 设置芯片名称后的耦合线参数
    """

    # 接口
    copy.deepcopy(qubit)

    # 设置芯片
    qubit.chip = chip_name

    return copy.deepcopy(qubit)

def generate_qubits(**generate_ops):
    qubits_ops = gene_qubits.gene_qubits(**generate_ops)
    return copy.deepcopy(qubits_ops)

def generate_qubits_from_topo(**gene_ops):
    """根据拓扑坐标在对应的位置生成qubits
    
    输入：
        topo_poss: 拓扑坐标

    输出：
        qubits: 生成的qubits参数
    """
    if "topo_positions" not in gene_ops.keys():
        raise ValueError("参数中没有topo_positions, 无法执行此参数! ")
    qubits_ops = gene_qubits.gene_qubits(**gene_ops)
    return copy.deepcopy(qubits_ops)

def find_qname_from_ctl_ops(ctl_ops, qubits_ops):
    for q_name, q_ops in qubits_ops.items():
        control_pins = copy.deepcopy(q_ops.control_pins)
        if ctl_ops.start_pos in control_pins:
            return q_name
        
    raise ValueError("没有找到控制线{}对应的qubit!".format(ctl_ops.name))

def find_qname_from_rdl_ops(rdl_ops, qubits_ops):
    for q_name, q_ops in qubits_ops.items():
        readout_pins = copy.deepcopy(q_ops.readout_pins)
        if rdl_ops.start_pos in readout_pins:
            return q_name
        
    raise ValueError("没有找到读取腔{}对应的qubit!".format(rdl_ops.name))