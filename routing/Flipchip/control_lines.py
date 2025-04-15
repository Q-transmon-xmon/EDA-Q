#########################################################################
# File Name: control_lines.py
# Description: Module for generating control lines.
#              Includes functions for calculating control line coordinates and generating control lines.
#########################################################################

from addict import Dict
from collections import defaultdict
import math
import re
import copy
import func_modules

gap = 100


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
        qubit_name = func_modules.qubits.find_qname_from_rdl_ops(rdl_ops=line_info, qubits_ops=qubits)
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
        qubit_name = func_modules.qubits.find_qname_from_rdl_ops(rdl_ops=line_info, qubits_ops=qubits)
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


# Create an alternating sequence
def create_alternate_list(m):
    """
    Create an alternating sequence.

    Args:
        m: Integer, sequence length.

    Returns:
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
    Calculate the number of pins in each section.

    Args:
        m: Integer, number of rows.
        n: Integer, number of columns.

    Returns:
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
                'upper': list(reversed(range(m - 1, m - top_rows - 1, -1))),
                'lower': list(reversed(range(bottom_rows))),
                'sides': list(reversed(range(bottom_rows, m - top_rows)))
            }
        if (top_pins + bottom_pins + left_pins + right_pins != total_pins):
            right_pins += 1

    # print("Rows with pins at the top:", row_distribution['upper'])
    # print("Rows with pins at the bottom:", row_distribution['lower'])
    # print("Rows with pins at the sides:", row_distribution['sides'])

    return top_pins, bottom_pins, left_pins, right_pins, row_distribution


def calculate_corner_points(upper_pins_y, lower_pins_y, left_pins_x, right_pins_x, upper_num, lower_num):
    """
    Calculate the corner points of the diagonal lines.

    Args:
        upper_pins_y: Float, y-coordinate of the upper pins.
        lower_pins_y: Float, y-coordinate of the lower pins.
        left_pins_x: Float, x-coordinate of the left pins.
        right_pins_x: Float, x-coordinate of the right pins.
        upper_num: Integer, number of upper pins.
        lower_num: Integer, number of lower pins.

    Returns:
        ul_points: List, upper left corner points.
        ll_points: List, lower left corner points.
        ur_points: List, upper right corner points.
        lr_points: List, lower right corner points.
    """
    # Define the step size
    delta = gap
    # Upper left corner points
    upper_left_points = [[left_pins_x + delta * (i - 1), upper_pins_y - delta * i]
                         for i in range(math.ceil(upper_num / 2))]
    # Lower left corner points
    lower_left_points = [[left_pins_x + delta * (i - 1) + 300, lower_pins_y + delta * i - 300]
                         for i in range(math.ceil(lower_num / 2))]
    # Upper right corner points
    upper_right_points = [[right_pins_x - delta * (i - 1), upper_pins_y - delta * i]
                          for i in range(math.floor(upper_num / 2))]
    # Lower right corner points
    lower_right_points = [[right_pins_x - delta * (i - 1) - 300, lower_pins_y + delta * i - 300]
                          for i in range(math.floor(lower_num / 2))]
    return upper_left_points, lower_left_points, upper_right_points, lower_right_points


def split_into_segments(indices):
    """
    Split the indices into multiple continuous segments.

    Args:
        indices: List, index list.

    Returns:
        segments: List, segmented list.
    """
    segments = []
    segment_lengths = []  # To store the length of each segment
    current_segment = [indices[0]]

    for i in range(1, len(indices)):
        if indices[i] == indices[i - 1] + 1:
            current_segment.append(indices[i])
        else:
            # Check and possibly split the current segment
            if len(segments) >= 2:
                len1, len2 = segment_lengths[-2], segment_lengths[-1]
                if len(current_segment) == len1 + len2:
                    # Split the current segment and update the list and length records
                    segments.append(current_segment[:len1])
                    segments.append(current_segment[len1:len1 + len2])
                    segment_lengths.append(len1)
                    segment_lengths.append(len2)
                    current_segment = current_segment[len1 + len2:]
                    segment_lengths.append(len(current_segment))
            segments.append(current_segment)
            segment_lengths.append(len(current_segment))
            current_segment = [indices[i]]

    # Check the last segment
    if len(segments) >= 2:
        len1, len2 = segment_lengths[-2], segment_lengths[-1]
        if len(current_segment) == len1 + len2:
            segments.append(current_segment[:len1])
            segments.append(current_segment[len1:len1 + len2])
            segment_lengths.append(len1)
            segment_lengths.append(len2)
            current_segment = current_segment[len1 + len2:]
            segment_lengths.append(len(current_segment))

    # Add the last segment if not empty
    if current_segment:
        segments.append(current_segment)

    # Check and remove empty lists
    segments = [seg for seg in segments if seg]
    if (len(segments) == 1):
        segment = copy.deepcopy(segments[0])
        segments.pop()
        segments.append(segment[:math.ceil(len(segment) / 2)])
        segments.append(segment[math.ceil(len(segment) / 2):])
    if (len(segments) > 2):
        for i in range(1, len(segments) - 1):
            if (len(segments[i]) == len(segments[i - 1]) + len(segments[i + 1])):
                segments.insert(i, segments[i][:len(segments[i + 1])])
                segments.insert(i + 1, segments[i + 1][len(segments[i + 2]):])
                segments.remove(segments[i + 2])

    return segments


def assign_corner_points(control_indices, ul_points, ll_points, ur_points, lr_points, upper_num, lower_num):
    """
    Assign corner points to control lines.

    Args:
        control_indices: Dictionary, control line indices.
        ul_points: List, upper left corner points.
        ll_points: List, lower left corner points.
        ur_points: List, upper right corner points.
        lr_points: List, lower right corner points.
        upper_num: Integer, number of upper pins.
        lower_num: Integer, number of lower pins.

    Returns:
        corner_points: Dictionary, containing corner points.
    """
    corner_points = {'upper': {}, 'lower': {}, 'left': {}, 'right': {}}

    for direction, indices in control_indices.items():
        segments = split_into_segments(indices)
        for segment_index, segment in enumerate(segments):
            for i in segment:
                if direction in ['upper', 'lower']:
                    num = upper_num if direction == 'upper' else lower_num
                    if segment_index % 2 == 0:  # Odd segments
                        corner_points[direction][i] = ul_points[min(i, len(ul_points) - 1)] if direction == 'upper' else \
                        ll_points[min(i, len(ll_points) - 1)]
                    else:  # Even segments
                        corner_points[direction][i] = ur_points[
                            min(num - 1 - i, len(ur_points) - 1)] if direction == 'upper' else lr_points[
                            min(num - 1 - i, len(lr_points) - 1)]

    return corner_points


def find_control_indices(pins, direction):
    """
    Extract all types of pins and their x-coordinates, and find the index of each "control" pin in the sorted type pins.

    Args:
        pins: Dictionary, pin information.
        direction: String, direction.

    Returns:
        direction_control_indices: List, control point indices.
    """
    # Extract all types of pins and their x-coordinates
    direction_pins = {k: v['pos'][0] for k, v in pins.items() if direction in k}
    # Sort these pins by x-coordinate
    sorted_direction_pins = sorted(direction_pins.items(), key=lambda item: item[1])
    # Get the names of "control" type pins
    direction_control_pins = [k for k in direction_pins if direction + '_control' in k]
    # Find the index of each "control" pin in the sorted type pins
    direction_control_indices = [sorted_direction_pins.index((pin, direction_pins[pin])) for pin in
                                 direction_control_pins]

    # Sort the found indices in ascending order
    reordered_indices = sorted(direction_control_indices)

    return reordered_indices


# Rearrange the sequence
def rearrange_segments(control_indices):
    """
    Rearrange the sequence.

    Args:
        control_indices: Dictionary, control line indices.

    Returns:
        control_indices: Dictionary, rearranged control line indices.
    """

    def rearrange_for_upper_lower(segments):
        rearranged = []
        i, j = 0, len(segments) - 1
        while i <= j:
            if i == j:  # When i and j are equal, add only once
                rearranged.extend(segments[i])
            else:
                rearranged.extend(segments[i])
                rearranged.extend(segments[j])
            i += 1
            j -= 1

        return rearranged

    for direction in ['upper', 'lower']:
        segments = split_into_segments(control_indices[direction])
        control_indices[direction] = rearrange_for_upper_lower(segments)

    return control_indices


def calculate_init_point_coordinates(pins, control_indices, direction):
    """
    Calculate the initial length coordinate set.

    Args:
        pins: Dictionary, pin information.
        control_indices: Dictionary, control line indices.
        direction: String, direction.

    Returns:
        coordinates_dict: Dictionary, initial length coordinate set.
    """
    coordinates_dict = {}

    # Get all pin sorting
    all_pins_sorted = sorted([k for k in pins.keys() if direction in k], key=lambda k: pins[k]['pos'][0])

    for index in control_indices:
        # Get the corresponding pin name from the sorted list
        pin_name = all_pins_sorted[index]
        if pin_name in pins:
            x, y = pins[pin_name]['pos']
            coordinates_dict[index] = [x, y]

    return coordinates_dict


# Calculate the initial length coordinate set
def calculate_start_straight_point_coordinates(pins, num, control_indices, direction):
    """
    Calculate the starting straight point coordinates.

    Args:
        pins: Dictionary, pin information.
        num: Integer, number of pins.
        control_indices: Dictionary, control line indices.
        direction: String, direction.

    Returns:
        coordinates_dict: Dictionary, starting straight point coordinates.
    """
    coordinates_dict = {}

    # Get all pin sorting
    all_pins_sorted = sorted([k for k in pins.keys() if direction in k], key=lambda k: pins[k]['pos'][0])

    for index in control_indices:
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

            coordinates_dict[index] = [new_x, new_y]

    return coordinates_dict


def get_qubits_in_line(line, qubits):
    """
    Get the qubits names that match the line number.

    Args:
        line: Integer, line number.
        qubits: Dictionary, qubit operation parameters.

    Returns:
        qubits_in_line: List, qubits names that match the line number.
    """
    # Store qubits names that match the line number
    qubits_in_line = []

    # Iterate through all qubits
    for qubit_name, qubit_info in qubits.items():
        # Check if the qubit's topo_pos y-coordinate matches the given line number
        if qubit_info['topo_pos'][1] == line:
            qubits_in_line.append(qubit_name)

    # Return the list of matching qubit names
    return qubits_in_line


# Create the mapping from pins to qubits
def create_qubits_mapping(control_indices, qubits_indices):
    """
    Create the mapping from pins to qubits.

    Args:
        control_indices: Dictionary, control line indices.
        qubits_indices: Dictionary, qubit indices.

    Returns:
        mapping_indices: Dictionary, mapping from pins to qubits.
    """

    def map_segments_to_qubits(segments, qubits, reverse=False):
        qubit_index = 0
        mapping = {}
        for segment in segments:
            for i in range(len(segment)):
                if reverse:
                    # Reverse mapping
                    mapping[segment[i]] = qubits[qubit_index + len(segment) - 1 - i]
                else:
                    # Forward mapping
                    mapping[segment[i]] = qubits[qubit_index + i]
            qubit_index += len(segment)
        return mapping

    # Process left and right sides
    def map_sides(control_left, control_right, qubits_sides):
        left_segments = split_into_segments(control_left)
        right_segments = split_into_segments(control_right)
        qubit_index = 0
        mapping_left = {}
        mapping_right = {}

        # Alternate mapping for left and right sides, left reverse, right forward
        for i in range(max(len(left_segments), len(right_segments))):
            if i < len(left_segments):
                for j, idx in enumerate(left_segments[i]):
                    mapping_left[idx] = qubits_sides[qubit_index + j]
                qubit_index += len(left_segments[i])

            if i < len(right_segments):
                for j, idx in enumerate(right_segments[i]):
                    mapping_right[idx] = qubits_sides[qubit_index + len(right_segments[i]) - 1 - j]
                qubit_index += len(right_segments[i])

        return mapping_left, mapping_right

    # Segment and map indices for each section
    upper_mapping = map_segments_to_qubits(split_into_segments(control_indices['upper']), qubits_indices['upper'],
                                           reverse=True)
    lower_mapping = map_segments_to_qubits(split_into_segments(control_indices['lower']), qubits_indices['lower'])
    left_mapping, right_mapping = map_sides(control_indices['left'], control_indices['right'], qubits_indices['sides'])

    # Combine all mappings
    final_mapping = {
        'upper': upper_mapping,
        'lower': lower_mapping,
        'left': left_mapping,
        'right': right_mapping
    }
    return final_mapping


# Get control point coordinates
def get_control_pins_coordinates(mapping_indices, qubits):
    """
    Get control point coordinates.

    Args:
        mapping_indices: Dictionary, mapping from pins to qubits.
        qubits: Dictionary, qubit operation parameters.

    Returns:
        control_pins_coordinates: Dictionary, control point coordinates.
    """
    # Initialize a dictionary to hold control pins coordinates
    control_pins_coordinates = {}

    # Iterate over the mapping indices
    for region, mappings in mapping_indices.items():
        region_coordinates = {}
        for index, qubit_id in mappings.items():
            # Find the qubit from qubits data
            qubit = qubits.get(qubit_id)
            # Extract and save the control_pins coordinates
            if qubit and 'control_pins' in qubit:
                region_coordinates[index] = qubit['control_pins'][0]
        # Save the coordinates for the current region
        control_pins_coordinates[region] = region_coordinates

    return control_pins_coordinates


import copy


def get_straight_end_coordinates(control_pins_coordinates):
    """
    Get the straight end coordinates.

    Args:
        control_pins_coordinates: Dictionary, control point coordinates.

    Returns:
        updated_coordinates: Dictionary, updated straight end coordinates.
    """
    updated_coordinates = copy.deepcopy(control_pins_coordinates)

    # Process 'upper' and 'lower' directions
    for direction in ['upper', 'lower']:
        grouped_by_y = {}
        for key, (x, y) in updated_coordinates[direction].items():
            if y not in grouped_by_y:
                grouped_by_y[y] = []
            grouped_by_y[y].append((key, x, y))

        for y, coords in grouped_by_y.items():
            sorted_coords = sorted(coords, key=lambda x: x[1])
            mid_index = len(sorted_coords) // 2

            for i, (key, x, original_y) in enumerate(sorted_coords):
                interval = abs(mid_index - abs(i - mid_index)) + 1
                new_y = original_y - gap * interval
                updated_coordinates[direction][key] = [x, new_y]

    # Create a combined list for 'left' and 'right'
    combined_left_right = []
    for key, (x, y) in updated_coordinates['left'].items():
        combined_left_right.append(('left', key, x, y))
    for key, (x, y) in updated_coordinates['right'].items():
        combined_left_right.append(('right', key, x, y))

    # Group based on y-coordinate values
    grouped_by_y = {}
    for direction, key, x, y in combined_left_right:
        if y not in grouped_by_y:
            grouped_by_y[y] = []
        grouped_by_y[y].append((direction, key, x, y))

    # Update 'left' and 'right' direction coordinates
    for y, coords in grouped_by_y.items():
        sorted_coords = sorted(coords, key=lambda x: x[2])  # Sort by x-coordinate
        mid_index = len(sorted_coords) // 2

        for i, (direction, key, x, original_y) in enumerate(sorted_coords):
            interval = abs(mid_index - abs(i - mid_index)) + 1
            new_y = original_y - gap * interval

            # Update coordinates based on direction
            if direction == 'left':
                updated_coordinates['left'][key] = [x, new_y]
            elif direction == 'right':
                updated_coordinates['right'][key] = [x, new_y]

    return updated_coordinates


# Get boundary coordinates
def get_boundary_end_points(end_straight_points, qubits_left_x, qubits_right_x, n, y_middle):
    """
    Get boundary coordinates.

    Args:
        end_straight_points: Dictionary, straight end coordinates.
        qubits_left_x: Float, leftmost qubit x-coordinate.
        qubits_right_x: Float, rightmost qubit x-coordinate.
        n: Integer, number of pins.
        y_middle: Float, middle y-coordinate.

    Returns:
        updated_points: Dictionary, updated boundary coordinates.
    """
    updated_points = {}

    # Process 'upper' and 'lower'
    for side in ['upper', 'lower']:
        if side in end_straight_points:
            # Split the points into segments based on continuous number sequences
            segments = []
            current_segment = []
            last_num = None

            for num in (end_straight_points[side]):
                if last_num is None or num == last_num + 1:
                    current_segment.append(num)
                else:
                    if current_segment:  # Ensure current_segment is not empty
                        segments.append(current_segment)
                    current_segment = [num]
                last_num = num

            # Handle the last segment
            if current_segment:  # Ensure current_segment is not empty
                # print(current_segment)
                if (len(current_segment) == n):
                    segments.append(current_segment[:math.ceil((n) / 2)])
                    segments.append(current_segment[math.ceil((n) / 2):])
                else:
                    segments.append(current_segment)

            # Assign x-coordinates based on segment number (odd/even)
            # print(side,segments)
            updated_points[side] = {}
            for i, segment in enumerate(segments, start=1):
                x_coord = qubits_left_x if i % 2 != 0 else qubits_right_x
                if (x_coord == qubits_left_x):
                    if (side == 'upper'):
                        counts = 0
                        for num in segment:
                            updated_points[side][num] = [x_coord + 30 * counts, end_straight_points[side][num][1]]
                            counts += 1
                    if (side == 'lower'):
                        counts = 0
                        for num in segment:
                            updated_points[side][num] = [x_coord + 30 * counts, end_straight_points[side][num][1]]
                            counts += 1
                if (x_coord == qubits_right_x):
                    if (side == 'upper'):
                        counts = 0
                        for num in segment:
                            updated_points[side][num] = [x_coord + 30 * counts, end_straight_points[side][num][1]]
                            counts += 1
                    if (side == 'lower'):
                        counts = 0
                        for num in segment:
                            updated_points[side][num] = [x_coord + 30 * counts, end_straight_points[side][num][1]]
                            counts += 1
                            # Process 'left' and 'right'
    # for side in ['left', 'right']:
    #     if side in end_straight_points:
    #         x_coord = qubits_left_x if side == 'left' else qubits_right_x
    #         updated_points[side] = {k: [x_coord, v[1]] for k, v in end_straight_points[side].items()}

    # Create a dictionary to store grouped points
    grouped_points = {}

    # Grouping logic
    for side in ['left', 'right']:
        updated_points[side] = {}
        sorted_points = sorted(end_straight_points[side].items(), key=lambda x: x[1][1])
        group = []
        last_y = None
        for key, value in sorted_points:
            y_coord = value[1]
            if last_y is not None and y_coord - last_y > gap:
                # Start a new group when the y-coordinate difference with the previous point is greater than gap
                if group:
                    grouped_points.setdefault(side, []).append(group)
                    group = []
            group.append((key, value))
            last_y = y_coord
        # Add the last group
        if group:
            grouped_points.setdefault(side, []).append(group)

    # Sort and adjust x_coord based on y_middle
    for side, groups in grouped_points.items():
        for group in groups:
            # Sort by the distance to y_middle
            group.sort(key=lambda x: abs(x[1][1] - y_middle), reverse=True)
            for index, (key, value) in enumerate(group):
                x_coord = qubits_left_x if side == 'left' else qubits_right_x
                # Adjust x_coord based on the index
                x_coord_adjusted = x_coord - 20 * index if side == 'left' else x_coord + 20 * index
                updated_points[side][key] = [x_coord_adjusted, value[1]]
    return updated_points


# Generate control lines
def generate_control_lines(qubits, readout_lines, pins, chip):
    """
    Generate control lines.

    Args:
        qubits: Dictionary, qubit operation parameters.
        readout_lines: Dictionary, readout line operation parameters.
        pins: Dictionary, pin information.
        chip: Dictionary, chip information.

    Returns:
        control_lines: Dictionary, control line information.
    """
    qubits = copy.deepcopy(qubits)
    readout_lines = copy.deepcopy(readout_lines)
    pins = copy.deepcopy(pins)
    chip = copy.deepcopy(chip)

    # import toolbox
    # toolbox.show_options(pins)

    topo_poss = func_modules.topo.extract_topo_positions_from_qubits_ops(qubits)

    # Define control lines
    control_lines = Dict()

    distance_to_chip = 380

    ############################ Input Check ###########################
    if chip == Dict() or chip is None:
        raise ValueError("No chip specified, cannot generate control_lines using this strategy!")

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
    upper_num, lower_num, left_num, right_num, row_distribution = pin_nums(max_y + 1, max_x + 1)
    # print('row_distribution',row_distribution)

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

    # Define the corner points of the diagonal lines
    ul_points, ll_points, ur_points, lr_points = calculate_corner_points(upper_pins_y, lower_pins_y, left_pins_x,
                                                                         right_pins_x, upper_num, lower_num)

    direction = ['upper', 'lower', 'left', 'right']
    num = Dict()
    num['upper'] = upper_num
    num['lower'] = lower_num
    num['left'] = left_num
    num['right'] = right_num

    # Get control line indices
    control_indices = Dict()
    for d in direction:
        control_indices[d] = find_control_indices(pins, d)

    # print(control_indices)
    control_indices = rearrange_segments(control_indices)

    # Get starting position coordinates
    start_pin_points = Dict()
    for d in direction:
        start_pin_points[d] = calculate_init_point_coordinates(pins, control_indices[d], d)

    # print('start_pin_points=',start_pin_points)

    # Get starting length coordinates
    start_straight_points = Dict()
    for d in direction:
        start_straight_points[d] = calculate_start_straight_point_coordinates(pins, num[d], control_indices[d], d)

    # print('start_straight_points',start_straight_points)

    # for d in direction:
    #     print(split_into_segments(control_indices[d]))
    # Get diagonal corner coordinates
    corner_points = assign_corner_points(control_indices, ul_points, ll_points, ur_points, lr_points, upper_num,
                                         lower_num)

    qubits_indices = Dict()
    for d in ['upper', 'lower', 'sides']:
        qubits_indices[d] = []

    for line in row_distribution['upper']:
        qubits_indices['upper'] += get_qubits_in_line(line, qubits)

    for line in row_distribution['lower']:
        qubits_indices['lower'] += get_qubits_in_line(line, qubits)

    for line in row_distribution['sides']:
        qubits_indices['sides'] += get_qubits_in_line(line, qubits)

    mapping_indices = create_qubits_mapping(control_indices, qubits_indices)

    # Example usage of the function
    control_pins_coordinates = get_control_pins_coordinates(mapping_indices, qubits)
    # print('control_pins_coordinates',control_pins_coordinates)

    end_straight_points = get_straight_end_coordinates(control_pins_coordinates)
    # print('end_straight_points',end_straight_points)

    boundary_end_points = get_boundary_end_points(end_straight_points, qubits_left_x[1] - 100, qubits_right_x[0] + 100,
                                                  max_x + 1, (upper_pins_y + lower_pins_y) / 2 - 2000)

    for d in direction:
        for i in control_indices[d]:
            if (d == 'upper' or d == 'lower'):
                pos = [start_pin_points[d][i], start_straight_points[d][i], corner_points[d][i],
                       boundary_end_points[d][i], end_straight_points[d][i], control_pins_coordinates[d][i]]
            else:
                pos = [start_pin_points[d][i], start_straight_points[d][i], boundary_end_points[d][i],
                       end_straight_points[d][i], control_pins_coordinates[d][i]]
            control_lines["control_lines_{}_{}".format(d, i)].name = "control_lines_{}_{}".format(d, i)
            control_lines["control_lines_{}_{}".format(d, i)].pos = pos
            control_lines["control_lines_{}_{}".format(d, i)].type = 'ChargeLine'

    return copy.deepcopy(control_lines)