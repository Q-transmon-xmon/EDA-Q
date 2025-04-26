import os
import copy
import toolbox

from func_modules.qubits import gene_qubits
from func_modules.qubits import primitives

############################################################################################
# Parameter processing related to crossing lines
############################################################################################

from addict import Dict
from library import qubits
from cmpnt_frame.qubit import Qubit as Qubit_frame
import toolbox
import copy

def soak_qubit(qubit_ops):
    """Complete according to classqubitparameter

    input：
        options: qubitparameter

    output：
        options: After completionqubitparameter
    """
    qubit_ops = primitives.soak_qubit(qubit_ops=qubit_ops)
    return copy.deepcopy(qubit_ops)

def soak_qubits(qubits_ops):
    """Complete according to classqubitsparameter

    input：
        qubits_op: qubitsparameter

    output：
        qubits_op: After completionqubitparameter
    """
    qubits_ops=  primitives.soak_qubits(qubits_ops=qubits_ops)
    return copy.deepcopy(qubits_ops)

def check_cp_info(qubits):
    """Check each onequbitThe coupled onequbitDoes it exist，If it doesn't exist, delete this coupling information

    input：
        qubits: qubitsparameter

    output：
        qubits: After processing coupled informationqubisparameter
    """

    # interface
    qubits = copy.deepcopy(qubits)

    # Each one in turnqubitjudge
    for q_name, q_op in qubits.items():
        for cp_dir, cp_q_name in q_op.coupling_qubits.items():
            if cp_q_name is None:
                continue
            if cp_q_name not in qubits.keys():
                qubits[q_name].coupling_qubits[cp_dir] = None
                print("{} 不存在，删除耦合信息".format(cp_q_name))

    return copy.deepcopy(qubits)

def change_qubits_type(qubits_ops, qubits_type):
    """set upqubitsType of

    input： 
        qubits: qubitsparameter
        type: target type

    output：
        qubits: 修改类型后的耦合先parameter
    """

    # interface
    copy.deepcopy(qubits_ops)

    qubits_ops = primitives.dehy_qubits(qubits_ops)
    qubits_ops = primitives.set_qubits_type(qubits_ops, qubits_type)
    qubits_ops = primitives.soak_qubits(qubits_ops)

    return copy.deepcopy(qubits_ops)

def reset_cp_info(qubits):
    """resetqubitscoupling information
    
    input：
        qubits: qubitsparameter

    output：
        qubits: resetcoupling information后的qubitsparameter
    """

    # interface
    qubits = Dict(qubits)

    # Reset coupling information
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
    """Supplement based on topology informationqubitCoupling information

    input：
        qubits: qubitsparameter
        topology: 拓扑parameter

    output：  
        qubits: After supplementing the coupling informationqubitsparameter
    """

    # interface
    qubits = copy.deepcopy(qubits)

    # Supplementary coupling information
    for edge in topology.edges:
        q0 = edge[0]
        q1 = edge[1]
        dir = toolbox.jg_dir(topology.positions[q0], topology.positions[q1])
        qubits[q1].coupling_qubits[dir] = q0
        dir = toolbox.jg_dir(topology.positions[q1], topology.positions[q0])
        qubits[q0].coupling_qubits[dir] = q1

    return copy.deepcopy(qubits)

def add_rd_info(qubits, readout_lines):
    """Add reading cavity information
    
    input：
        qubits: qubitsparameter
        readout_lines: 读取腔parameter
    
    output：
        qubits: After supplementing the reading of cavity informationqubitsparameter
    """

    # interface
    qubits = copy.deepcopy(qubits)
    readout_lines = copy.deepcopy(readout_lines)

    # Supplement and read cavity information sequentially
    for rd_name, rd_op in readout_lines.items():
        q_name = rd_op.qubit_connect
        if q_name == Dict():
            raise ValueError("没有与{}相连的qubit".format(rd_name))
        if q_name not in qubits:
            raise ValueError("与{}相连的qubit: {} 不存在！".format(rd_name, q_name))
        qubits[q_name].readout_line = rd_name

    return copy.deepcopy(qubits)

