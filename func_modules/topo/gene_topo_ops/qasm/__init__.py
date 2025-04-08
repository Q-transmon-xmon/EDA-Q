from func_modules.topo.gene_topo_ops.qasm import qasm_to_topo
import copy
from addict import Dict


def qasm(qasm_path, 
         row,
         col,
         matrix_path,
         topo_convergence_path,
         qubit_layout_path,
         topo_pruning_path,
         final_topo_path):
    
    topo_ops = qasm_to_topo.qasm_to_topo(qasm_path,
                                         row,
                                         col, 
                                         matrix_path,
                                         topo_convergence_path,
                                         qubit_layout_path,
                                         topo_pruning_path,
                                         final_topo_path)

    return copy.deepcopy(topo_ops)