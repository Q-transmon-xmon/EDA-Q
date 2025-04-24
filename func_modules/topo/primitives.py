############################################################################################
# Parameters related to topology processing
############################################################################################

from addict import Dict
import toolbox
import copy, math
import random

def generate_topo_positions(qubits_num, topo_col: int = None, topo_row: int = None):
    """Generate topology coordinates based on qubits_num
    
    Input:
        qubits_num: the number of qubits
        topo_col: the number of columns in the topology structure (optional)
        topo_row: the number of rows in the topology structure (optional)

    Output:
        topology_pos: the topology coordinates
    """
    # When the number of rows and columns is not specified, try to use a square matrix as much as possible
    if topo_col is None and topo_row is None:
        topo_col = math.ceil(math.sqrt(qubits_num))
        topo_row = math.ceil(qubits_num/topo_col)
        print("未指定拓扑的行列数，默认col = {}, row = {}".format(topo_col, topo_row))
    elif topo_col is None:
        topo_col = math.ceil(qubits_num/topo_row)
        print("计算得topo_col = {}".format(topo_col))
    elif topo_row is None:
        topo_row = math.ceil(qubits_num/topo_col)
        print("计算得topo_row = {}".format(topo_row))
    else:
        if topo_col*topo_row < qubits_num:
            raise ValueError("拓扑的行列数不足以容纳量子比特：\n \
                             qubits_num = {}, topo_col = {}, topo_row = {}".format(qubits_num, topo_col, topo_row))

    # Generate coordinates
    positions = Dict()
    idx = 0
    for y in range(topo_row):
        for x in range(topo_col):
            positions["q"+str(idx)] = (x, y)
            idx += 1
            if idx == qubits_num:
                break

    return copy.deepcopy(positions)

def generate_topo_positions_col_row(qubits_num, topo_col: int = None, topo_row: int = None):
    """Generate topology coordinates based on qubits_num
    
    Input:
        qubits_num: the number of qubits
        topo_col: the number of columns in the topology structure (optional)
        topo_row: the number of rows in the topology structure (optional)

    Output:
        topology_pos: the topology coordinates
    """

    # When the number of rows and columns is not specified, try to use a square matrix as much as possible
    if topo_col is None and topo_row is None:
        topo_col = math.ceil(math.sqrt(qubits_num))
        topo_row = math.ceil(qubits_num/topo_col)
        print("未指定拓扑的行列数，默认col = {}, row = {}".format(topo_col, topo_row))
    elif topo_col is None:
        topo_col = math.ceil(qubits_num/topo_row)
        print("计算得topo_col = {}".format(topo_col))
    elif topo_row is None:
        topo_row = math.ceil(qubits_num/topo_col)
        print("计算得topo_row = {}".format(topo_row))
    else:
        if topo_col*topo_row < qubits_num:
            raise ValueError("拓扑的行列数不足以容纳量子比特：\n \
                             qubits_num = {}, topo_col = {}, topo_row = {}".format(qubits_num, topo_col, topo_row))

    # Generate coordinates
    positions = Dict()
    idx = 0
    for y in range(topo_row):
        for x in range(topo_col):
            positions["q"+str(idx)] = (x, y)
            idx += 1
            if idx == qubits_num:
                break

    return copy.deepcopy(positions), topo_col, topo_row

def generate_full_edges(positions):
    """
    Generate a complete set of edges for the given topology coordinates.

    Input:
        positions: A dictionary of qubit positions with qubit names as keys and (x, y) tuples as values.

    Output:
        edges: A list of lists, where each inner list contains two qubit names representing an edge between them.
    """
    positions = Dict(positions)
    edges = []
    qubits = list(positions.keys())
    for i in range(0, len(qubits)):
        for j in range(i + 1, len(qubits)):
            topo_pos_i = positions[qubits[i]]
            topo_pos_j = positions[qubits[j]]
            if (abs(topo_pos_i[0] - topo_pos_j[0]) + abs(topo_pos_i[1] - topo_pos_j[1])) == 1:
                edges.append([qubits[i], qubits[j]])
    
    return copy.deepcopy(edges)

def generate_random_edges(positions, edges_num: int = None):
    """
    Randomly generate a specified number of edges for the given topology coordinates.

    Input:
        positions: A dictionary of qubit positions with qubit names as keys and (x, y) tuples as values.
        edges_num: The number of edges to randomly generate. If None, a random number between 1 and the maximum number of possible edges will be chosen.

    Output:
        edges: A list of randomly selected edges, where each edge is a list containing two qubit names.
    """
    full_edges = generate_full_edges(positions)
    max_edges_num = len(full_edges)
    if edges_num is None:
        edges_num = random.randint(1, max_edges_num)
    print("随机生成拓扑边的数量是{}...".format(edges_num))
    # outlier detection
    if edges_num > max_edges_num:
        print("设置的边太多，自动降为能容纳边数的最大值: {}".format(max_edges_num))
        edges_num = max_edges_num
    # take a sample
    edges = random.sample(full_edges, edges_num)
    return copy.deepcopy(edges)

def to_random_edges_full_connected(topo_poss):
    """
    Randomly generate topology edges based on the given topology coordinates to ensure the final topology is a connected graph.

    Input:
        topo_poss: Topology coordinates

    Output:
        topo_edges: Topology edges
    """

    # Reminder information
    print("随机生成拓扑边（连通图）...")

    # Call method to generate connected topological edges
    topo_edges = toolbox.generate_connected_edges(topo_poss)

    return copy.deepcopy(topo_edges)