def dehy_qubits(qubits_ops):
    """supportqubitsSimplify the parameters into eachqubitCommon parameters for class types

    input：
        qubits_ops: Before simplificationqubitsparameter
    
    output：
        new_qubits_ops: After simplificationqubitsparameter
    """
    return copy.deepcopy(primitives.dehy_qubits(qubits_ops))

def set_chips(qubits, chip_name):
    """set upqubitsChip information

    input：
        qubits: qubitsparameter
        chip_name: 要set up的芯片名称

    output： 
        qubits: set up芯片名称后的耦合线parameter
    """

    # interface
    copy.deepcopy(qubits)

    # Set the chips in sequence
    for k, v in qubits.items():
        qubits[k].chip = chip_name

    return copy.deepcopy(qubits)

def set_chip(qubit, chip_name):
    """Set up a singlequbitThe chip
    
    input：
        qubit: qubitParameters for
        chip_name: 要设置The chip名称

    output： 
        qubit: Coupling line parameters after setting the chip name
    """

    # interface
    copy.deepcopy(qubit)

    # Set chip
    qubit.chip = chip_name

    return copy.deepcopy(qubit)

def generate_qubits(**generate_ops):
    qubits_ops = gene_qubits.gene_qubits(**generate_ops)
    return copy.deepcopy(qubits_ops)

def generate_qubits_1(num: int,
                    num_cols: int,
                    num_rows: int,
                    type: str = "Transmon",
                    chip: str = "default_layer",
                    dist: int = 2000,
                    geometric_options: Dict = Dict()):
    """
    Generate operational parameters based on the number of quantum bits and type.

    Input:
        gene_ops: dict, containing the number of quantum bits and type.

    Output:
        qubits_ops: dict, the generated set of operational parameters for quantum bits.
    """

    def generate_topo_pos(num, col, row):
        """
        Generate topological positions for quantum bits based on column and row numbers.

        Input:
            col: int, the number of columns.
            row: int, the number of rows.

        Output:
            topo_pos: list, a list of topological positions for quantum bits.
        """
        gds_pos = []
        for x in range(0, col):
            for y in range(0, row):
                gds_pos.append((x, y))
                num -= 1
                if num == 0:
                    break
        return copy.deepcopy(gds_pos)
    
    def generate_gds_pos(num, col, row, dist):
        """
        Generate GDS coordinates for quantum bits based on column and row numbers and spacing.

        Input:
            col: int, the number of columns.
            row: int, the number of rows.
            dist: float, the spacing between quantum bits.

        Output:
            gds_pos: list, a list of GDS coordinates for quantum bits.
        """
        gds_pos = []
        for x in range(0, col):
            for y in range(0, row):
                gds_pos.append((x*dist, y*dist))
                num -= 1
                if num == 0:
                    break
        return copy.deepcopy(gds_pos)
    
    topo_pos_list = generate_topo_pos(num=num, col=num_cols, row=num_rows)
    gds_pos_list = generate_gds_pos(num=num, col=num_cols, row=num_rows, dist=dist)

    qubits_ops = Dict()
    for i in range(num):
        q_name = "q" + str(i)
        qubits_ops[q_name].name = q_name
        qubits_ops[q_name].type = type
        qubits_ops[q_name].gds_pos = copy.deepcopy(gds_pos_list[i])
        qubits_ops[q_name].topo_pos = copy.deepcopy(topo_pos_list[i])
        qubits_ops[q_name].chip = chip
        for k, v in geometric_options:
            qubits_ops[q_name][k] = copy.deepcopy(v)
    return qubits_ops

def generate_qubits_from_topology(topo_ops: Dict = None, 
                                  type: str = "Transmon", 
                                  dist: int = 2000,
                                  geometric_options: Dict = Dict()):

    return

def generate_qubits_from_topo(**gene_ops):
    """Generate corresponding positions based on topological coordinatesqubits
    
    input：
        topo_poss: Topological coordinates

    output：
        qubits: Generatedqubitsparameter
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