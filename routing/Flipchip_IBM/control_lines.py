#########################################################################
# File Name: control_lines.py
# Description: Module for generating control lines.
#              Includes functions for calculating control line coordinates and generating control lines.
#########################################################################

from addict import Dict
import numpy as np
import math
from scipy.spatial import KDTree
import matplotlib.pyplot as plt
import networkx as nx
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
    """
    topo_poss = copy.deepcopy(topo_poss)
    old_poss = []

    for q_name, q_topo_pos in topo_poss.items():
        old_poss.append(q_topo_pos)

    return copy.deepcopy(old_poss)


# Calculate the number of qubits assigned to upper, lower, left, and right control lines
def count_points_in_quadrants(topo_poss, pins):
    ################################## Interface ##################################
    topo_poss = copy.deepcopy(topo_poss)
    pins = copy.deepcopy(pins)

    # import toolbox
    # toolbox.show_options(topo_poss)
    # toolbox.show_options(pins)

    # Add required parameters

    ##########################################################################
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
    upper_num += (sum(1 for x, y in positions if y == max([y for x, y in positions])) - sum(
        1 for x, y in positions if y == (max([y for x, y in positions]) - 1)))
    left_num = right_num = int((num - upper_num - lower_num) / 2)
    return upper_num, lower_num, left_num, right_num


# Calculate the path coordinate set for each qubit within the given topology
def calculate_path_pos(topo_poss, qubits):
    """
    Calculate the available path coordinate set for each qubit in the given topology.

    Args:
        topo_poss: Dictionary representing the qubit topology.
        qubits: Dictionary representing the qubit information.

    Returns:
        path_pos: List containing the path coordinate set for each qubit.
    """
    topo_poss = copy.deepcopy(topo_poss)
    qubits = copy.deepcopy(qubits)
    positions = convert_topo(topo_poss)
    num = len(positions)
    path_pos = [[] for _ in range(num)]
    count = 0
    for qubit in qubits.keys():
        qubit_name = qubit
        left_pos = min([x for x, y in qubits[qubit_name].outline])
        upper_pos = max([y for x, y in qubits[qubit_name].outline])
        right_pos = max([x for x, y in qubits[qubit_name].outline])
        lower_pos = min([y for x, y in qubits[qubit_name].outline])
        x_step = y_step = 50
        forbid_pos_x = qubits[qubit_name].coupling_pins.top[0]
        forbid_pos_y = qubits[qubit_name].coupling_pins.left[1]
        for i in np.arange(left_pos, right_pos, x_step):
            for j in np.arange(lower_pos, upper_pos, y_step):
                if ((i < (forbid_pos_x - x_step / 2) or i > (forbid_pos_x + x_step / 2)) and
                        (j < (forbid_pos_y - y_step / 2) or j > (forbid_pos_y + y_step / 2))):
                    path_pos[count].append([i, j])
        count += 1
    return path_pos


# Calculate the starting coordinate of the control line pins
def calculate_launch_pad_pos(pins):
    """
    Calculate the starting coordinates of the control line pins.

    Args:
        pins: Dictionary containing the control line pin information.

    Returns:
        init_pos: Dictionary containing the starting coordinates of the pins in different directions.
        pad_pos: Dictionary containing the adjusted coordinates of the pins in different directions.
    """
    pins = copy.deepcopy(pins)
    pad_pos = Dict()
    init_pos = Dict()
    pad_pos["upper"] = []
    pad_pos["lower"] = []
    pad_pos["left"] = []
    pad_pos["right"] = []
    init_pos["upper"] = []
    init_pos["lower"] = []
    init_pos["left"] = []
    init_pos["right"] = []

    for pad in pins:
        if re.match(r'^pin_upper_controlline_\d', pad):
            pos = pins[pad].pos
            init_pos["upper"].append(pos)
            pos = [pos[0], pos[1] - pins[pad].start_straight]
            pad_pos["upper"].append(pos)
        elif re.match(r'^pin_lower_controlline_\d', pad):
            pos = pins[pad].pos
            init_pos["lower"].append(pos)
            pos = [pos[0], pos[1] + pins[pad].start_straight]
            pad_pos["lower"].append(pos)
        elif re.match(r'^pin_left_controlline_\d', pad):
            pos = pins[pad].pos
            init_pos["left"].append(pos)
            pos = [pos[0] + pins[pad].start_straight, pos[1]]
            pad_pos["left"].append(pos)
        elif re.match(r'^pin_right_controlline_\d', pad):
            pos = pins[pad].pos
            init_pos["right"].append(pos)
            pos = [pos[0] - pins[pad].start_straight, pos[1]]
            pad_pos["right"].append(pos)
    return init_pos, pad_pos


# Calculate the control and readout position coordinates for each qubit
def calculate_qubit_control_pos(topo_poss, qubits):
    """
    Calculate the control and readout position coordinates for each qubit.

    Args:
        topo_poss: Dictionary representing the qubit topology.
        qubits: Dictionary representing the qubit information.

    Returns:
        control_pos: Dictionary containing the control position coordinates for each qubit.
    """
    control_pos = Dict()
    positions = convert_topo(topo_poss)
    topology_pos_x = max([x for x, y in positions])
    topology_pos_y = max([y for x, y in positions])
    for qubit in qubits:
        i = qubits[qubit].topo_pos[0]
        j = qubits[qubit].topo_pos[1]
        if (i > j and i + j > topology_pos_x and i > (topology_pos_x + 1) / 2):
            control_pos[i][j] = qubits[qubit].control_pins[0]
        else:
            if (i < topology_pos_x / 2 and j < topology_pos_y / 2):
                control_pos[i][j] = qubits[qubit].control_pins[3]
            elif (i < topology_pos_x / 2 and j >= topology_pos_y / 2):
                control_pos[i][j] = qubits[qubit].control_pins[1]
            elif (i >= topology_pos_x / 2 and j < topology_pos_y / 2):
                control_pos[i][j] = qubits[qubit].control_pins[3]
            else:
                control_pos[i][j] = qubits[qubit].control_pins[1]
    return control_pos


# Find the shortest disjoint paths in the given graph
def find_disjoint_paths(G, start_to_end):
    """
    Find the shortest disjoint paths in the given graph.

    Args:
        G: Network graph object.
        start_to_end: List containing tuples of start and end points.

    Returns:
        paths: List containing all found disjoint paths.
    """
    paths = []
    for start, end in start_to_end:
        G_temp = copy.deepcopy(G)
        for path in paths:
            G_temp.remove_nodes_from(path)
        other_points = []
        for x, y in start_to_end:
            if x != start and y != end:
                other_points.append(x)
                other_points.append(y)
        other_points = list(set(other_points))
        G_temp.remove_nodes_from(other_points)
        try:
            path = nx.astar_path(G_temp, source=start, target=end)
            paths.append(path)
        except nx.NetworkXNoPath:
            paths.append([])

    return paths


# Calculate the Euclidean distance between two points
def calculate_distance(point1, point2):
    """
    Calculate the Euclidean distance between two points.

    Args:
        point1: Tuple representing the first point's coordinates.
        point2: Tuple representing the second point's coordinates.

    Returns:
        distance: Float representing the distance between the two points.
    """
    x1, y1 = point1
    x2, y2 = point2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


# Find the extreme points in the given point set
def find_extreme_points(points):
    """
    Find the extreme points in the given point set.

    Args:
        points: List containing multiple coordinate points.

    Returns:
        min_x_points, max_x_points, min_y_points, max_y_points: Four lists containing the points with the minimum and maximum x and y coordinates.
    """
    if not points:
        return [], [], [], []
    min_x_points = []
    max_x_points = []
    min_y_points = []
    max_y_points = []

    for point in points:
        y = point[1]
        row_points = [p for p in points if p[1] == y]
        min_x = float('inf')  # Initial value set to positive infinity
        max_x = float('-inf')  # Initial value set to negative infinity

        for row_point in row_points:
            x = row_point[0]  # Get the x-coordinate
            if x < min_x:
                min_x = x
            if x > max_x:
                max_x = x
        min_pos = [p for p in row_points if p[0] == min_x]
        max_pos = [p for p in row_points if p[0] == max_x]
        min_x_points.append(min_pos[0])
        max_x_points.append(max_pos[0])

    for point in points:
        x = point[0]
        column_points = [p for p in points if p[0] == x]
        min_y = float('inf')  # Initial value set to positive infinity
        max_y = float('-inf')  # Initial value set to negative infinity

        for column_point in column_points:
            y = column_point[1]  # Get the y-coordinate
            if y < min_y:
                min_y = y
            if y > max_y:
                max_y = y
        min_pos = [p for p in column_points if p[1] == min_y]
        max_pos = [p for p in column_points if p[1] == max_y]
        min_y_points.append(min_pos[0])
        max_y_points.append(max_pos[0])

    min_x_points = list(set(min_x_points))
    max_x_points = list(set(max_x_points))
    min_y_points = list(set(min_y_points))
    max_y_points = list(set(max_y_points))

    min_x_points = sorted(min_x_points, key=lambda x: x[1])
    max_x_points = sorted(max_x_points, key=lambda x: x[1])
    min_y_points = sorted(min_y_points, key=lambda x: x[0])
    max_y_points = sorted(max_y_points, key=lambda x: x[0])

    return min_x_points, max_x_points, min_y_points, max_y_points


# Find the closest point in the given point set to the target point
def find_closest_point(left_points, end_pos):
    """
    Find the closest point in the given point set to the target point.

    Args:
        left_points: List containing multiple coordinate points.
        end_pos: Tuple representing the target point's coordinates.

    Returns:
        closest_point_index: Integer representing the index of the closest point.
    """
    closest_point_index = None
    min_distance = float('inf')

    for index, point in enumerate(left_points):
        distance = abs(point[1] - end_pos[1])
        if distance < min_distance:
            min_distance = distance
            closest_point_index = index

    return closest_point_index


def create_network(init_pos, pad_pos, control_pos, path_pos, topo_poss, pins):
    """
    Create a network graph for qubit control lines and establish connections.

    Args:
        init_pos: Dictionary containing the starting coordinates of the pins in different directions.
        pad_pos: Dictionary containing the adjusted coordinates of the pins in different directions.
        control_pos: Dictionary containing the control position coordinates for each qubit.
        path_pos: List containing the path coordinate set for each qubit.
        topo_poss: Dictionary representing the qubit topology.
        pins: Dictionary containing the control line pin information.

    Returns:
        G: Network graph object.
        start_points: List containing the starting coordinates.
        end_points: List containing the ending coordinates.
        paths: List containing all found paths.
    """
    start_points = []
    init_points = []
    end_points = []
    way_points = []
    all_points = []

    for init_poses in init_pos.values():
        for init_point in init_poses:
            init_points.append(init_point)
    init_points = [tuple(coord) for coord in init_points]

    for start_poses in pad_pos.values():
        for start_point in start_poses:
            start_points.append(start_point)
    start_points = [tuple(coord) for coord in start_points]

    for subdict in control_pos.values():
        for end_point in subdict.values():
            end_points.append((end_point))
    end_points = [tuple(coord) for coord in end_points]

    for path in path_pos:
        for point in path:
            way_points.append(point)
    way_points = [tuple(coord) for coord in way_points]

    all_points.extend(init_points)
    all_points.extend(start_points)
    all_points.extend(end_points)
    all_points.extend(way_points)

    G = nx.Graph()

    for point in all_points:
        G.add_node(tuple(point))

    # Add connections for the first segment length of the pins
    for i in range(len(init_points)):
        G.add_edge(init_points[i], start_points[i])

    # Get the topology boundary values
    positions = convert_topo(topo_poss)
    topology_pos_x = max([x for x, y in positions])
    topology_pos_y = max([y for x, y in positions])

    way_points_tmp = copy.deepcopy(way_points)

    selected_points = []
    for point in way_points_tmp:
        y = point[1]
        row_points = [p for p in way_points_tmp if p[1] == y]
        min_x = float('inf')  # Initial value set to positive infinity
        max_x = float('-inf')  # Initial value set to negative infinity

        for row_point in row_points:
            x = row_point[0]  # Get the x-coordinate
            if x < min_x:
                min_x = x
            if x > max_x:
                max_x = x
        min_pos = [p for p in row_points if p[0] == min_x]
        max_pos = [p for p in row_points if p[0] == max_x]
        selected_points.append(min_pos[0])
        selected_points.append(max_pos[0])

    for point in way_points_tmp:
        x = point[0]
        column_points = [p for p in way_points_tmp if p[0] == x]
        min_y = float('inf')  # Initial value set to positive infinity
        max_y = float('-inf')  # Initial value set to negative infinity

        for column_point in column_points:
            y = column_point[1]  # Get the y-coordinate
            if y < min_y:
                min_y = y
            if y > max_y:
                max_y = y
        min_pos = [p for p in column_points if p[1] == min_y]
        max_pos = [p for p in column_points if p[1] == max_y]
        selected_points.append(min_pos[0])
        selected_points.append(max_pos[0])

    selected_points = list(set(selected_points))

    matches = []

    selected_coordinates = np.array(selected_points)
    way_coordinates = np.array(way_points)

    corners = []  # Four corner coordinates

    # Find the top-left and bottom-right points
    leftmost_topmost = min(way_points_tmp, key=lambda point: point[0] + point[1])
    rightmost_bottommost = max(way_points_tmp, key=lambda point: point[0] + point[1])
    corners.append(leftmost_topmost)
    corners.append(rightmost_bottommost)

    # Find the bottom-left and top-right points
    leftmost_bottommost = min(way_points_tmp, key=lambda point: point[0] - point[1])
    rightmost_topmost = max(way_points_tmp, key=lambda point: point[0] - point[1])
    corners.append(leftmost_bottommost)
    corners.append(rightmost_topmost)

    inner_points = [point for point in way_coordinates if tuple(point) not in selected_points]
    inner_points = [point for point in inner_points if not np.array_equal(point, corners[0])
                    and not np.array_equal(point, corners[1])
                    and not np.array_equal(point, corners[2])
                    and not np.array_equal(point, corners[3])]

    # Connect each selected point to its nearest inner point
    for selected_point in selected_points:
        min_distance = float('inf')
        nearest_point = None

        for inner_point in inner_points:
            distance = calculate_distance(selected_point, inner_point)
            if distance < min_distance:
                min_distance = distance
                nearest_point = inner_point

        matches.append((selected_point, nearest_point))
        G.add_edge(tuple(selected_point), tuple(nearest_point))

    # Sort by x-coordinate in ascending order
    sorted_by_x = sorted(way_points, key=lambda point: (point[0], point[1]))

    # Sort by y-coordinate in ascending order
    sorted_by_y = sorted(way_points, key=lambda point: (point[1], point[0]))

    # Establish connections between nodes with the same x-coordinate
    for i in range(len(sorted_by_x) - 1):
        if sorted_by_x[i][0] == sorted_by_x[i + 1][0]:
            matches.append((sorted_by_x[i], sorted_by_x[i + 1]))
            G.add_edge(tuple(sorted_by_x[i]), tuple(sorted_by_x[i + 1]))

    # Establish connections between nodes with the same y-coordinate
    for i in range(len(sorted_by_y) - 1):
        if sorted_by_y[i][1] == sorted_by_y[i + 1][1]:
            matches.append((sorted_by_y[i], sorted_by_y[i + 1]))
            G.add_edge(tuple(sorted_by_y[i]), tuple(sorted_by_y[i + 1]))

    for end_point in end_points:
        max_second_value = float('-inf')
        for first_key, second_dict in control_pos.items():
            if end_point[0] in [value[0] for value in second_dict.values()]:
                for second_key, value in second_dict.items():
                    if value[0] == end_point[0] and second_key > max_second_value:
                        max_second_value = second_key
        closest_x = None
        min_x_distance = float('inf')
        for way_point in way_points:
            if abs(way_point[0] - end_point[0]) < min_x_distance:
                closest_x = way_point[0]
                min_x_distance = abs(way_point[0] - end_point[0])
        same_x_points = [point for point in way_points if point[0] == closest_x]

        same_x_points.sort(key=lambda point: math.sqrt((end_point[0] - point[0]) ** 2 + (end_point[1] - point[1]) ** 2))
        same_x_points = same_x_points[:int(len(same_x_points) / (max_second_value + 1))]
        for same_x_point in same_x_points:
            matches.append((end_point, same_x_point))
            G.add_edge(tuple(end_point), tuple(same_x_point))

    start_to_end = []
    upper_num, lower_num, left_num, right_num = count_points_in_quadrants(topo_poss, pins)

    paths = []

    left_points, right_points, lower_points, upper_points = find_extreme_points(selected_points)

    lower_count = 0
    for i in range(topology_pos_x + 1):
        count = 0
        for j in range(topology_pos_y, -1, -1):
            if (i >= j and i + j <= topology_pos_x and j <= (topology_pos_x + 1) / 2 and lower_count < lower_num):
                init_start_pos = tuple(init_pos['lower'][lower_count])
                start_pos = tuple(pad_pos['lower'][lower_count])
                end_pos = tuple(control_pos[i][j])
                start_to_end.append([init_start_pos, end_pos])
                lower_count += 1

                index = int(i * len(lower_points) / (topology_pos_x + 1))
                G.add_edge(start_pos, tuple(lower_points[index + count]))
                count += 1

    upper_count = 0
    for i in range(topology_pos_x + 1):
        count = 0
        for j in range(topology_pos_y + 1):
            if (i <= j and i + j >= topology_pos_y and j >= (topology_pos_x + 1) / 2 and upper_count < upper_num):
                if (j == topology_pos_y and i + 1 > sum(
                        1 for x, y in positions if y == max([y for x, y in positions]))):
                    break
                init_start_pos = tuple(init_pos['upper'][upper_count])
                start_pos = tuple(pad_pos['upper'][upper_count])
                end_pos = tuple(control_pos[i][j])
                if [start_pos, end_pos] not in start_to_end:
                    start_to_end.append([init_start_pos, end_pos])
                    upper_count += 1

                index = int(i * len(upper_points) / (topology_pos_x + 1))
                G.add_edge(start_pos, tuple(upper_points[index + count]))
                count += 1

    left_count = left_num - 1
    for j in range(topology_pos_y + 1):
        count = 1
        for i in range(topology_pos_x + 1):
            if (i < j and i + j < topology_pos_x and i < (topology_pos_x + 1) / 2 and left_count >= 0):
                init_start_pos = tuple(init_pos['left'][left_count])
                start_pos = tuple(pad_pos['left'][left_count])
                end_pos = tuple(control_pos[i][j])
                start_to_end.append([init_start_pos, end_pos])
                left_count -= 1

                index = find_closest_point(left_points, end_pos)
                G.add_edge(start_pos, left_points[index + count])
                count += 1

    right_count = right_num - 1
    for j in range(topology_pos_y + 1):
        count = 0
        for i in range(topology_pos_x, -1, -1):
            if (i > j and i + j > topology_pos_x and i > (topology_pos_x + 1) / 2 and right_count >= 0):
                init_start_pos = tuple(init_pos['right'][right_count])
                start_pos = tuple(pad_pos['right'][right_count])
                end_pos = tuple(control_pos[i][j])
                start_to_end.append([init_start_pos, end_pos])
                right_count -= 1

                index = find_closest_point(right_points, end_pos)
                G.add_edge(start_pos, right_points[index + count])
                count += 1

    paths.extend(find_disjoint_paths(G, start_to_end))

    return G, start_points, end_points, paths


def generate_ctls(qubits_ops, pins_ops, chip_name, ctls_type):
    """
    Main function to generate control lines.

    Args:
        qubits_ops: Dictionary containing qubit operation information.
        pins_ops: Dictionary containing pin information.
        chip_name: String specifying the chip name.
        ctls_type: String specifying the control line type.

    Returns:
        ctls_ops: Dictionary containing the generated control line operations.
    """
    print("Flipchip_routing_IBM generating control lines...")
    ############################# Interface #############################

    topo_poss = Dict()
    for q_name, q_ops in qubits_ops.items():
        topo_poss[q_name] = copy.deepcopy(q_ops.topo_pos)

    qubits = copy.deepcopy(qubits_ops)
    qubits = convert_qubits_format(qubits)
    qubits = aj_control_pins(qubits)

    pins = copy.deepcopy(pins_ops)

    control_lines = Dict()

    # Add any required parameters

    ################################################################
    ############################## Input Check ###########################
    # Check qubit height
    for k, v in qubits.items():
        maxy = v.outline[0][1]
        miny = maxy
        for pos in v.outline:
            maxy = max(maxy, pos[1])
            miny = min(miny, pos[1])
        height = maxy - miny
        if height < 470:
            raise ValueError(
                "{} height is insufficient to generate control lines!\n{} height is {} and must be at least {}".format(
                    k, k, height, 470))
        # Check the number of control pins
        if len(v.control_pins) < 4:
            raise ValueError(
                "{} has insufficient control line pins. {} has {} control pins and must have at least {}".format(v.name,
                                                                                                                 len(v.control_pins),
                                                                                                                 len(v.control_pins),
                                                                                                                 4))
    # Check qubit type
    qtype = qubits[list(qubits.keys())[0]].type
    for k, v in qubits.items():
        if v.type != qtype:
            raise ValueError("This routing algorithm requires consistent qubit types.")
    ################################################################

    path_pos = calculate_path_pos(topo_poss, qubits)
    init_pos, pad_pos = calculate_launch_pad_pos(pins)
    control_pos = calculate_qubit_control_pos(topo_poss, qubits)

    G, start_points, end_points, paths = create_network(init_pos, pad_pos, control_pos, path_pos, topo_poss, pins)

    for i in range(len(paths)):
        control_lines["control_lines_{}".format(i)].name = "control_lines_{}".format(i)
        control_lines["control_lines_{}".format(i)].pos = paths[i]

    ctls_ops = copy.deepcopy(control_lines)
    ctls_ops = func_modules.ctls.set_chips(ctls_ops, chip_name)
    ctls_ops = func_modules.ctls.set_types(ctls_ops, ctls_type)
    ctls_ops = func_modules.ctls.soak_ctls(ctls_ops)

    return copy.deepcopy(ctls_ops)


def convert_qubits_format(qubits_ops):
    """
    Convert the qubit format to adapt to the new structure requirements.

    Args:
        qubits_ops: Dictionary containing qubit operation information.

    Returns:
        qubits_ops: Dictionary containing the converted qubit operation information.
    """
    import toolbox
    for q_name, q_ops in qubits_ops.items():
        old_coupling_pins = copy.deepcopy(q_ops.coupling_pins)
        coupling_pins = Dict()
        coupling_pins.right = toolbox.find_rightmost_coordinate(old_coupling_pins)
        coupling_pins.left = toolbox.find_leftmost_coordinate(old_coupling_pins)
        coupling_pins.top = toolbox.find_topmost_coordinate(old_coupling_pins)
        coupling_pins.bot = toolbox.find_botmost_coordinate(old_coupling_pins)
        qubits_ops[q_name].coupling_pins = copy.deepcopy(coupling_pins)
    return copy.deepcopy(qubits_ops)


def aj_control_pins(qubits_ops):
    """
    Check and adjust the control line pins of qubits to ensure each qubit has at least four control pins.

    Args:
        qubits_ops: Dictionary containing qubit operation information.

    Returns:
        qubits_ops: Dictionary containing the adjusted qubit operation information.
    """
    qubits_ops = copy.deepcopy(qubits_ops)
    for q_name, q_ops in qubits_ops.items():
        control_pins = copy.deepcopy(q_ops.control_pins)
        if len(control_pins) >= 4:
            continue
        else:
            control_pins = buman(control_pins)
            qubits_ops[q_name].control_pins = copy.deepcopy(control_pins)
    return copy.deepcopy(qubits_ops)


def buman(l):
    """
    Expand the control line pins to ensure there are at least four pins.

    Args:
        l: List containing control line pins.

    Returns:
        l: List containing the expanded control line pins.
    """
    l = copy.deepcopy(l)
    num = len(l)
    lend = l[num - 1]
    for i in range(num, 4):
        l.append(lend)
    return l