from addict import Dict
import copy
from base.branch_base import BranchBase
from func_modules.topo import primitives
from func_modules.topo.gene_topo_ops import qasm

def gene_topo_ops(**gene_ops):
    gto = GeneTopoOps(**gene_ops)
    return copy.deepcopy(gto.branch_process())

class GeneTopoOps(BranchBase):
    def qubits_num(self, gene_ops):
        """
        qubits_num
        """
        # interface
        qubits_num = gene_ops.qubits_num

        # Generate coordinates
        options = Dict()
        options.positions, options.col_num, options.row_num = primitives.generate_topo_positions_col_row(qubits_num)
        
        return copy.deepcopy(options)

    def qubits_num__topo_col(self, gene_ops):
        """
        qubits_num, topo_col
        """
        # interface
        qubits_num = gene_ops.qubits_num
        topo_col = gene_ops.topo_col

        # Generate coordinates
        options = Dict()
        options.positions, options.col_num, options.row_num = primitives.generate_topo_positions_col_row(qubits_num, topo_col)

        return copy.deepcopy(options)

    def options(self, gene_ops):
        return copy.deepcopy(gene_ops.options)
    
    def topo_col__topo_row(self, gene_ops):
        # interface
        topo_col = gene_ops.topo_col
        topo_row = gene_ops.topo_row
        qubits_num = topo_col * topo_row

        # Generate coordinates
        options = Dict()
        options.positions, options.col_num, options.row_num = primitives.generate_topo_positions_col_row(qubits_num, topo_col, topo_row)

        return copy.deepcopy(options)
    
    # qasmhave sth. to do with
    def qasm_path(self, gene_ops):
        qasm_path = gene_ops.qasm_path
        row = None
        col = None
        matrix_path = "./qasm_relevant_files/matrix.png"
        topo_convergence_path = "./qasm_relevant_files/topo_convergence.png"
        qubit_layout_path = "./qasm_relevant_files/qubit_layout.png"
        topo_pruning_path = "./qasm_relevant_files/topo_pruning.png"
        final_topo_path = "./qasm_relevant_files/final_topo.png"

        topo_ops = qasm.qasm(qasm_path, 
                             row,
                             col,
                             matrix_path,
                             topo_convergence_path,
                             qubit_layout_path,
                             topo_pruning_path,
                             final_topo_path)

        return copy.deepcopy(topo_ops)
    def qasm_path__row(self, gene_ops):
        qasm_path = gene_ops.qasm_path
        row = gene_ops.row
        col = None
        matrix_path = "./qasm_relevant_files/matrix.png"
        topo_convergence_path = "./qasm_relevant_files/topo_convergence.png"
        qubit_layout_path = "./qasm_relevant_files/qubit_layout.png"
        topo_pruning_path = "./qasm_relevant_files/topo_pruning.png"
        final_topo_path = "./qasm_relevant_files/final_topo.png"

        topo_ops = qasm.qasm(qasm_path, 
                             row,
                             col,
                             matrix_path,
                             topo_convergence_path,
                             qubit_layout_path,
                             topo_pruning_path,
                             final_topo_path)

        return copy.deepcopy(topo_ops)
    def col__qasm_path(self, gene_ops):
        qasm_path = gene_ops.qasm_path
        row = None
        col = gene_ops.col
        matrix_path = "./qasm_relevant_files/matrix.png"
        topo_convergence_path = "./qasm_relevant_files/topo_convergence.png"
        qubit_layout_path = "./qasm_relevant_files/qubit_layout.png"
        topo_pruning_path = "./qasm_relevant_files/topo_pruning.png"
        final_topo_path = "./qasm_relevant_files/final_topo.png"

        topo_ops = qasm.qasm(qasm_path, 
                             row,
                             col,
                             matrix_path,
                             topo_convergence_path,
                             qubit_layout_path,
                             topo_pruning_path,
                             final_topo_path)

        return copy.deepcopy(topo_ops)
    def col__qasm_path__row(self, gene_ops):
        qasm_path = gene_ops.qasm_path
        row = gene_ops.row
        col = gene_ops.col
        matrix_path = "./qasm_relevant_files/matrix.png"
        topo_convergence_path = "./qasm_relevant_files/topo_convergence.png"
        qubit_layout_path = "./qasm_relevant_files/qubit_layout.png"
        topo_pruning_path = "./qasm_relevant_files/topo_pruning.png"
        final_topo_path = "./qasm_relevant_files/final_topo.png"

        topo_ops = qasm.qasm(qasm_path, 
                             row,
                             col,
                             matrix_path,
                             topo_convergence_path,
                             qubit_layout_path,
                             topo_pruning_path,
                             final_topo_path)

        return copy.deepcopy(topo_ops)
    def col__files_path__qasm_path__row(self, gene_ops):
        qasm_path = gene_ops.qasm_path
        col = gene_ops.col
        row = gene_ops.row
        files_path = gene_ops.files_path
        matrix_path = files_path.matrix_path
        topo_convergence_path = files_path.topo_convergence_path
        qubit_layout_path = files_path.qubit_layout_path
        topo_pruning_path = files_path.topo_pruning_path
        final_topo_path = files_path.final_topo_path

        topo_ops = qasm.qasm(qasm_path, 
                             row,
                             col,
                             matrix_path,
                             topo_convergence_path,
                             qubit_layout_path,
                             topo_pruning_path,
                             final_topo_path)

        return copy.deepcopy(topo_ops)
    
    def num__shape(self, gene_ops):
        shape = gene_ops.shape
        num = gene_ops.num

        topo_ops = Dict()
        
        if shape == "hex":
            topo_ops.positions = primitives.generate_hex_pos(num)
        
        topo_ops.edges = []
        return topo_ops