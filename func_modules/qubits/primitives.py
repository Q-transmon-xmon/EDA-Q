##########################################################################
#Generate and configure the operational parameters of the qubits based on the input chip name, spacing, qubit type, and topological location.
##########################################################################

from addict import Dict
from library import qubits
from cmpnt_frame.qubit import Qubit as QubitFrame
import toolbox
import copy

def soak_qubit(qubit_ops):
    """
    Complete qubit parameters based on the class.

    Input:
        options: qubit parameters

    Output:
        options: completed qubit parameters
    """
    qubit_ops = copy.deepcopy(qubit_ops)
    q_inst = getattr(qubits, qubit_ops.type)(qubit_ops)
    qubit_ops = q_inst.options
    return copy.deepcopy(qubit_ops)

def soak_qubits(qubits_op):
    """
    Complete qubits parameters based on the class.

    Input:
        qubits_op: qubits parameters

    Output:
        qubits_op: completed qubit parameters
    """
    qubits_op = copy.deepcopy(qubits_op)
    for q_name, q_ops in qubits_op.items():
        q_inst = getattr(qubits, q_ops.type)(options=q_ops)
        qubits_op[q_name] = q_inst.options
    return copy.deepcopy(qubits_op)

def check_cp_info(qubits):
    """
    Check if the coupled qubit for each qubit exists, if not, remove the coupling information.

    Input:
        qubits: qubits parameters

    Output:
        qubits: qubits parameters after processing coupling information
    """
    qubits = copy.deepcopy(qubits)
    for q_name, q_op in qubits.items():
        for cp_dir, cp_q_name in q_op.coupling_qubits.items():
            if cp_q_name is None:
                continue
            if cp_q_name not in qubits.keys():
                qubits[q_name].coupling_qubits[cp_dir] = None
                print("{} does not exist, removing coupling information".format(cp_q_name))
    return copy.deepcopy(qubits)

def set_qubits_type(qubits, type):
    """
    Set the type of qubits.

    Input: 
        qubits: qubits parameters
        type: target type

    Output:
        qubits: qubits parameters with modified type
    """
    copy.deepcopy(qubits)
    for k, v in qubits.items():
        qubits[k].type = type
    return copy.deepcopy(qubits)

def reset_cp_info(qubits):
    """
    Reset qubits coupling information.
    
    Input:
        qubits: qubits parameters

    Output:
        qubits: qubits parameters with reset coupling information
    """
    qubits = Dict(qubits)
    coupling_qubits = Dict(
        top=None,
        bot=None,
        left=None,
        right=None
    )
    for q_name, q_ops in qubits.items():
        qubits[q_name].coupling_qubits = copy.deepcopy(coupling_qubits)
    return copy.deepcopy(qubits)

def topo_to_cp_info(qubits, topology):
    """
    Supplement qubit coupling information based on topological information.

    Input:
        qubits: qubits parameters
        topology: topological parameters

    Output:  
        qubits: qubits parameters with supplemented coupling information
    """
    qubits = copy.deepcopy(qubits)
    for edge in topology.edges:
        q0 = edge[0]
        q1 = edge[1]
        dir = toolbox.jg_dir(topology.positions[q0], topology.positions[q1])
        qubits[q1].coupling_qubits[dir] = q0
        dir = toolbox.jg_dir(topology.positions[q1], topology.positions[q0])
        qubits[q0].coupling_qubits[dir] = q1
    return copy.deepcopy(qubits)

def add_rd_info(qubits, readout_lines):
    """
    Add readout cavity information.
    
    Input:
        qubits: qubits parameters
        readout_lines: readout cavity parameters
    
    Output:
        qubits: qubits parameters with added readout cavity information
    """
    qubits = copy.deepcopy(qubits)
    readout_lines = copy.deepcopy(readout_lines)
    for rd_name, rd_op in readout_lines.items():
        q_name = rd_op.qubit_connect
        if q_name == Dict():
            raise ValueError("No qubit connected to {}".format(rd_name))
        if q_name not in qubits:
            raise ValueError("The qubit connected to {}: {} does not exist!".format(rd_name, q_name))
        qubits[q_name].readout_line = rd_name
    return copy.deepcopy(qubits)

