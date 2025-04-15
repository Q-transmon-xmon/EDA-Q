#########################################################################
# File Name: transmission_lines.py
# Description: This file mainly contains the automated wiring code for M*N TSV matrix transmission lines.
#########################################################################

from addict import Dict
import math
import copy
import re
import func_modules


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


# Return the coordinates of the top, bottom, left, and right boundaries of the qubits
def boundary_qubit_pos(qubits):
    """
    Return the boundary positions of the qubits.

    Input:
    qubits: Dictionary containing the position information of the qubits.

    Output:
    x_left, x_right, y_upper, y_lower: The left and right boundary positions and upper and lower boundary positions of the qubits.
    """
    qubits = copy.deepcopy(qubits)
    gds_positions = [qubit["gds_pos"] for qubit in qubits.values()]
    x_left, x_right = min([x for x, y in gds_positions]), max([x for x, y in gds_positions])
    y_upper, y_lower = max([y for x, y in gds_positions]), min([y for x, y in gds_positions])
    return x_left, x_right, y_upper, y_lower


# Return the maximum and minimum vertical coordinates of the end position of the readout line in the i-th row
def boundary_readout_line_pos(i, qubits, readout_lines):
    """
    Return the maximum and minimum vertical coordinates of the end position of the readout line in the i-th row.

    Input:
    i: Row number.
    qubits: Dictionary containing the position information of the qubits.
    readout_lines: Dictionary containing the position information of the readout lines.

    Output:
    The maximum and minimum vertical coordinates.
    """
    qubits = copy.deepcopy(qubits)
    readout_lines = copy.deepcopy(readout_lines)
    end_pos = []

    for q_name, q_op in qubits.items():
        if q_op.topo_pos[1] != i:
            continue
        rd_name = func_modules.rdls.find_rdl_name(readout_lines, q_op)
        end_pos.append(readout_lines[rd_name].end_pos)
    return max([y for x, y in end_pos]), min([y for x, y in end_pos])


# Return the maximum and minimum values of space in the i-th row of the readout line
def boundary_readout_line_space(i, qubits, readout_lines):
    """
    Return the maximum and minimum values of space in the i-th row of the readout line.

    Input:
    i: Row number.
    qubits: Dictionary containing the position information of the qubits.
    readout_lines: Dictionary containing the position information of the readout lines.

    Output:
    The maximum and minimum values of space.
    """
    qubits = copy.deepcopy(qubits)
    readout_lines = copy.deepcopy(readout_lines)
    space = []
    for q_name, q_op in qubits.items():
        if q_op.topo_pos[1] != i:
            continue
        rd_name = func_modules.rdls.find_rdl_name(readout_lines, q_op)
        space.append(readout_lines[rd_name].space)
    return max(space), min(space)


# Return the maximum and minimum values of pos for Pins in the specified direction
def boundary_pin_pos(direction, pins):
    """
    Return the maximum and minimum values of pos for Pins in the specified direction.

    Input:
    direction: Direction.
    pins: Dictionary containing the position information of the Pins.

    Output:
    The maximum and minimum values of pos.
    """
    pins = copy.deepcopy(pins)
    pos = []
    for k, v in pins.items():
        if k.startswith(f'pin_{direction}_'):
            pos.append(v["pos"])
    return max([x for x, y in pos]), min([x for x, y in pos]), max([y for x, y in pos]), min([y for x, y in pos])


# Return the maximum and minimum values of the starting distance for Pins in the specified direction
def boundary_pin_start_straight(direction, pins):
    """
    Return the maximum and minimum values of the starting distance for Pins in the specified direction.

    Input:
    direction: Direction.
    pins: Dictionary containing the starting distance information of the Pins.

    Output:
    The maximum and minimum values of the starting distance.
    """
    pins = copy.deepcopy(pins)
    start_straight = []
    for k, v in pins.items():
        if k.startswith(f'pin_{direction}_'):
            start_straight.append(v["start_straight"])
    return max(start_straight), min(start_straight)


