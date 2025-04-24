import os
import copy
import toolbox

from func_modules.topo import gene_topo_ops
from func_modules.topo import primitives

############################################################################################
# Parameter processing related to topology
############################################################################################
from addict import Dict

def generate_topo_positions(qubits_num, topo_col: int = None, topo_row: int = None):
    topo_positions = primitives.generate_topo_positions(qubits_num=qubits_num, topo_col=topo_col, topo_row=topo_row)
    return copy.deepcopy(topo_positions)

def generate_random_edges(positions, edges_num):
    topo_edges = primitives.generate_random_edges(positions=positions, edges_num=edges_num)
    return copy.deepcopy(topo_edges)

def generate_topology(**gene_ops):
    return copy.deepcopy(gene_topo_ops.gene_topo_ops(**gene_ops))

def extract_topo_positions_from_qubits_ops(qubits_ops):
    topo_positions = Dict()
    for q_name, q_ops in qubits_ops.items():
        topo_positions[q_name] = copy.deepcopy(q_ops.topo_pos)
    return copy.deepcopy(topo_positions)

def generate_hex_full_edges(positions):
    return primitives.generate_hex_full_edges(positions)