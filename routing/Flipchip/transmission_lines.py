#########################################################################
# File Name: transmission_lines.py
# Description: Module for generating transmission lines.
#              Includes functions for calculating transmission line paths and generating transmission lines.
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
        qubit_name = func_modules.qubits.find_qname_from_rdl_ops(rdl_ops=line_info, qubits_ops=qubits)
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
        qubit_name = func_modules.qubits.find_qname_from_rdl_ops(rdl_ops=line_info, qubits_ops=qubits)
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
        row_distribution: Dictionary, row distribution.
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

    return top_pins, bottom_pins, left_pins, right_pins, row_distribution['top'], row_distribution['bottom'], \
    row_distribution['sides']


def calculate_corner_points(upper_pins_y, lower_pins_y, left_pins_x, right_pins_x, upper_num, lower_num):
    """
    Calculates the list of diagonal corner points for the four corners.

    Input:
        upper_pins_y: Float, y-coordinate of the upper pins.
        lower_pins_y: Float, y-coordinate of the lower pins.
        left_pins_x: Float, x-coordinate of the left pins.
        right_pins_x: Float, x-coordinate of the right pins.
        upper_num: Integer, number of upper pins.
        lower_num: Integer, number of lower pins.

    Output:
        ul_points: List, upper left corner point coordinates.
        ll_points: List, lower left corner point coordinates.
        ur_points: List, upper right corner point coordinates.
        lr_points: List, lower right corner point coordinates.
    """
    # Define the step size
    delta = gap
    # Upper left corner point coordinates
    upper_left_points = [[left_pins_x + delta * (i - 1), upper_pins_y - delta * i]
                         for i in range(math.ceil(upper_num / 2))]
    # Lower left corner point coordinates
    lower_left_points = [[left_pins_x + delta * (i - 1) + 300, lower_pins_y + delta * i - 300]
                         for i in range(math.ceil(lower_num / 2))]
    # Upper right corner point coordinates
    upper_right_points = [[right_pins_x - delta * (i - 1), upper_pins_y - delta * i]
                          for i in range(math.floor(upper_num / 2))]
    # Lower right corner point coordinates
    lower_right_points = [[right_pins_x - delta * (i - 1) - 300, lower_pins_y + delta * i - 300]
                          for i in range(math.floor(lower_num / 2))]
    return upper_left_points, lower_left_points, upper_right_points, lower_right_points


def find_transmission_indices(pins, direction):
    """
    Extracts all types of pins and their x-coordinates, and finds the indices of each "transmission" pin in the sorted list of type pins.

    Input:
        pins: Dictionary, pin information.
        direction: String, direction.

    Output:
        transmission_indices: List, transmission line indices.
    """
    # Extract all types of pins and their x-coordinates
    direction_pins = {k: v['pos'][0] for k, v in pins.items() if direction in k}
    # Sort these pins by x-coordinate
    sorted_direction_pins = sorted(direction_pins.items(), key=lambda item: item[1])
    # Get the names of "transmission" type pins
    direction_transmission_pins = [k for k in direction_pins if direction + '_transmission' in k]
    # Find the indices of each "transmission" pin in the sorted list of type pins
    direction_transmission_indices = [sorted_direction_pins.index((pin, direction_pins[pin])) for pin in
                                      direction_transmission_pins]
    # Reorder the indices by comparing every two pins
    reordered_indices = []
    for i in range(0, len(direction_transmission_indices), 2):
        if i + 1 < len(direction_transmission_indices):
            # If there are two pins to compare
            first_index = direction_transmission_indices[i]
            second_index = direction_transmission_indices[i + 1]
            reordered_indices.extend(sorted([first_index, second_index]))
        else:
            # If it is the last single pin
            reordered_indices.append(direction_transmission_indices[i])

    return reordered_indices


# Calculates the initial position coordinate set
def calculate_init_point_coordinates(pins, transmission_indices, direction):
    """
    Calculates the initial position coordinate set.

    Input:
        pins: Dictionary, pin information.
        transmission_indices: List, transmission line indices.
        direction: String, direction.

    Output:
        coordinates: List, initial position coordinate set.
    """
    coordinates = []

    # Get all pins sorted
    all_pins_sorted = sorted([k for k in pins.keys() if direction in k], key=lambda k: pins[k]['pos'][0])

    for index in transmission_indices:
        # Get the corresponding pin name from the sorted list
        pin_name = all_pins_sorted[index]
        if pin_name in pins:
            x, y = pins[pin_name]['pos']
            coordinates.append((x, y))

    return coordinates


