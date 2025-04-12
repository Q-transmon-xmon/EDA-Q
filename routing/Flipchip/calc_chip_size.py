#########################################################################
# File Name: calc_chip_size.py
# Description: Module for calculating chip size.
#              Includes functions for calculating chip boundary coordinates and chip size.
#########################################################################

from addict import Dict
import copy, math
import func_modules

gap = 100


def calc_chip_size(qubits_ops, rdls_ops, pins_geometric_ops):
    """
    Function to calculate the chip size.

    Args:
        qubits_ops: Dictionary describing qubit operation parameters.
        rdls_ops: Dictionary describing readout line operation parameters.
        pins_geometric_ops: Dictionary describing geometric operation parameters for pins.

    Returns:
        start_pos: Tuple representing the starting position of the chip.
        end_pos: Tuple representing the ending position of the chip.
    """
    qubits = copy.deepcopy(qubits_ops)
    readout_lines = copy.deepcopy(rdls_ops)
    geometric_ops = copy.deepcopy(pins_geometric_ops)
    topo_poss = func_modules.topo.extract_topo_positions(qubits_ops=qubits)

    distance_to_chip = 380
    pad_width = geometric_ops.pad_width
    pad_gap = geometric_ops.pad_gap

    # Initialize maximum values
    max_x = max_y = float('-inf')

    # Iterate through all coordinates in the logical topology dictionary
    for coords in topo_poss.values():
        # Update the maximum logical x and y coordinates
        max_x = max(max_x, coords[0])
        max_y = max(max_y, coords[1])

    # Get the boundary coordinates of qubit positions
    x_left, x_right, y_upper, y_lower = boundary_qubit_pos(qubits)

    # Number of pins on the top, bottom, left, and right
    upper_num, lower_num, left_num, right_num = pin_nums(max_y + 1, max_x + 1)

    # Highest coordinate and space of the readout lines
    readout_end_y = boundary_readout_line_pos(max_y, readout_lines, qubits)[0]
    readout_space_y = boundary_readout_line_space(max_y, readout_lines, qubits)[0]

    # Get the boundary coordinates of qubit outlines
    qubits_left_x = boundary_qubits_outline(0, qubits)
    qubits_right_x = boundary_qubits_outline(max_x, qubits)

    # Pins boundary coordinates
    upper_pins_y = readout_end_y + readout_space_y + math.ceil(upper_num / 2) * gap + distance_to_chip
    lower_pins_y = y_lower - math.ceil(lower_num / 2) * gap - distance_to_chip
    left_pins_x = qubits_left_x[1] - math.ceil(upper_num / 2) * gap - distance_to_chip
    right_pins_x = qubits_right_x[0] + math.ceil(upper_num / 2) * gap + distance_to_chip

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

    start_pos = (left_pins_x - 400 - distance_to_chip, lower_pins_y - 400 - distance_to_chip)
    end_pos = (right_pins_x + 400 + distance_to_chip, upper_pins_y + 400 + distance_to_chip)

    return copy.deepcopy(start_pos), copy.deepcopy(end_pos)


def pin_nums(m, n):
    """
    Calculate the number of pins in each section.

    Args:
        m: Integer, number of rows.
        n: Integer, number of columns.

    Returns:
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


# Return the maximum and minimum y-coordinates of the end_pos of the readout lines in the i-th row
def boundary_readout_line_pos(i, readout_lines, qubits):
    """
    Return the maximum and minimum y-coordinates of the end_pos of the readout lines in the i-th row.

    Args:
        i: Integer, row number.
        readout_lines: Dictionary describing readout line operation parameters.
        qubits: Dictionary describing qubit operation parameters.

    Returns:
        max_y: Float, maximum y-coordinate value.
        min_y: Float, minimum y-coordinate value.
    """
    # Initialize a dictionary to store the readout lines in the i-th row
    line_in_row = {}

    # Iterate through readout_lines to determine which readout lines are in the i-th row
    for line_name, line_info in readout_lines.items():
        qubit_name = func_modules.qubits.find_qname_from_rdl_ops(line_info, qubits)
        qubit_info = qubits.get(qubit_name)

        # Ensure qubit_info is not empty and its topo_pos row coordinate matches i
        if qubit_info and qubit_info['topo_pos'][1] == i:
            line_in_row[line_name] = line_info

    # Check if there are any readout lines in the i-th row
    if not line_in_row:
        return None

    # Initialize maximum and minimum y-coordinate values
    max_y = float('-inf')
    min_y = float('inf')

    # Iterate through the readout lines in the i-th row and update the maximum and minimum y-coordinate values
    for line_name, line_info in line_in_row.items():
        end_pos_y = line_info['end_pos'][1]
        max_y = max(max_y, end_pos_y)
        min_y = min(min_y, end_pos_y)

    return max_y, min_y


# Return the maximum and minimum space values of the readout lines in the i-th row
def boundary_readout_line_space(i, readout_lines, qubits):
    """
    Return the maximum and minimum space values of the readout lines in the i-th row.

    Args:
        i: Integer, row number.
        readout_lines: Dictionary describing readout line operation parameters.
        qubits: Dictionary describing qubit operation parameters.

    Returns:
        max_space: Float, maximum space value.
        min_space: Float, minimum space value.
    """
    # Initialize a dictionary to store the readout lines in the i-th row
    line_in_row = {}

    # Iterate through readout_lines to determine which readout lines are in the i-th row
    for line_name, line_info in readout_lines.items():
        qubit_name = func_modules.qubits.find_qname_from_rdl_ops(line_info, qubits)
        qubit_info = qubits.get(qubit_name)

        # Ensure qubit_info is not empty and its topo_pos row coordinate matches i
        if qubit_info and qubit_info['topo_pos'][1] == i:
            line_in_row[line_name] = line_info

    # Check if there are any readout lines in the i-th row
    if not line_in_row:
        return None

    # Initialize maximum and minimum space values
    max_space = float('-inf')
    min_space = float('inf')

    # Iterate through the readout lines in the i-th row and update the maximum and minimum space values
    for line_name, line_info in line_in_row.items():
        space = line_info['space']
        max_space = max(max_space, space)
        min_space = min(min_space, space)

    return max_space, min_space


# Return the coordinates of the outermost qubits on the top, bottom, left, and right
def boundary_qubit_pos(qubits):
    """
    Return the coordinates of the outermost qubits on the top, bottom, left, and right.

    Args:
        qubits: Dictionary describing qubit operation parameters.

    Returns:
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


# Return the maximum and minimum x-coordinates of the qubit outlines in the i-th column
def boundary_qubits_outline(i, qubits):
    """
    Return the maximum and minimum x-coordinates of the qubit outlines in the i-th column.

    Args:
        i: Integer, column number.
        qubits: Dictionary describing qubit operation parameters.

    Returns:
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

    # Return None if no qubits are found in the i-th column
    if min_x == float('inf') or max_x == float('-inf'):
        return None

    return max_x + 100, min_x - 100