def dehy(qubits_ops):
    """
    Simplify qubits parameters to common parameters for each qubit class type.

    Input:
        qubits_ops: original qubits parameters
    
    Output:
        new_qubits_ops: simplified qubits parameters
    """

    # 接口
    qubits_op = copy.deepcopy(qubits_ops)

    # 简化
    new_qubits_op = Dict()
    for q_name, q_op in qubits_op.items():
        new_qubits_op[q_name].name = copy.deepcopy(q_op.name)
        new_qubits_op[q_name].type = copy.deepcopy(q_op.type)
        new_qubits_op[q_name].gds_pos = copy.deepcopy(q_op.gds_pos)
        new_qubits_op[q_name].topo_pos = copy.deepcopy(q_op.topo_pos)
        new_qubits_op[q_name].chip = copy.deepcopy(q_op.chip)
        new_qubits_op[q_name].coupling_pins = copy.deepcopy(q_op.coupling_pins)
        new_qubits_op[q_name].coupling_qubits = copy.deepcopy(q_op.coupling_qubits)
        new_qubits_op[q_name].coupling_pins = copy.deepcopy(q_op.coupling_pins)
        new_qubits_op[q_name].readout_line = copy.deepcopy(q_op.readout_line)
        new_qubits_op[q_name].control_line = copy.deepcopy(q_op.control_line)
        new_qubits_op[q_name].readout_pins = copy.deepcopy(q_op.readout_pins)
        new_qubits_op[q_name].control_pins = copy.deepcopy(q_op.control_pins)
        new_qubits_op[q_name].outline = copy.deepcopy(q_op.outline)

    # 接口
    new_qubits_ops = copy.deepcopy(new_qubits_op)

    return copy.deepcopy(new_qubits_ops)

def set_cls_info(qubits, ctls):
    """
    Add control line information
    
    Input:
        qubits: qubits parameters
        ctls: control line parameters
    
    Output:
        qubits: qubits parameters with added control line information
    """
    qubits = copy.deepcopy(qubits)
    cls = copy.deepcopy(ctls)

    # Add control line information one by one
    for cl_name, cl_op in cls.items():
        q_name = cl_op.qubit_connect
        qubits[q_name].control_line = cl_name
        
    return copy.deepcopy(qubits)

def set_chips(qubits, chip_name):
    """
    Set the chip information for qubits

    Input:
        qubits: qubits parameters
        chip_name: the chip name to be set

    Output: 
        qubits: qubits parameters with set chip name
    """
    copy.deepcopy(qubits)

    # Set chip one by one
    for k, v in qubits.items():
        qubits[k].chip = chip_name

    return copy.deepcopy(qubits)

def set_chip(qubit, chip_name):
    """
    Set the chip for a single qubit
    
    Input:
        qubit: qubit parameters
        chip_name: the chip name to be set

    Output: 
        qubit: qubit parameters with set chip name
    """
    copy.deepcopy(qubit)

    # Set chip
    qubit.chip = chip_name

    return copy.deepcopy(qubit)

def dehy_qubits(qubits_ops):
    """
    Simplify qubits parameters to common parameters for each qubit class type.

    Input:
        qubits_ops: original qubits parameters
    
    Output:
        new_qubits_ops: simplified qubits parameters
    """
    qubits_ops = copy.deepcopy(qubits_ops)

    for q_name, q_ops in qubits_ops.items():
        q_ops.type = "Qubit"
        qubits_ops[q_name] = copy.deepcopy(QubitFrame(options=q_ops).options)
    
    return copy.deepcopy(qubits_ops)

def generate_qubits_from_topo(topo_positions: Dict,
                              chip_name: str = "chip0",
                              dist: float = 2000,
                              qubits_type: str = "Transmon"):
    """
    Generate operation parameters based on chip name, distance, qubit type, and topological positions.

    Input:
        gene_ops: dict, contains chip name, distance, qubit type, and topological positions.

    Output:
        qubits_ops: dict, a set of generated qubit operation parameters.
    """
    topo_positions = copy.deepcopy(topo_positions)

    import toolbox
    gds_pos = toolbox.generate_gds_pos2(topo_positions=topo_positions, dist=dist)
    
    qubits_ops = Dict()
    for q_name, topo_pos in topo_positions.items():
        qubits_ops[q_name].name = q_name
        qubits_ops[q_name].type = qubits_type
        qubits_ops[q_name].gds_pos = copy.deepcopy(gds_pos[q_name])
        qubits_ops[q_name].topo_pos = copy.deepcopy(topo_pos)
        qubits_ops[q_name].chip = chip_name

    return copy.deepcopy(qubits_ops)