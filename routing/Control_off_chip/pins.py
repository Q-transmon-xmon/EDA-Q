###############################################################################################
# File Name: pins.py
# Description: This file mainly contains the pin assignment code for M*N TSV matrix transmission lines.
###############################################################################################

from addict import Dict
import math, copy, func_modules


def convert_topo(topo_poss):
    """
    Due to version updates, format conversion is performed to ensure that previous code runs normally.
    Original format:
    topology.positions = [
        [0, 0],
        [1, 0],
        ...
    ]
    topology.edges = [
        [[0, 0], [1, 0]],
        [[0, 0], [0, 1]],
        ...
    ]
    New format:
    topology.positions = Dict(
        q0 = [0, 0],
        q1 = [1, 0],
        ...
    )
    topology.edges = [
        ["q0", "q1"],
        ["q0", "q13"],
        ...
    ]
    """
    topo_poss = copy.deepcopy(topo_poss)
    old_poss = []

    for q_name, q_topo_pos in topo_poss.items():
        old_poss.append(q_topo_pos)

    return copy.deepcopy(old_poss)


def boundary_qubit_pos(qubits):
    """
    Calculate the boundary positions of qubits.

    Input:
    qubits: Dictionary containing the position information of qubits.

    Output:
    x_left, x_right, y_upper, y_lower: The left and right boundary positions and upper and lower boundary positions of qubits.
    """
    qubits = copy.deepcopy(qubits)
    gds_positions = [qubit["gds_pos"] for qubit in qubits.values()]
    x_left, x_right = min([x for x, y in gds_positions]), max([x for x, y in gds_positions])
    y_upper, y_lower = max([y for x, y in gds_positions]), min([y for x, y in gds_positions])
    return x_left, x_right, y_upper, y_lower


# Generate launch_pad
def generate_pins(qubits_ops, chip_ops, pins_type):
    """
    Function to generate pins.

    Input:
    qubits_ops: Dictionary describing the operation parameters of qubits.
    chip_ops: Dictionary describing the operation parameters of the chip.
    pins_type: String specifying the type of pins.

    Output:
    pins_ops: Dictionary of generated pin operation parameters.
    """
    print("Control_off_chip strategy generating pins...")
    ########################### Interface ###########################

    topo_poss = Dict()
    for q_name, q_ops in qubits_ops.items():
        topo_poss[q_name] = copy.deepcopy(q_ops.topo_pos)

    qubits = copy.deepcopy(qubits_ops)
    chip = copy.deepcopy(chip_ops)
    pins_type = pins_type

    pins = Dict()

    # Add required parameters
    pad_width = 120
    pad_gap = 100
    distance_to_chip = 350
    ############################################################

    ############################ Input Check ###########################
    if chip == Dict() or chip is None:
        raise ValueError("No chip specified, cannot generate pins using this strategy!")
    ################################################################

    old_topo_poss = convert_topo(topo_poss)

    row_num = max([y for x, y in old_topo_poss]) + 1
    column_num = max([x for x, y in old_topo_poss]) + 1
    total_num = row_num * 2
    upper_num = lower_num = math.floor(total_num / 4)
    if upper_num % 2 != 0:
        upper_num -= 1
        lower_num -= 1
    left_num = right_num = math.ceil((total_num - upper_num - lower_num) / 2)
    max_x_num = (chip.end_pos[0] - chip.start_pos[0]) / (pad_width + pad_gap * 2) - 2
    max_y_num = (chip.end_pos[1] - chip.start_pos[1]) / (pad_width + pad_gap * 2) - 2
    if max_x_num < upper_num or max_y_num < left_num:
        raise ValueError("Current chip size causes pin overflow.")
    x_left, x_right, y_upper, y_lower = boundary_qubit_pos(qubits)
    for i in range(upper_num):
        pin_name = "pin_upper_{}".format(i)
        pins[pin_name] = Dict()
        pins[pin_name].name = pin_name
        pins[pin_name].pos = [x_left + (x_right - x_left) / upper_num * i + (x_right - x_left) / upper_num / 2,
                              chip.end_pos[1] - distance_to_chip]
        pins[pin_name].distance_to_qubits = pins[pin_name].pos[1] - y_upper

    for i in range(lower_num):
        pin_name = "pin_lower_{}".format(i)
        pins[pin_name] = Dict()
        pins[pin_name].name = pin_name
        pins[pin_name].pos = [x_left + (x_right - x_left) / lower_num * i + (x_right - x_left) / lower_num / 2,
                              chip.start_pos[1] + distance_to_chip]
        pins[pin_name].distance_to_qubits = y_lower - pins[pin_name].pos[1]
        pins[pin_name].orientation = 180

    for i in range(left_num):
        pin_name = "pin_left_{}".format(i)
        pins[pin_name] = Dict()
        pins[pin_name].name = pin_name
        pins[pin_name].pos = [chip.start_pos[0] + distance_to_chip,
                              (y_upper - (y_upper - y_lower) / left_num * i - (y_upper - y_lower) / left_num / 2)]
        pins[pin_name].distance_to_qubits = x_left - pins[pin_name].pos[0]
        pins[pin_name].orientation = 90

    for i in range(right_num):
        pin_name = "pin_right_{}".format(i)
        pins[pin_name] = Dict()
        pins[pin_name].name = pin_name
        pins[pin_name].pos = [chip.end_pos[0] - distance_to_chip,
                              (y_upper - (y_upper - y_lower) / right_num * i - (y_upper - y_lower) / right_num / 2)]
        pins[pin_name].distance_to_qubits = pins[pin_name].pos[0] - x_right
        pins[pin_name].orientation = 270

    pins_ops = copy.deepcopy(pins)
    pins_ops = func_modules.pins.set_chips(pins_ops, chip_ops.name)
    pins_ops = func_modules.pins.set_types(pins_ops, pins_type=pins_type)
    pins_ops = func_modules.pins.soak_pins(pins_ops)

    return copy.deepcopy(pins_ops)