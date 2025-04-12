#########################################################################
# File Name: pins.py
# Description: Module for assigning pins for multiplexed lines in an N*N square matrix.
#              Includes functions for pin position conversion, boundary calculation, and pin generation.
#########################################################################

from addict import Dict
import math
import re
import copy
import func_modules


def convert_topo(topo_poss):
    """
    Due to version updates, perform format conversion to ensure compatibility with previous code.

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

    Args:
        topo_poss: Dictionary containing the old format topology position data.

    Returns:
        old_poss: List containing the converted old format topology position data.
    """
    topo_poss = copy.deepcopy(topo_poss)

    old_poss = []

    for q_name, q_topo_pos in topo_poss.items():
        old_poss.append(q_topo_pos)
    return copy.deepcopy(old_poss)


def boundary_qubit_pos(qubits):
    """
    Calculate the boundary positions of qubits on the chip.

    Args:
        qubits: Dictionary containing qubit position information.

    Returns:
        x_left: Float, the x-coordinate of the leftmost qubit position.
        x_right: Float, the x-coordinate of the rightmost qubit position.
        y_upper: Float, the y-coordinate of the highest qubit position.
        y_lower: Float, the y-coordinate of the lowest qubit position.
    """
    qubits = copy.deepcopy(qubits)
    gds_positions = [qubit["gds_pos"] for qubit in qubits.values()]
    x_left, x_right = min([x for x, y in gds_positions]), max([x for x, y in gds_positions])
    y_upper, y_lower = max([y for x, y in gds_positions]), min([y for x, y in gds_positions])
    return x_left, x_right, y_upper, y_lower


def count_points_in_quadrants(topo_poss):
    """
    Calculate the number of points in different quadrants.

    Args:
        topo_poss: Dictionary containing topology position data.

    Returns:
        upper_num: Integer, the number of points in the upper quadrant.
        lower_num: Integer, the number of points in the lower quadrant.
        left_num: Integer, the number of points in the left quadrant.
        right_num: Integer, the number of points in the right quadrant.
    """
    upper_num = 0
    lower_num = 0
    left_num = 0
    right_num = 0
    positions = convert_topo(topo_poss)
    num = len(positions)

    for x, y in positions:
        if x >= y and x + y <= max([x for x, y in positions]) and y <= max([y for x, y in positions]) / 2:
            lower_num += 1

    upper_lines = math.ceil(max([y for x, y in positions]) / 2)

    for i in range(upper_lines):
        upper_num += max([x for x, y in positions]) + 1 - i * 2

    upper_num += (sum(1 for x, y in positions if y == max([y for x, y in positions])) -
                  sum(1 for x, y in positions if y == (max([y for x, y in positions]) - 1)))

    left_num = right_num = int((num - upper_num - lower_num) / 2)
    return upper_num, lower_num, left_num, right_num


def generate_pins(qubits_ops, chip_ops, pins_type):
    """
    Main function to generate pins.

    Args:
        qubits_ops: Dictionary containing qubit operation parameters.
        chip_ops: Dictionary containing chip operation parameters.
        pins_type: String specifying the type of pins.

    Returns:
        pins_ops: Dictionary containing the generated pin information.
    """
    print("Flipchip_routing_IBM generating pins...")
    ########################### Interface ###########################

    topo_poss = Dict()
    for q_name, q_ops in qubits_ops.items():
        topo_poss[q_name] = copy.deepcopy(q_ops.topo_pos)

    qubits = copy.deepcopy(qubits_ops)
    chip = copy.deepcopy(chip_ops)

    pad_width = 120
    pad_gap = 100
    distance_to_chip = 350

    pins = Dict()

    # Add any required parameters

    ############################################################

    ############################ Input Check ###########################
    if chip == Dict() or chip is None:
        raise ValueError("No chip specified, cannot generate pins using this strategy!")
    ################################################################

    upper_num_controlline, lower_num_controlline, left_num_controlline, right_num_controlline = count_points_in_quadrants(
        topo_poss)
    upper_num = upper_num_controlline
    lower_num = lower_num_controlline
    left_num = left_num_controlline
    right_num = right_num_controlline

    max_x_num = (chip.end_pos[0] - chip.start_pos[0]) / (pad_width + pad_gap * 2) - 2
    max_y_num = (chip.end_pos[1] - chip.start_pos[1]) / (pad_width + pad_gap * 2) - 2

    x_left, x_right, y_upper, y_lower = boundary_qubit_pos(qubits)

    controlline_count = [0, 0, 0, 0]

    for i in range(upper_num):
        pin_name = "pin_upper_controlline_{}".format(controlline_count[0])
        controlline_count[0] += 1
        pins[pin_name].name = pin_name
        pins[pin_name].pos = [x_left + (x_right - x_left) / upper_num * i + (x_right - x_left) / upper_num / 2,
                              chip.end_pos[1] - distance_to_chip]
        pins[pin_name].distance_to_qubits = pins[pin_name].pos[1] - y_upper

    for i in range(lower_num):
        pin_name = "pin_lower_controlline_{}".format(controlline_count[1])
        controlline_count[1] += 1
        pins[pin_name].name = pin_name
        pins[pin_name].pos = [x_left + (x_right - x_left) / lower_num * i + (x_right - x_left) / lower_num / 2,
                              chip.start_pos[1] + distance_to_chip]
        pins[pin_name].distance_to_qubits = y_lower - pins[pin_name].pos[1]
        pins[pin_name].orientation = 180

    for i in range(left_num):
        pin_name = "pin_left_controlline_{}".format(controlline_count[2])
        controlline_count[2] += 1
        pins[pin_name].name = pin_name
        pins[pin_name].pos = [chip.start_pos[0] + distance_to_chip,
                              (y_upper - (y_upper - y_lower) / left_num * i - (y_upper - y_lower) / left_num / 2)]
        pins[pin_name].distance_to_qubits = x_left - pins[pin_name].pos[0]
        pins[pin_name].orientation = 90

    for i in range(right_num):
        pin_name = "pin_right_controlline_{}".format(controlline_count[3])
        controlline_count[3] += 1
        pins[pin_name].name = pin_name
        pins[pin_name].pos = [chip.end_pos[0] - distance_to_chip,
                              (y_upper - (y_upper - y_lower) / right_num * i - (y_upper - y_lower) / right_num / 2)]
        pins[pin_name].distance_to_qubits = pins[pin_name].pos[0] - x_right
        pins[pin_name].orientation = 270

    pins_ops = copy.deepcopy(pins)
    pins_ops = func_modules.pins.set_types(pins_ops, pins_type)
    pins_ops = func_modules.pins.set_chips(pins_ops, chip.name)
    pins_ops = func_modules.pins.soak_pins(pins_ops)

    return copy.deepcopy(pins_ops)