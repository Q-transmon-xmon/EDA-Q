############################################################################################
# Parameter processing related to coupling lines
############################################################################################

from addict import Dict
from library import coupling_lines as cpls_lib
import copy
import toolbox


def generate_cpls(topo_ops, qubits_ops, cpls_type, chip_name):
    """
    Generate coupling lines based on topology information and cp_pins provided by qubits.

    Input:
        topo_ops: Topology information
        qubits_ops: Qubits parameters
        cpls_type: Type of coupling to generate
        chip_name: Layer where the coupling is generated

    Output: 
        cpls_ops: Parameters of the coupling lines
    """
    # Information prompt
    print("Generating coupling lines based on topology information...")

    # Interface
    qubits_ops = copy.deepcopy(qubits_ops)
    topo_ops = copy.deepcopy(topo_ops)
    cpls_ops = Dict()

    # Determine if coupling_pins exist
    for qname, qops in qubits_ops.items():
        if len(qops.coupling_pins) == 0:
            raise ValueError(f"{qname} has no coupling_pins parameter and cannot automatically generate coupling lines.")

    # Generate coupling line parameters
    for edge in topo_ops.edges:
        q0 = edge[0]
        q1 = edge[1]
        # Generate common parameters for cpls_ops
        cp_name = f"{q0}_cp_{q1}"
        cpls_ops[cp_name] = Dict()
        cpls_ops[cp_name].name = cp_name
        cpls_ops[cp_name].type = cpls_type
        cpls_ops[cp_name].chip = chip_name
        cpls_ops[cp_name].qubits = [q0, q1]

        # Determine direction and generate further
        edge0 = topo_ops.positions[q0]
        edge1 = topo_ops.positions[q1]
        dir = toolbox.jg_dir(edge0, edge1)

        if dir == "left":    # q0 is to the left of q1
            q0_right = toolbox.find_rightmost_coordinate(qubits_ops[q0].coupling_pins)
            q1_left = toolbox.find_leftmost_coordinate(qubits_ops[q1].coupling_pins)
            cpls_ops[cp_name].start_pos = q0_right
            cpls_ops[cp_name].end_pos = q1_left
        elif dir == "right":    # q0 is to the right of q1
            q0_left = toolbox.find_leftmost_coordinate(qubits_ops[q0].coupling_pins)
            q1_right = toolbox.find_rightmost_coordinate(qubits_ops[q1].coupling_pins)
            cpls_ops[cp_name].start_pos = q0_left
            cpls_ops[cp_name].end_pos = q1_right
        elif dir == "top":    # q0 is above q1
            q0_bot = toolbox.find_botmost_coordinate(qubits_ops[q0].coupling_pins)
            q1_top = toolbox.find_topmost_coordinate(qubits_ops[q1].coupling_pins)
            cpls_ops[cp_name].start_pos = q0_bot
            cpls_ops[cp_name].end_pos = q1_top
        elif dir == "bot":    # q0 is below q1
            q0_top = toolbox.find_topmost_coordinate(qubits_ops[q0].coupling_pins)
            q1_bot = toolbox.find_botmost_coordinate(qubits_ops[q1].coupling_pins)
            cpls_ops[cp_name].start_pos = q0_top
            cpls_ops[cp_name].end_pos = q1_bot
        else:
            raise ValueError(f"Failed to create coupling line, edge {edge} is illegal!")

    # Obtain complete parameters
    cpls_ops = soak_cpls(cpls_ops)
    return copy.deepcopy(cpls_ops)


def soak_cpls(coupling_lines):
    """
    Supplement parameters with class.

    Input:
        coupling_lines: Coupling line parameters to be supplemented

    Output:
        coupling_lines: Supplemented coupling line parameters
    """
    # Interface
    coupling_lines = copy.deepcopy(coupling_lines)

    # Update parameters in sequence
    for cpl_name, cpl_ops in coupling_lines.items():
        cpl_inst = getattr(cpls_lib, cpl_ops.type)(options=cpl_ops)
        coupling_lines[cpl_name] = cpl_inst.options

    return copy.deepcopy(coupling_lines)


def set_chips(cpls_ops, chip_name: str = None):
    """
    Set the chip information for coupling lines.

    Input:
        cpls_ops: Coupling line parameters
        chip_name: The chip name to be set

    Output: 
        cpls_ops: Coupling line parameters after setting the chip name
    """
    # Interface
    cpls_ops = copy.deepcopy(cpls_ops)

    # Set the chip in sequence
    for cpl_name, cpl_ops in cpls_ops.items():
        cpls_ops[cpl_name].chip = chip_name

    return copy.deepcopy(cpls_ops)


def set_types(cpls, type):
    """
    Set the type of coupling lines.

    Input: 
        cpls: Coupling line parameters
        type: Target type

    Output:
        cpls: Coupling line parameters after modifying the type
    """
    # Interface
    cpls = copy.deepcopy(cpls)

    # Modify the type of coupling lines in sequence
    for k, v in cpls.items():
        cpls[k].type = type

    return copy.deepcopy(cpls)


def add_cpl(q0_ops: Dict = None,
            q0_pin_num: int = 0,
            q1_ops: Dict = None,
            q1_pin_num: int = 0,
            cp_type: str = "CouplingLineStraight", 
            chip: str = "chip0", 
            geometric_ops: Dict = Dict()):
    """
    Add operational parameters for coupling lines.

    Input:
        q0_ops: str, Operational parameters of quantum bit Q0 (including coupling pin information `coupling_pins`).
        q0_pin_num: int, The coupling pin number of Q0 (default is 0).
        q1_ops: str, Operational parameters of quantum bit Q1 (including coupling pin information `coupling_pins`).
        q1_pin_num: int, The coupling pin number of Q1 (default is 0).
        cp_type: str, Type of coupling line (default is "CouplingLineStraight").
        chip: str, Chip name (default is "chip0").
        geometric_ops: Dict, Geometric operation parameters (optional).

    Output:
        cpl_ops: Dict, Generated operational parameters for coupling lines.
    """
    q0_ops = copy.deepcopy(q0_ops)
    q1_ops = copy.deepcopy(q1_ops)

    cpl_ops = Dict()
    cpl_ops.name = f"{q0_ops.name}_cp_{q1_ops.name}"
    cpl_ops.type = cp_type
    cpl_ops.chip = chip
    cpl_ops.start_pos = copy.deepcopy(q0_ops.coupling_pins[q0_pin_num])
    cpl_ops.end_pos = copy.deepcopy(q1_ops.coupling_pins[q1_pin_num])
    for op_name, op in geometric_ops.items():
        cpl_ops[op_name] = copy.deepcopy(op)
        
    cpl_ops = getattr(cpls_lib, cpl_ops.type)(options=cpl_ops).options

    return copy.deepcopy(cpl_ops)