# Calculates the initial straight line point coordinates
def calculate_start_straight_point_coordinates(pins, num, transmission_indices, direction):
    """
    Calculates the starting straight line point coordinates.

    Input:
        pins: Dictionary, pin information.
        num: Integer, number of pins.
        transmission_indices: List, transmission line indices.
        direction: String, direction.

    Output:
        coordinates: List, starting straight line point coordinates.
    """
    coordinates = []

    # Get all pins sorted
    all_pins_sorted = sorted([k for k in pins.keys() if direction in k], key=lambda k: pins[k]['pos'][0])

    for index in transmission_indices:
        # Get the corresponding pin name from the sorted list
        pin_name = all_pins_sorted[index]
        if pin_name in pins:
            x, y = pins[pin_name]['pos']
            if direction == 'upper':
                if index < (num - 1) / 2:
                    new_x = x
                    new_y = y - index * gap - gap
                else:
                    new_x = x
                    new_y = y - (num - index - 1) * gap - gap
            elif direction == 'lower':
                if index < (num - 1) / 2:
                    new_x = x
                    new_y = y + index * gap + gap
                else:
                    new_x = x
                    new_y = y + (num - index - 1) * gap + gap
            elif direction == 'left':
                if index < (num - 1) / 2:
                    new_x = x + gap * index + gap
                    new_y = y
                else:
                    new_x = x + (num - index - 1) * gap + gap
                    new_y = y

            elif direction == 'right':
                if index < (num - 1) / 2:
                    new_x = x - gap * index - gap
                    new_y = y
                else:
                    new_x = x - (num - index - 1) * gap - gap
                    new_y = y

            coordinates.append((new_x, new_y))

    return coordinates


def calculate_transmission_boundary_point(i, qubits, readout_lines, qubits_left_x, qubits_right_x):
    """
    Calculates the transmission line boundary point coordinates.

    Input:
        i: Integer, row number.
        qubits: Dictionary, qubit operation parameters.
        readout_lines: Dictionary, readout line operation parameters.
        qubits_left_x: Float, x-coordinate of the leftmost qubit.
        qubits_right_x: Float, x-coordinate of the rightmost qubit.

    Output:
        boundary_point: Tuple, transmission line boundary point coordinates.
    """
    # Initialize a dictionary to store the readout pins in the i-th row
    line_in_row = {}

    # Iterate through readout_lines to determine which readout lines are in the i-th row
    for line_name, line_info in readout_lines.items():
        qubit_name = func_modules.qubits.find_qname_from_rdl_ops(rdl_ops=line_info, qubits_ops=qubits)
        qubit_info = qubits.get(qubit_name)

        # Confirm that qubit_info is not empty and its topo_pos row coordinate matches i
        if qubit_info and qubit_info['topo_pos'][1] == i:
            line_in_row[line_name] = line_info

    # Check if there are any readout lines in the i-th row
    if not line_in_row:
        return None

    # Initialize the maximum y-coordinate and space values
    max_y = float('-inf')
    max_space = float('-inf')

    # Iterate through the readout lines in the i-th row to update the maximum y-coordinate and space values
    for line_name, line_info in line_in_row.items():
        end_pos_y = line_info['end_pos'][1]
        space = line_info['space']
        max_y = max(max_y, end_pos_y)
        max_space = max(max_space, space)

    return (qubits_left_x - 100, max_y + max_space), (qubits_right_x + 100, max_y + max_space)


