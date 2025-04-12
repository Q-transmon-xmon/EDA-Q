############################################################################################
# Cross-line related parameter processing
############################################################################################

from addict import Dict
import toolbox
import copy
from library import readout_lines

def qubits_to_rd(qubits):
    """Generate corresponding readout cavities based on qubit information.
    
    Input:
        qubits: qubits parameters

    Output:
        readout_lines: generated readout cavity parameters
    """

    # Interface
    readout_lines = Dict()
    qubits = copy.deepcopy(qubits)

    # Generate readout cavities
    for q_name, q_op in qubits.items():
        rd_name = q_name + "_readout"
        rd_op = Dict()
        rd_op.name = rd_name
        if q_op.type == "Xmon":
            rd_op.type = "ReadoutArrow"
            rd_op.chip = q_op.chip
            rd_op.qubit_connect = q_name
            rd_op.start_pos = q_op.readout_pins[0]
            rd_op.start_pos[0] += 50
            rd_op.start_pos[1] += 50
            readout_lines[rd_name] = Dict(rd_op)
        else:
            rd_op.type = "ReadoutLine"
            rd_op.chip = q_op.chip
            rd_op.qubit_connect = q_name
            rd_op.start_pos = q_op.readout_pins[0]
            rd_op.end_pos = [q_op.readout_pins[0][0], q_op.readout_pins[0][1] + 800]
            readout_lines[rd_name] = Dict(rd_op)
    readout_lines = soak_rd_lines(readout_lines)

    return copy.deepcopy(readout_lines)

def fix_control_off_bug(qubits, rdls_ops):
    """Fix the control offset bug based on qubits and readout line operations.
    
    Input:
        qubits: qubits parameters
        rdls_ops: readout line operations parameters

    Output:
        readout_lines: fixed readout line parameters
    """

    qubits = copy.deepcopy(qubits)
    readout_lines = copy.deepcopy(rdls_ops)

    # Force the end_pos to be consistent for each line
    only = None
    for k, v in readout_lines.items():
        cnt = 0
        for kk, vv in readout_lines.items():
            if v.end_pos[1] == vv.end_pos[1]:
                cnt += 1
        if cnt == 1:
            only = k
            break
    if only is None:
        pass
    else:
        q = readout_lines[only].qubit_connect
        qq = None
        topo_pos = qubits[q].topo_pos
        for k, v in qubits.items():
            if k == q:
                continue
            if qubits[q].topo_pos[1] == v.topo_pos[1]:
                qq = k
                break
        if qq is None:    # This case occurs when there is only one qubit per line
            return copy.deepcopy(readout_lines)
        qq_rd = qq + "_readout"
        readout_lines[only].end_pos[1] = readout_lines[qq_rd].end_pos[1]
    return copy.deepcopy(readout_lines)

def soak_rd_lines(rdls_ops):
    """Complete the readout cavity parameters based on the class.
    
    Input:
        rdls_ops: readout cavity parameters

    Output:
        rdls_ops: completed readout cavity parameters
    """

    # Interface
    rd_op = copy.deepcopy(rdls_ops)

    # Obtain the total readout cavity instance
    rds = readout_lines.ReadoutLines(rd_op)
    for rd_name, rd_options in rd_op.items():
        rd_inst = getattr(rds, rd_name)
        rd_op[rd_name] = Dict(rd_inst.options)

    # Interface
    rdls_ops = copy.deepcopy(rd_op)

    return copy.deepcopy(rdls_ops)
