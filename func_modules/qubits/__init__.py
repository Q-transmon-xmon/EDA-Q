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
    """Complete according to class qubit parameter.

    input:
        qubit_ops: qubit parameter.

    output:
        qubit_ops: qubit parameter after completion.
    """
    qubit_ops = primitives.soak_qubit(qubit_ops=qubit_ops)
    return copy.deepcopy(qubit_ops)

def soak_qubits(qubits_ops):
    """Complete according to class qubits parameter.

    input:
        qubits_ops: qubits parameter.

    output:
        qubits_ops: qubit parameter after completion.
    """
    qubits_ops = primitives.soak_qubits(qubits_ops=qubits_ops)
    return copy.deepcopy(qubits_ops)

def check_cp_info(qubits):
    """Check each qubit's coupled qubit. If it doesn't exist, delete this coupling information.

    input:
        qubits: qubits parameter.

    output:
        qubits: qubits parameter after processing coupling information.
    """
    qubits = copy.deepcopy(qubits)
    for q_name, q_op in qubits.items():
        for cp_dir, cp_q_name in q_op.coupling_qubits.items():
            if cp_q_name is None:
                continue
            if cp_q_name not in qubits.keys():
                qubits[q_name].coupling_qubits[cp_dir] = None
                print(f"{cp_q_name} does not exist, deleting coupling information.")
    return copy.deepcopy(qubits)

def change_qubits_type(qubits_ops, qubits_type):
    """Set up qubits type.

    input:
        qubits_ops: qubits parameter.
        qubits_type: target type.

    output:
        qubits_ops: qubits parameter after modifying the type.
    """
    qubits_ops = copy.deepcopy(qubits_ops)
    qubits_ops = primitives.dehy_qubits(qubits_ops)
    qubits_ops = primitives.set_qubits_type(qubits_ops, qubits_type)
    qubits_ops = primitives.soak_qubits(qubits_ops)
    return copy.deepcopy(qubits_ops)

def reset_cp_info(qubits):
    """Reset qubits coupling information.

    input:
        qubits: qubits parameter.

    output:
        qubits: qubits parameter after resetting coupling information.
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
    """Supplement qubit coupling information based on topology information.

    input:
        qubits: qubits parameter.
        topology: topology parameter.

    output:
        qubits: qubits parameter after supplementing coupling information.
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
    """Add readout cavity information.

    input:
        qubits: qubits parameter.
        readout_lines: readout cavity parameter.

    output:
        qubits: qubits parameter after supplementing readout cavity information.
    """
    qubits = copy.deepcopy(qubits)
    readout_lines = copy.deepcopy(readout_lines)
    for rd_name, rd_op in readout_lines.items():
        q_name = rd_op.qubit_connect
        if q_name == Dict():
            raise ValueError(f"No qubit connected to {rd_name}.")
        if q_name not in qubits:
            raise ValueError(f"Qubit connected to {rd_name}: {q_name} does not exist!")
        qubits[q_name].readout_line = rd_name
    return copy.deepcopy(qubits)

def dehy_qubits(qubits_ops):
    """Simplify qubits parameters into each qubit's common parameters for class types.

    input:
        qubits_ops: qubits parameter before simplification.

    output:
        new_qubits_ops: qubits parameter after simplification.
    """
    return copy.deepcopy(primitives.dehy_qubits(qubits_ops))

def set_chips(qubits, chip_name):
    """Set up qubits chip information.

    input:
        qubits: qubits parameter.
        chip_name: the name of the chip to set up.

    output:
        qubits: qubits parameter after setting up the chip name.
    """
    qubits = copy.deepcopy(qubits)
    for k, v in qubits.items():
        qubits[k].chip = chip_name
    return copy.deepcopy(qubits)

def set_chip(qubit, chip_name):
    """Set up a single qubit's chip.

    input:
        qubit: qubit parameter.
        chip_name: the name of the chip to set up.

    output:
        qubit: qubit parameter after setting the chip name.
    """
    qubit = copy.deepcopy(qubit)
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
        num: int, the number of quantum bits.
        num_cols: int, the number of columns.
        num_rows: int, the number of rows.
        type: str, the type of qubits (default is "Transmon").
        chip: str, the name of the chip (default is "default_layer").
        dist: int, the spacing between quantum bits (default is 2000).
        geometric_options: Dict, additional geometric options.

    Output:
        qubits_ops: Dict, the generated set of operational parameters for quantum bits.
    """
    def generate_topo_pos(num, col, row):
        """
        Generate topological positions for quantum bits based on column and row numbers.

        Input:
            num: int, the number of quantum bits.
            col: int, the number of columns.
            row: int, the number of rows.

        Output:
            topo_pos: list, a list of topological positions for quantum bits.
        """
        topo_pos = []
        for x in range(col):
            for y in range(row):
                topo_pos.append((x, y))
                num -= 1
                if num == 0:
                    break
            if num == 0:
                break
        return copy.deepcopy(topo_pos)

    def generate_gds_pos(num, col, row, dist):
        """
        Generate GDS coordinates for quantum bits based on column and row numbers and spacing.

        Input:
            num: int, the number of quantum bits.
            col: int, the number of columns.
            row: int, the number of rows.
            dist: float, the spacing between quantum bits.

        Output:
            gds_pos: list, a list of GDS coordinates for quantum bits.
        """
        gds_pos = []
        for x in range(col):
            for y in range(row):
                gds_pos.append((x * dist, y * dist))
                num -= 1
                if num == 0:
                    break
            if num == 0:
                break
        return copy.deepcopy(gds_pos)

    topo_pos_list = generate_topo_pos(num=num, col=num_cols, row=num_rows)
    gds_pos_list = generate_gds_pos(num=num, col=num_cols, row=num_rows, dist=dist)

    qubits_ops = Dict()
    for i in range(num):
        q_name = "q" + str(i)
        qubits_ops[q_name] = Dict()
        qubits_ops[q_name].name = q_name
        qubits_ops[q_name].type = type
        qubits_ops[q_name].gds_pos = copy.deepcopy(gds_pos_list[i])
        qubits_ops[q_name].topo_pos = copy.deepcopy(topo_pos_list[i])
        qubits_ops[q_name].chip = chip
        for k, v in geometric_options.items():
            qubits_ops[q_name][k] = copy.deepcopy(v)
    return qubits_ops

def generate_qubits_from_topology(topo_ops: Dict = None, 
                                  type: str = "Transmon", 
                                  dist: int = 2000,
                                  geometric_options: Dict = Dict()):
    return

def generate_qubits_from_topo(**gene_ops):
    """Generate corresponding positions based on topological coordinates for qubits.

    input:
        topo_positions: Topological coordinates.

    output:
        qubits: Generated qubits parameter.
    """
    if "topo_positions" not in gene_ops.keys():
        raise ValueError("Parameter topo_positions is missing!")
    qubits_ops = gene_qubits.gene_qubits(**gene_ops)
    return copy.deepcopy(qubits_ops)

def find_qname_from_ctl_ops(ctl_ops, qubits_ops):
    for q_name, q_ops in qubits_ops.items():
        control_pins = copy.deepcopy(q_ops.control_pins)
        if ctl_ops.start_pos in control_pins:
            return q_name
    raise ValueError(f"No qubit found corresponding to control line {ctl_ops.name}!")

def find_qname_from_rdl_ops(rdl_ops, qubits_ops):
    for q_name, q_ops in qubits_ops.items():
        readout_pins = copy.deepcopy(q_ops.readout_pins)
        if rdl_ops.start_pos in readout_pins:
            return q_name
    raise ValueError(f"No qubit found corresponding to readout line {rdl_ops.name}!")