def cp_lines_update_topo_edges(coupling_lines, topo_edges):
    """
    Update topology edge information based on coupling line parameters.

    Input:
        coupling_lines: Coupling line parameters
        topo_edges: Topology edge information

    Output:
        new_topo_edges: Updated topology edge information
    """

    # interface
    coupling_lines = copy.deepcopy(coupling_lines)
    topo_edges = copy.deepcopy(topo_edges)

    # New topological edge
    new_topo_edges = []
    for cp_name, cp_op in coupling_lines.items():
        new_topo_edges.append(cp_op.qubits)

    # Update new topology edges
    for edge in new_topo_edges:
        if edge not in topo_edges:
            print("自动删除边{}...".format(edge))

    return copy.deepcopy(new_topo_edges)

import math

def generate_hex_pos(num):
    """
    Generate a set of hexagonal coordinates and return them in dictionary format.
    Each hexagon's coordinates form a regular hexagon shape, with multiple hexagons joined together.

    Input:
    num: The number of hexagons

    Return:
    positions: A dictionary where each key is 'q' followed by the index, and the value is the corresponding coordinate tuple (x, y)
    """
    length = 1    # Distance between nodes
    positions = Dict()

    if num == 0:
        raise ValueError("num不能为0")
    
    if not isinstance(num, int):
        raise ValueError("num必须是整数")
    
    if num < 0:
        raise ValueError("num必须大于0")
    
    if num > 7:
        raise ValueError("num现在不能大于7")
    
    # The center point of a hexagon
    base_poses = [(0, 0)]
    base_poses += list(
            (1*math.sqrt(3)*math.cos(angle*math.pi/180), 1*math.sqrt(3)*math.sin(angle*math.pi/180)) for angle in range(0, 361, 60))
    # Relative to the center point，Node perspective
    angles = [(i*60+30)*math.pi/180 for i in range(6)]
    
    qubits_idx = 0    # Node number
    base_pos_idx = 0    # Center point number
    while 1:
        if num == 0:
            break

        base_pos = copy.deepcopy(base_poses[base_pos_idx])
        
        for angle in angles:
            pos = (base_pos[0]+length*math.cos(angle), base_pos[1]+length*math.sin(angle))
            if not panduan_shifou_yijingyou_zhege_dian(positions, pos):
                positions["q{}".format(qubits_idx)] = copy.deepcopy(pos)
                qubits_idx += 1

        num -= 1
        base_pos_idx += 1

    

    # kuozhan_idx = 0
    
    # def kuozhan_base_pos():
    #     kuozhan_idx += 1
    #     return
    
    return positions

def panduan_shifou_yijingyou_zhege_dian(positions, pos):
    for qname, qpos in positions.items():
        if are_coordinates_coincident(pos, qpos):
            return True
    return False

def are_coordinates_coincident(coord1, coord2, tolerance=1e-9):
    """
    Determine if two floating-point coordinates coincide.

    :param coord1: The first coordinate tuple (x1, y1)
    :param coord2: The second coordinate tuple (x2, y2)
    :param tolerance: The tolerance error for determining if floating-point numbers are equal, default is 1e-9
    :return: Returns True if the coordinates coincide, otherwise returns False
    """
    return (math.isclose(coord1[0], coord2[0], abs_tol=tolerance) and
            math.isclose(coord1[1], coord2[1], abs_tol=tolerance))

def generate_hex_full_edges(positions):
    """
    Generate a full set of edges for the given hexagonal coordinates.

    Input:
        positions: Dictionary of hexagonal coordinates

    Output:
        edges: List of edges connecting the hexagonal coordinates
    """
    positions = copy.deepcopy(positions)
    
    edges = []
    for q in positions.keys():
        for qq in positions.keys():
            # Determine if they are the same point
            if q == qq:
                continue
            # Determine if the distance is1
            dist = calculate_distance(positions[q], positions[qq])
            if not are_floats_equal(1, dist):
                continue
            # Determine if this edge already exists
            if panduan_shifou_you_zhege_bian(edges, [q, qq]):
                continue
            edges.append([q, qq])
    return edges

def panduan_shifou_you_zhege_bian(edges, edge):
    """
    Determine if a specific edge already exists in the list of edges.

    Input:
        edges: List of existing edges
        edge: Edge to check for existence

    Output:
        True if the edge exists, False otherwise
    """
    for e in edges:
        ee = [e[1], e[0]]
        if e == edge or ee == edge:
            return True
    return False

def calculate_distance(coord1, coord2):
    """
    Calculate the Euclidean distance between two 2D coordinates.

    Parameters:
    coord1 -- The first coordinate, a tuple or list with two elements (x1, y1)
    coord2 -- The second coordinate, a tuple or list with two elements (x2, y2)

    Returns:
    The floating-point distance between the two coordinates.
    """
    x1 = coord1[0]
    y1 = coord1[1]
    x2, y2 = coord2[0], coord2[1]
    
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return distance

def are_floats_equal(a, b, rel_tol=1e-09, abs_tol=0.0):
    """
    Determine if two floating-point numbers can be considered equal.

    Parameters:
    a -- The first floating-point number
    b -- The second floating-point number
    rel_tol -- Relative tolerance, default is 1e-09
    abs_tol -- Absolute tolerance, default is 0.0

    Returns:
    True if the two floating-point numbers are within the given tolerance range, otherwise False.
    """
    return math.isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol)