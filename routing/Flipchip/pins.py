#########################################################################
# File Name: pins.py
# Description: Module for generating pins.
#              Includes functions for calculating pin positions and types.
#########################################################################

from addict import Dict
import math
import re
import copy
import func_modules

gap = 100


# Returns the maximum and minimum y-coordinates of the end_pos of the readout lines in the i-th row
def boundary_readout_line_pos(i, readout_lines, qubits):
    """
    Returns the maximum and minimum y-coordinates of the end_pos of the readout lines in the i-th row.

    Input:
        i: Integer, row number.
        readout_lines: Dictionary, describing the operation parameters of the readout lines.
        qubits: Dictionary, describing the operation parameters of the qubits.

    Output:
        max_y: Float, maximum y-coordinate value.
        min_y: Float, minimum y-coordinate value.
    """
    # Initialize a dictionary to store the readout lines in the i-th row
    line_in_row = {}

    # Iterate through readout_lines to determine which readout lines are in the i-th row
    for line_name, line_info in readout_lines.items():
        qubit_name = func_modules.qubits.find_qname_from_rdl_ops(line_info, qubits)
        qubit_info = qubits.get(qubit_name)

        # Confirm that qubit_info is not empty and its topo_pos row coordinate matches i
        if qubit_info and qubit_info['topo_pos'][1] == i:
            line_in_row[line_name] = line_info

    # Check if there are any readout lines in the i-th row
    if not line_in_row:
        return None

    # Initialize the maximum and minimum y-coordinate values
    max_y = float('-inf')
    min_y = float('inf')

    # Iterate through the readout lines in the i-th row to update the maximum and minimum y-coordinate values
    for line_name, line_info in line_in_row.items():
        end_pos_y = line_info['end_pos'][1]
        max_y = max(max_y, end_pos_y)
        min_y = min(min_y, end_pos_y)

    return max_y, min_y


# Returns the maximum and minimum space values of the readout lines in the i-th row
def boundary_readout_line_space(i, readout_lines, qubits):
    """
    Returns the maximum and minimum space values of the readout lines in the i-th row.

    Input:
        i: Integer, row number.
        readout_lines: Dictionary, describing the operation parameters of the readout lines.
        qubits: Dictionary, describing the operation parameters of the qubits.

    Output:
        max_space: Float, maximum space value.
        min_space: Float, minimum space value.
    """
    # Initialize a dictionary to store the readout lines in the i-th row
    line_in_row = {}

    # Iterate through readout_lines to determine which readout lines are in the i-th row
    for line_name, line_info in readout_lines.items():
        qubit_name = func_modules.qubits.find_qname_from_rdl_ops(line_info, qubits)
        qubit_info = qubits.get(qubit_name)

        # Confirm that qubit_info is not empty and its topo_pos row coordinate matches i
        if qubit_info and qubit_info['topo_pos'][1] == i:
            line_in_row[line_name] = line_info

    # Check if there are any readout lines in the i-th row
    if not line_in_row:
        return None

    # Initialize the maximum and minimum space values
    max_space = float('-inf')
    min_space = float('inf')

    # Iterate through the readout lines in the i-th row to update the maximum and minimum space values
    for line_name, line_info in line_in_row.items():
        space = line_info['space']
        max_space = max(max_space, space)
        min_space = min(min_space, space)

    return max_space, min_space


# Returns the coordinates of the outermost qubits on the top, bottom, left, and right
def boundary_qubit_pos(qubits):
    """
    Returns the coordinates of the outermost qubits on the top, bottom, left, and right.

    Input:
        qubits: Dictionary, describing the operation parameters of the qubits.

    Output:
        x_left: Float, x-coordinate of the leftmost qubit.
        x_right: Float, x-coordinate of the rightmost qubit.
        y_upper: Float, y-coordinate of the topmost qubit.
        y_lower: Float, y-coordinate of the bottommost qubit.
    """
    qubits = copy.deepcopy(qubits)
    gds_positions = [qubit["gds_pos"] for qubit in qubits.values()]
    x_left, x_right = min([x for x, y in gds_positions]), max([x for x, y in gds_positions])
    y_upper, y_lower = max([y for x, y in gds_positions]), min([y for x, y in gds_positions])
    return x_left, x_right, y_upper, y_lower