def generate_transmission_lines(qubits, readout_lines, pins, chip):
    """
    Main function for generating transmission lines.

    Input:
        qubits: Dictionary, describing the operation parameters of the qubits.
        readout_lines: Dictionary, describing the operation parameters of the readout lines.
        pins: Dictionary, pin information.
        chip: Dictionary, chip information.

    Output:
        transmission_lines: Dictionary, transmission line information.
    """
    # Interface
    qubits = copy.deepcopy(qubits)
    readout_lines = copy.deepcopy(readout_lines)
    pins = copy.deepcopy(pins)
    chip = copy.deepcopy(chip)

    topo_poss = func_modules.topo.extract_topo_positions_from_qubits_ops(qubits)

    # Define transmission lines
    transmission_lines = Dict()

    distance_to_chip = 380

    ############################ Input Check ###########################
    if chip == Dict() or chip is None:
        raise ValueError("No chip specified, cannot generate transmission_lines using this strategy!")

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
    upper_num, lower_num, left_num, right_num, upper_lines, lower_lines, side_lines = pin_nums(max_y + 1, max_x + 1)

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

    # Define the list of diagonal corner points for the four corners
    ul_points, ll_points, ur_points, lr_points = calculate_corner_points(upper_pins_y, lower_pins_y, left_pins_x,
                                                                         right_pins_x, upper_num, lower_num)

    direction = ['upper', 'lower', 'left', 'right']
    num = Dict()
    num['upper'] = upper_num
    num['lower'] = lower_num
    num['left'] = left_num
    num['right'] = right_num

    # Get transmission line indices
    transmission_indices = Dict()
    for d in direction:
        transmission_indices[d] = find_transmission_indices(pins, d)

    # Get initial position coordinates
    start_pin_point = Dict()
    for d in direction:
        start_pin_point[d] = calculate_init_point_coordinates(pins, transmission_indices[d], d)

    # Get initial straight line coordinates
    start_straight_point = Dict()
    for d in direction:
        start_straight_point[d] = calculate_start_straight_point_coordinates(pins, num[d], transmission_indices[d], d)

    # Get diagonal corner point coordinates
    corner_points = Dict()
    for d in direction:
        corner_points[d] = []
    for i in transmission_indices['upper']:
        if (i < upper_num / 2):
            corner_points['upper'].append(ul_points[i])
        else:
            corner_points['upper'].append(ur_points[upper_num - 1 - i])
    for i in transmission_indices['lower']:
        if (i < lower_num / 2):
            corner_points['lower'].append(ll_points[i])
        else:
            corner_points['lower'].append(lr_points[lower_num - 1 - i])

    # Get transmission line end positions
    transmission_boundary_point = Dict()
    transmission_boundary_point['upper'] = []
    transmission_boundary_point['lower'] = []
    transmission_boundary_point['left'] = []
    transmission_boundary_point['right'] = []

    upper_lines.reverse()
    for line in upper_lines:
        transmission_boundary_point['upper'].append(
            calculate_transmission_boundary_point(line, qubits, readout_lines, qubits_left_x[1], qubits_right_x[0])[0])
        transmission_boundary_point['upper'].append(
            calculate_transmission_boundary_point(line, qubits, readout_lines, qubits_left_x[1], qubits_right_x[0])[1])
    lower_lines.reverse()
    for line in lower_lines:
        transmission_boundary_point['lower'].append(
            calculate_transmission_boundary_point(line, qubits, readout_lines, qubits_left_x[1], qubits_right_x[0])[0])
        transmission_boundary_point['lower'].append(
            calculate_transmission_boundary_point(line, qubits, readout_lines, qubits_left_x[1], qubits_right_x[0])[1])
    side_lines.reverse()
    for line in side_lines:
        transmission_boundary_point['left'].append(
            calculate_transmission_boundary_point(line, qubits, readout_lines, qubits_left_x[1], qubits_right_x[0])[0])
        transmission_boundary_point['right'].append(
            calculate_transmission_boundary_point(line, qubits, readout_lines, qubits_left_x[1], qubits_right_x[0])[1])

    # Provide transmission line paths
    for d in direction:
        if (d == 'upper' or d == 'lower'):
            for i in range(len(transmission_indices[d])):
                if (i % 2 == 0):
                    start_pin_pos = start_pin_point[d][i]
                    start_straight_pos = start_straight_point[d][i]
                    start_corner_pos = corner_points[d][i]
                    start_transmission_boundary_pos = transmission_boundary_point[d][i]
                    i += 1
                else:
                    end_pin_pos = start_pin_point[d][i]
                    end_straight_pos = start_straight_point[d][i]
                    end_corner_pos = corner_points[d][i]
                    end_transmission_boundary_pos = transmission_boundary_point[d][i]

                    transmission_route = [start_pin_pos, start_straight_pos, start_corner_pos,
                                          start_transmission_boundary_pos, end_transmission_boundary_pos,
                                          end_corner_pos, end_straight_pos, end_pin_pos]

                    transmission_name = "transmission_lines_{}_{}".format(d, math.floor(i / 2))
                    transmission_lines[transmission_name].name = transmission_name
                    transmission_lines[transmission_name].pos = transmission_route
        elif (d == 'left'):
            for i in range(len(transmission_indices[d])):
                start_pin_pos = start_pin_point['left'][i]
                start_straight_pos = start_straight_point['left'][i]
                start_transmission_boundary_pos = transmission_boundary_point['left'][i]
                end_pin_pos = start_pin_point['right'][i]
                end_straight_pos = start_straight_point['right'][i]
                end_transmission_boundary_pos = transmission_boundary_point['right'][i]

                transmission_route = [start_pin_pos, start_straight_pos, start_transmission_boundary_pos,
                                      end_transmission_boundary_pos, end_straight_pos, end_pin_pos]

                transmission_name = "transmission_lines_side_{}".format(i)
                transmission_lines[transmission_name].name = transmission_name
                transmission_lines[transmission_name].pos = transmission_route
    return copy.deepcopy(transmission_lines)