# Return the maximum width of the qubits in the i-th column
def boundary_qubit_width(i, qubits):
    """
    Return the maximum width of the qubits in the i-th column.

    Input:
    i: Column number.
    qubits: Dictionary containing the position information of the qubits.

    Output:
    The maximum width.
    """
    qubits = copy.deepcopy(qubits)
    width = []

    for q_name, q_op in qubits.items():
        max_x = max(pos[0] for pos in q_op.outline)
        min_x = min(pos[0] for pos in q_op.outline)
        w = max_x - min_x
        if q_op.topo_pos[0] == i:
            width.append(w)

    return max(width), min(width)


# Generate transmission lines
def generate_tmls(qubits_ops, rdls_ops, pins_ops, tmls_type, chip_name):
    """
    Generate transmission lines.

    Input:
    qubits_ops: Dictionary describing the operation parameters of the qubits.
    rdls_ops: Dictionary describing the operation parameters of the readout lines.
    pins_ops: Dictionary describing the operation parameters of the Pins.
    tmls_type: String specifying the type of transmission lines.
    chip_name: String specifying the name of the chip.

    Output:
    tmls_ops: Dictionary of generated transmission line operation parameters.
    """
    print("Control_off_chip策略生成传输线...")

    # Interface
    topo_poss = Dict()
    for q_name, q_ops in qubits_ops.items():
        topo_poss[q_name] = copy.deepcopy(q_ops.topo_pos)
    qubits = copy.deepcopy(qubits_ops)
    pins = copy.deepcopy(pins_ops)
    readout_lines = copy.deepcopy(rdls_ops)

    # Generate transmission lines
    transmission_lines = Dict()

    old_topo_poss = convert_topo(topo_poss)

    ReadoutLine_start_r = 100
    row_num = max([y for x, y in old_topo_poss]) + 1
    column_num = max([x for x, y in old_topo_poss]) + 1
    total_num = row_num * 2
    upper_num = lower_num = math.floor(total_num / 4)
    if upper_num % 2 != 0:
        upper_num -= 1
        lower_num -= 1
    left_num = right_num = math.ceil((total_num - upper_num - lower_num) / 2)
    qubit_left, qubit_right, qubit_upper, qubit_lower = boundary_qubit_pos(qubits)
    # When there are Pins on the top and bottom
    if (upper_num >= 2):
        wiring_upper_distance = boundary_pin_pos("upper", pins)[3] - \
                                boundary_readout_line_pos(row_num - 1, qubits, readout_lines)[0] - \
                                boundary_pin_start_straight("upper", pins)[0] - \
                                boundary_readout_line_space(row_num - 1, qubits, readout_lines)[0]
        wiring_upper_gap = wiring_lower_gap = wiring_upper_distance / (upper_num / 2 + 1)

        wiring_left_distance = qubit_left - boundary_qubit_width(0, qubits)[0] / 2 - boundary_pin_pos("left", pins)[0] - \
                               boundary_pin_start_straight("left", pins)[0] - ReadoutLine_start_r
        wiring_left_gap = wiring_left_distance / (left_num + upper_num / 2 + 1)

        wiring_right_distance = boundary_pin_pos("right", pins)[1] - qubit_right - \
                                boundary_qubit_width(column_num - 1, qubits)[0] / 2 - \
                                boundary_pin_start_straight("right", pins)[0] - ReadoutLine_start_r
        wiring_right_gap = wiring_right_distance / (right_num + upper_num / 2 + 1)

        if (wiring_left_gap < 50 or wiring_right_gap < 50):
            raise ValueError("前芯片尺寸导致传输线距离过短。")

        for i in range(int(upper_num / 2)):
            start_pos = pins["pin_upper_{}".format(i)].pos
            end_pos = pins["pin_upper_{}".format(upper_num - i - 1)].pos
            [x, y] = start_pos
            y -= pins["pin_upper_{}".format(i)].start_straight
            start_straight_pos = [x, y]
            [x, y] = end_pos
            y -= pins["pin_upper_{}".format(upper_num - i - 1)].start_straight
            end_straight_pos = [x, y]

            conner_left1 = (start_straight_pos[0],
                            boundary_readout_line_pos(int(row_num - 1), qubits, readout_lines)[0] + (
                                        upper_num / 2 - i) * wiring_upper_gap)
            conner_right1 = (end_straight_pos[0],
                             boundary_readout_line_pos(int(row_num - 1), qubits, readout_lines)[0] + (
                                         upper_num / 2 - i) * wiring_upper_gap)
            conner_left2 = (qubit_left - (upper_num / 2 - i + 2) * wiring_left_gap - ReadoutLine_start_r -
                            boundary_qubit_width(0, qubits)[0] / 2,
                            boundary_readout_line_pos(int(row_num - 1), qubits, readout_lines)[0] + (
                                        upper_num / 2 - i) * wiring_upper_gap)
            conner_right2 = (
            qubit_right + (upper_num / 2 - i + 2) * wiring_right_gap + boundary_qubit_width(column_num - 1, qubits)[
                0] / 2, boundary_readout_line_pos(int(row_num - 1), qubits, readout_lines)[0] + (
                        upper_num / 2 - i) * wiring_upper_gap)
            conner_left3 = (qubit_left - (upper_num / 2 - i + 2) * wiring_left_gap - ReadoutLine_start_r -
                            boundary_qubit_width(0, qubits)[0] / 2,
                            boundary_readout_line_pos(int(row_num - (upper_num / 2 - i)), qubits, readout_lines)[0] +
                            boundary_readout_line_space(int(row_num - 1 - i), qubits, readout_lines)[0])
            conner_right3 = (
            qubit_right + (upper_num / 2 - i + 2) * wiring_right_gap + boundary_qubit_width(column_num - 1, qubits)[
                0] / 2, boundary_readout_line_pos(int(row_num - (upper_num / 2 - i)), qubits, readout_lines)[0] +
            boundary_readout_line_space(int(row_num - 1 - i), qubits, readout_lines)[0])

            pos = [start_pos, start_straight_pos, conner_left1, conner_left2, conner_left3, conner_right3,
                   conner_right2, conner_right1, end_straight_pos, end_pos]
            transmission_name = "transmission_lines_upper_{}".format(i)
            transmission_lines[transmission_name].name = transmission_name
            transmission_lines[transmission_name].pos = pos

        for i in range(int(lower_num / 2)):
            start_pos = pins["pin_lower_{}".format(i)].pos
            end_pos = pins["pin_lower_{}".format(lower_num - i - 1)].pos
            [x, y] = start_pos
            y += pins["pin_lower_{}".format(i)].start_straight
            start_straight_pos = [x, y]
            [x, y] = end_pos
            y += pins["pin_lower_{}".format(lower_num - i - 1)].start_straight
            end_straight_pos = [x, y]

            conner_left1 = (start_straight_pos[0], qubit_lower - (lower_num / 2 - i + 1) * wiring_lower_gap)
            conner_right1 = (end_straight_pos[0], qubit_lower - (lower_num / 2 - i + 1) * wiring_lower_gap)
            conner_left2 = (qubit_left - (lower_num / 2 - i + 2) * wiring_left_gap - ReadoutLine_start_r -
                            boundary_qubit_width(0, qubits)[0] / 2,
                            qubit_lower - (lower_num / 2 - i + 1) * wiring_lower_gap)
            conner_right2 = (
            qubit_right + (lower_num / 2 - i + 2) * wiring_right_gap + boundary_qubit_width(column_num - 1, qubits)[
                0] / 2, qubit_lower - (lower_num / 2 - i + 1) * wiring_lower_gap)
            conner_left3 = (qubit_left - (lower_num / 2 - i + 2) * wiring_left_gap - ReadoutLine_start_r -
                            boundary_qubit_width(0, qubits)[0] / 2,
                            boundary_readout_line_pos(int(lower_num / 2 - i) - 1, qubits, readout_lines)[0] +
                            boundary_readout_line_space(int(lower_num / 2 - i) - 1, qubits, readout_lines)[0])
            conner_right3 = (
            qubit_right + (lower_num / 2 - i + 2) * wiring_right_gap + boundary_qubit_width(column_num - 1, qubits)[
                0] / 2, boundary_readout_line_pos(int(lower_num / 2 - i) - 1, qubits, readout_lines)[0] +
            boundary_readout_line_space(int(lower_num / 2 - i) - 1, qubits, readout_lines)[0])

            pos = [start_pos, start_straight_pos, conner_left1, conner_left2, conner_left3, conner_right3,
                   conner_right2, conner_right1, end_straight_pos, end_pos]
            transmission_name = "transmission_lines_lower_{}".format(i)
            transmission_lines[transmission_name].name = transmission_name
            transmission_lines[transmission_name].pos = pos

        for i in range(left_num):
            start_pos = pins["pin_left_{}".format(i)].pos
            end_pos = pins["pin_right_{}".format(i)].pos
            [x, y] = start_pos
            x += pins["pin_left_{}".format(i)].start_straight
            start_straight_pos = [x, y]
            [x, y] = end_pos
            x -= pins["pin_right_{}".format(i)].start_straight
            end_straight_pos = [x, y]
            if (i <= math.ceil(left_num / 2)):
                conner_left1 = (start_straight_pos[0] + (left_num - i) * wiring_left_gap - ReadoutLine_start_r -
                                boundary_qubit_width(0, qubits)[0] / 2, start_straight_pos[1])
                conner_right1 = (
                end_straight_pos[0] - (right_num - i) * wiring_right_gap + boundary_qubit_width(column_num - 1, qubits)[
                    0] / 2, end_straight_pos[1])
                conner_left2 = (start_straight_pos[0] + (left_num - i) * wiring_left_gap - ReadoutLine_start_r -
                                boundary_qubit_width(0, qubits)[0] / 2,
                                boundary_readout_line_pos(int(row_num - upper_num / 2 - i) - 1, qubits, readout_lines)[
                                    0] + boundary_readout_line_space(int(row_num - upper_num / 2 - i) - 1, qubits,
                                                                     readout_lines)[0])
                conner_right2 = (
                end_straight_pos[0] - (right_num - i) * wiring_right_gap + boundary_qubit_width(column_num - 1, qubits)[
                    0] / 2, boundary_readout_line_pos(int(row_num - upper_num / 2 - i) - 1, qubits, readout_lines)[0] +
                boundary_readout_line_space(int(row_num - upper_num / 2 - i) - 1, qubits, readout_lines)[0])
            else:
                conner_left1 = (
                start_straight_pos[0] + i * wiring_left_gap - ReadoutLine_start_r - boundary_qubit_width(0, qubits)[
                    0] / 2, start_straight_pos[1])
                conner_right1 = (
                end_straight_pos[0] - i * wiring_right_gap + boundary_qubit_width(column_num - 1, qubits)[0] / 2,
                end_straight_pos[1])
                conner_left2 = (
                start_straight_pos[0] + i * wiring_left_gap - ReadoutLine_start_r - boundary_qubit_width(0, qubits)[
                    0] / 2, boundary_readout_line_pos(int(row_num - upper_num / 2 - i) - 1, qubits, readout_lines)[0] +
                boundary_readout_line_space(int(row_num - upper_num / 2 - i) - 1, qubits, readout_lines)[0])
                conner_right2 = (
                end_straight_pos[0] - i * wiring_right_gap + boundary_qubit_width(column_num - 1, qubits)[0] / 2,
                boundary_readout_line_pos(int(row_num - upper_num / 2 - i) - 1, qubits, readout_lines)[0] +
                boundary_readout_line_space(int(row_num - upper_num / 2 - i) - 1, qubits, readout_lines)[0])

            pos = [start_pos, start_straight_pos, conner_left1, conner_left2, conner_right2, conner_right1,
                   end_straight_pos, end_pos]
            transmission_name = "transmission_lines_horizontal_{}".format(i)
            transmission_lines[transmission_name].name = transmission_name
            transmission_lines[transmission_name].pos = pos
    # When there is no pin above or below
    else:
        wiring_left_distance = qubit_left - boundary_qubit_width(0, qubits)[0] / 2 - boundary_pin_pos("left", pins)[0] - \
                               boundary_pin_start_straight("left", pins)[0] - ReadoutLine_start_r
        wiring_left_gap = wiring_left_distance / (left_num + upper_num / 2 + 1)

        wiring_right_distance = boundary_pin_pos("right", pins)[1] - qubit_right - \
                                boundary_qubit_width(column_num - 1, qubits)[0] / 2 - \
                                boundary_pin_start_straight("right", pins)[0] - ReadoutLine_start_r
        wiring_right_gap = wiring_right_distance / (right_num + upper_num / 2 + 1)
        for i in range(left_num):
            start_pos = pins["pin_left_{}".format(i)].pos
            end_pos = pins["pin_right_{}".format(i)].pos
            [x, y] = start_pos
            x += pins["pin_left_{}".format(i)].start_straight
            start_straight_pos = [x, y]
            [x, y] = end_pos
            x -= pins["pin_right_{}".format(i)].start_straight
            end_straight_pos = [x, y]
            if (i <= math.ceil(left_num / 2)):
                conner_left1 = (start_straight_pos[0] + (left_num - i) * wiring_left_gap - ReadoutLine_start_r -
                                boundary_qubit_width(0, qubits)[0] / 2, start_straight_pos[1])
                conner_right1 = (
                end_straight_pos[0] - (right_num - i) * wiring_right_gap + boundary_qubit_width(column_num - 1, qubits)[
                    0] / 2, end_straight_pos[1])
                conner_left2 = (start_straight_pos[0] + (left_num - i) * wiring_left_gap - ReadoutLine_start_r -
                                boundary_qubit_width(0, qubits)[0] / 2,
                                boundary_readout_line_pos(int(row_num - upper_num / 2 - i) - 1, qubits, readout_lines)[
                                    0] + boundary_readout_line_space(int(row_num - upper_num / 2 - i) - 1, qubits,
                                                                     readout_lines)[0])
                conner_right2 = (
                end_straight_pos[0] - (right_num - i) * wiring_right_gap + boundary_qubit_width(column_num - 1, qubits)[
                    0] / 2, boundary_readout_line_pos(int(row_num - upper_num / 2 - i) - 1, qubits, readout_lines)[-1] +
                boundary_readout_line_space(int(row_num - upper_num / 2 - i) - 1, qubits, readout_lines)[0])

            else:
                conner_left1 = (
                start_straight_pos[0] + i * wiring_left_gap - ReadoutLine_start_r - boundary_qubit_width(0, qubits)[
                    0] / 2, start_straight_pos[1])
                conner_right1 = (
                end_straight_pos[0] - i * wiring_right_gap + boundary_qubit_width(column_num - 1, qubits)[0] / 2,
                end_straight_pos[1])
                conner_left2 = (
                start_straight_pos[0] + i * wiring_left_gap - ReadoutLine_start_r - boundary_qubit_width(0, qubits)[
                    0] / 2, boundary_readout_line_pos(int(row_num - upper_num / 2 - i) - 1, qubits, readout_lines)[0] +
                boundary_readout_line_space(int(row_num - upper_num / 2 - i) - 1, qubits, readout_lines)[0])
                conner_right2 = (
                end_straight_pos[0] - i * wiring_right_gap + boundary_qubit_width(column_num - 1, qubits)[0] / 2,
                boundary_readout_line_pos(int(row_num - upper_num / 2 - i) - 1, qubits, readout_lines)[0] +
                boundary_readout_line_space(int(row_num - upper_num / 2 - i) - 1, qubits, readout_lines)[0])

            pos = [start_pos, start_straight_pos, conner_left1, conner_left2, conner_right2, conner_right1,
                   end_straight_pos, end_pos]
            transmission_name = "transmission_lines_horizontal_{}".format(i)
            transmission_lines[transmission_name].name = transmission_name
            transmission_lines[transmission_name].pos = pos

    tmls_ops = copy.deepcopy(transmission_lines)
    tmls_ops = func_modules.tmls.set_chips(tmls_ops, chip_name)
    tmls_ops = func_modules.tmls.set_types(tmls_ops, tmls_type)
    tmls_ops = func_modules.tmls.soak_tmls(tmls_ops)

    return copy.deepcopy(tmls_ops)