# Returns the maximum and minimum outline values of the qubits in the i-th column
def boundary_qubits_outline(i, qubits):
    """
    Returns the maximum and minimum outline values of the qubits in the i-th column.

    Input:
        i: Integer, column number.
        qubits: Dictionary, describing the operation parameters of the qubits.

    Output:
        max_x: Float, maximum x-coordinate.
        min_x: Float, minimum x-coordinate.
    """
    min_x = float('inf')
    max_x = float('-inf')

    for qubit in qubits.values():
        if qubit['topo_pos'][0] == i:  # Check if it is in the i-th column
            # Process each qubit's coupling_qubits
            for key, coupling_qubit in qubit['coupling_pins'].items():
                if coupling_qubit:  # Ensure coupling_qubit is not null
                    x = coupling_qubit[0]
                    min_x = min(min_x, x)
                    max_x = max(max_x, x)

    # If no qubits are found in the i-th column, return None
    if min_x == float('inf') or max_x == float('-inf'):
        return None

    return max_x + 100, min_x - 100


# Sequence for adding pins on the top and bottom
def create_alternate_list(m):
    """
    Creates an alternating sequence.

    Input:
        m: Integer, sequence length.

    Output:
        result: List, alternating sequence.
    """
    result = []
    for i in range((m + 2) // 2):
        result.append(i)
        if m - i != i:
            result.append(m - i)
    return result


def pin_nums(m, n):
    """
    Calculates the number of pins in each section.

    Input:
        m: Integer, number of rows.
        n: Integer, number of columns.

    Output:
        top_pins: Integer, number of pins on the top.
        bottom_pins: Integer, number of pins on the bottom.
        left_pins: Integer, number of pins on the left.
        right_pins: Integer, number of pins on the right.
    """
    # Calculate the number of pins in each section
    row_pins = 2 * m
    bit_pins = m * n
    total_pins = row_pins + bit_pins

    # Initialize the number of pins on the top, bottom, left, and right
    top_pins, bottom_pins, left_pins, right_pins = 0, 0, 0, 0

    # Row distribution dictionary
    row_distribution = {'top': [], 'bottom': [], 'sides': []}

    # Find the most balanced distribution method
    min_difference = float('inf')
    for rows_to_sides in range(m + 1):
        side_pins_per_row = rows_to_sides * (n + 2)
        top_bottom_pins = total_pins - side_pins_per_row

        top_rows = (m - rows_to_sides) // 2
        bottom_rows = m - rows_to_sides - top_rows

        current_top_pins = top_rows * (n + 2)
        current_bottom_pins = bottom_rows * (n + 2)
        current_side_pins = side_pins_per_row // 2

        current_difference = max(current_top_pins, current_bottom_pins, current_side_pins) - \
                             min(current_top_pins, current_bottom_pins, current_side_pins)

        if current_difference < min_difference:
            min_difference = current_difference
            top_pins = current_top_pins
            bottom_pins = current_bottom_pins
            left_pins = right_pins = current_side_pins

            # Update row distribution
            row_distribution = {
                'top': list(range(m - 1, m - top_rows - 1, -1)),
                'bottom': list(range(bottom_rows)),
                'sides': list(range(bottom_rows, m - top_rows))
            }

    # print("Rows with pins at the top:", row_distribution['top'])
    # print("Rows with pins at the bottom:", row_distribution['bottom'])
    # print("Rows with pins at the sides:", row_distribution['sides'])

    if (top_pins + bottom_pins + left_pins + right_pins != total_pins):
        right_pins += 1

    return top_pins, bottom_pins, left_pins, right_pins


import func_modules


def generate_pins(qubits, readout_lines, chip, pins_geometric_ops):
    """
    Main function for generating pins.

    Input:
        qubits: Dictionary, describing the operation parameters of the qubits.
        readout_lines: Dictionary, describing the operation parameters of the readout lines.
        chip: Dictionary, describing the operation parameters of the chip.
        pins_geometric_ops: Dictionary, describing the geometric operation parameters of the pins.

    Output:
        pins: Dictionary, operation parameters of the pins.
        chip: Dictionary, updated operation parameters of the chip.
    """
    ########################### Interface ###########################
    qubits = copy.deepcopy(qubits)
    readout_lines = copy.deepcopy(readout_lines)
    chip = copy.deepcopy(chip)
    pins_geometric_ops = copy.deepcopy(pins_geometric_ops)

    topo_poss = func_modules.topo.extract_topo_positions_from_qubits_ops(qubits)

    distance_to_chip = 380
    pad_width = pins_geometric_ops.pad_width
    pad_gap = pins_geometric_ops.pad_gap

    pins = Dict()

    # Add necessary parameters

    ############################################################

    ############################ Input Check ###########################
    if chip == Dict() or chip is None:
        raise ValueError("No chip specified, cannot generate pins using this strategy!")
    ################################################################
    # Initialize the maximum value
    max_x = max_y = float('-inf')

    # Iterate through all coordinates in the logical topology dictionary
    for coords in topo_poss.values():
        # Update the maximum logical x and y coordinates
        max_x = max(max_x, coords[0])
        max_y = max(max_y, coords[1])

    # Get the boundary coordinates of the qubit positions
    x_left, x_right, y_upper, y_lower = boundary_qubit_pos(qubits)

    # Number of pins on the top, bottom, left, and right
    upper_num, lower_num, left_num, right_num = pin_nums(max_y + 1, max_x + 1)
    # print(upper_num,lower_num,left_num,right_num,(max_y + 1)*(max_x + 1)+(max_y+1)*2)

    # Highest y-coordinate and space of the readout lines
    readout_end_y = boundary_readout_line_pos(max_y, readout_lines, qubits)[0]
    readout_space_y = boundary_readout_line_space(max_y, readout_lines, qubits)[0]

    # Get the boundary coordinates of the qubit shapes
    qubits_left_x = boundary_qubits_outline(0, qubits)
    qubits_right_x = boundary_qubits_outline(max_x, qubits)

    # Pins boundary coordinates
    upper_pins_y = readout_end_y + readout_space_y + math.ceil(upper_num / 2) * gap + distance_to_chip
    lower_pins_y = y_lower - math.ceil(lower_num / 2) * gap - distance_to_chip
    left_pins_x = qubits_left_x[1] - math.ceil(upper_num / 2) * gap - distance_to_chip
    right_pins_x = qubits_right_x[0] + math.ceil(upper_num / 2) * gap + distance_to_chip

    # # Get the center coordinates
    # center_x = (x_left + x_right)/2
    # center_y = (y_lower + y_upper)/2

    # # Alignment operation
    # # Current center coordinates of the pins
    # current_center_x = (left_pins_x + right_pins_x) / 2
    # current_center_y = (lower_pins_y + upper_pins_y) / 2

    # # Calculate the difference from the target center coordinates
    # delta_x = center_x - current_center_x
    # delta_y = center_y - current_center_y

    # # Adjust the pins boundary coordinates
    # upper_pins_y += delta_y
    # lower_pins_y += delta_y
    # left_pins_x += delta_x
    # right_pins_x += delta_x

    # Get the minimum chip length
    upper_length = (pad_gap * 2 + pad_width) * upper_num
    lower_length = (pad_gap * 2 + pad_width) * lower_num
    left_length = (pad_gap * 2 + pad_width) * left_num
    right_length = (pad_gap * 2 + pad_width) * right_num

    # Check if the large-scale chip will overflow and handle it
    if (upper_pins_y - lower_pins_y) < max(right_length, left_length):
        print("Vertical width overflow, adjusting chip size...")
        upper_pins_y += (max(right_length, left_length) - (upper_pins_y - lower_pins_y))
        lower_pins_y -= (max(right_length, left_length) - (upper_pins_y - lower_pins_y))

    if (right_pins_x - left_pins_x) < max(upper_length, lower_length):
        print("Horizontal width overflow, adjusting chip size...")
        left_pins_x -= (max(upper_length, lower_length) - (right_pins_x - left_pins_x))
        right_pins_x += (max(upper_length, lower_length) - (right_pins_x - left_pins_x))

    # # Check if the chip size meets the requirements
    # start_pos = (left_pins_x - 400 - distance_to_chip, lower_pins_y - 400 - distance_to_chip)
    # end_pos = (right_pins_x + 400 + distance_to_chip, upper_pins_y + 400 + distance_to_chip)
    # if chip.start_pos != start_pos or chip.end_pos != end_pos:
    #     raise ValueError("The routing requires a chip size of [{}], actual size is [{}]".format(start_pos, end_pos, chip.start_pos, chip.end_pos))

    # Set the chip size
    chip['start_pos'] = [left_pins_x - 400 - distance_to_chip, lower_pins_y - 400 - distance_to_chip]
    chip['end_pos'] = [right_pins_x + 400 + distance_to_chip, upper_pins_y + 400 + distance_to_chip]

    transmission_count = [0, 0, 0, 0]
    controlline_count = [0, 0, 0, 0]

    # Check the parity of the number of columns
    pins_round1 = math.ceil((max_x + 1) / 2)
    pins_round2 = math.floor((max_x + 1) / 2)

    # Sequence list for top and bottom pins
    pins_alternate_list = create_alternate_list(upper_num - 1)
    pins_count = 0

    # Set the number of iterations based on the parity of the columns
    round_all = upper_num // (max_x + 3) * (math.ceil((max_x + 1) / 2) + 1) if (
                pins_round1 != pins_round2) else math.ceil(upper_num / 2)
    create_transmission = True
    for i in range(round_all):
        # Transmission pin creation logic
        if create_transmission and controlline_count[0] % (pins_round1 + pins_round2) == 0 and controlline_count[
            0] != 0:
            for _ in range(2):  # Create two transmission pins
                pin_name = "pin_upper_transmission_{}".format(transmission_count[0])
                transmission_count[0] += 1
                pins[pin_name].pos = [
                    left_pins_x + (right_pins_x - left_pins_x) / upper_num * pins_alternate_list[pins_count] + (
                                right_pins_x - left_pins_x) / upper_num / 2,
                    chip.end_pos[1] - distance_to_chip]
                pins_count += 1
            create_transmission = False  # Set flag to False to avoid creating transmission pins in this round
        else:
            # Control line creation logic
            if pins_round1 != pins_round2 and (controlline_count[0] - pins_round2 * 2) % (
                    pins_round1 + pins_round2) == 0:
                pin_name = "pin_upper_control_{}".format(controlline_count[0])
                controlline_count[0] += 1
                pins[pin_name].pos = [
                    left_pins_x + (right_pins_x - left_pins_x) / upper_num * pins_alternate_list[pins_count] + (
                                right_pins_x - left_pins_x) / upper_num / 2,
                    chip.end_pos[1] - distance_to_chip]
                pins_count += 1
            else:
                for _ in range(2):  # Create two control line pins
                    pin_name = "pin_upper_control_{}".format(controlline_count[0])
                    controlline_count[0] += 1
                    pins[pin_name].pos = [
                        left_pins_x + (right_pins_x - left_pins_x) / upper_num * pins_alternate_list[pins_count] + (
                                    right_pins_x - left_pins_x) / upper_num / 2,
                        chip.end_pos[1] - distance_to_chip]
                    pins_count += 1

            if controlline_count[0] % (
                    pins_round1 + pins_round2) == 0:  # Check if a round of control line generation is complete
                create_transmission = True  # Reset flag to allow creating transmission pins in the next round

        pins[pin_name].name = pin_name
        pins[pin_name].distance_to_qubits = pins[pin_name].pos[1] - y_upper

    # Sequence list for top and bottom pins
    pins_alternate_list = create_alternate_list(lower_num - 1)
    pins_count = 0

    # Set the number of iterations based on the parity of the columns
    round_all = lower_num // (max_x + 3) * (math.ceil((max_x + 1) / 2) + 1) if (
                pins_round1 != pins_round2) else math.ceil(lower_num / 2)
    create_transmission = True  # Start with transmission pins

    for i in range(round_all):
        # If transmission pins should be created
        if create_transmission:
            for _ in range(2):  # Create two transmission pins
                pin_name = "pin_lower_transmission_{}".format(transmission_count[1])
                transmission_count[1] += 1
                pins[pin_name].pos = [
                    left_pins_x + (right_pins_x - left_pins_x) / lower_num * pins_alternate_list[pins_count] + (
                                right_pins_x - left_pins_x) / lower_num / 2,
                    chip.start_pos[1] + distance_to_chip]
                pins_count += 1
                pins[pin_name].orientation = 180

            create_transmission = False

        else:
            # Control line pin creation logic
            if pins_round1 != pins_round2 and (controlline_count[1] - pins_round2 * 2) % (
                    pins_round1 + pins_round2) == 0:
                pin_name = "pin_lower_control_{}".format(controlline_count[1])
                controlline_count[1] += 1
                pins[pin_name].pos = [
                    left_pins_x + (right_pins_x - left_pins_x) / lower_num * pins_alternate_list[pins_count] + (
                                right_pins_x - left_pins_x) / lower_num / 2,
                    chip.start_pos[1] + distance_to_chip]
                pins_count += 1
                pins[pin_name].orientation = 180
            else:
                for _ in range(2):  # Create two control line pins
                    pin_name = "pin_lower_control_{}".format(controlline_count[1])
                    controlline_count[1] += 1
                    pins[pin_name].pos = [
                        left_pins_x + (right_pins_x - left_pins_x) / lower_num * pins_alternate_list[pins_count] + (
                                    right_pins_x - left_pins_x) / lower_num / 2,
                        chip.start_pos[1] + distance_to_chip]
                    pins_count += 1
                    pins[pin_name].orientation = 180

            # Check if a round of control line generation is complete
            if controlline_count[1] % (pins_round1 + pins_round2) == 0:
                create_transmission = True  # Reset flag to allow creating transmission pins in the next round

        pins[pin_name].name = pin_name
        pins[pin_name].distance_to_qubits = y_lower - pins[pin_name].pos[1]
        pins[pin_name].orientation = 180

    exchang_label = 0
    control_counter = 0

    for i in range(left_num):
        if exchang_label % 2 == 0:
            interval = math.ceil((max_x + 3) / 2)
        else:
            interval = math.floor((max_x + 3) / 2)

        if control_counter % interval == 0:
            pin_name = "pin_left_transmission_{}".format(transmission_count[2])
            transmission_count[2] += 1
            exchang_label += 1
            control_counter = 0  # Reset counter
        else:
            pin_name = "pin_left_control_{}".format(controlline_count[2])
            controlline_count[2] += 1

        control_counter += 1  # Increment control_counter regardless of the case

        pins[pin_name].name = pin_name
        pins[pin_name].pos = [chip.start_pos[0] + distance_to_chip,
                              (upper_pins_y - (upper_pins_y - lower_pins_y) / left_num * i - (
                                          upper_pins_y - lower_pins_y) / left_num / 2)]
        pins[pin_name].distance_to_qubits = x_left - pins[pin_name].pos[0]
        pins[pin_name].orientation = 90

    exchang_label = 1
    control_counter = 0

    for i in range(right_num):
        if exchang_label % 2 == 0:
            interval = math.ceil((max_x + 3) / 2)
        else:
            interval = math.floor((max_x + 3) / 2)

        if control_counter % interval == 0:
            pin_name = "pin_right_transmission_{}".format(transmission_count[3])
            transmission_count[3] += 1
            exchang_label += 1
            control_counter = 0  # Reset counter
        else:
            pin_name = "pin_right_control_{}".format(controlline_count[3])
            controlline_count[3] += 1

        control_counter += 1  # Increment control_counter regardless of the case

        pins[pin_name].name = pin_name
        pins[pin_name].pos = [chip.end_pos[0] - distance_to_chip,
                              (upper_pins_y - (upper_pins_y - lower_pins_y) / right_num * i - (
                                          upper_pins_y - lower_pins_y) / right_num / 2)]
        pins[pin_name].distance_to_qubits = pins[pin_name].pos[0] - x_right
        pins[pin_name].orientation = 270

    return copy.deepcopy(pins), copy.deepcopy(chip)