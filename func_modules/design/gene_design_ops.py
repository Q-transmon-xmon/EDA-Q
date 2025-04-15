###################################################################################################
#Define the GeneDesignOps class to generate design operational parameters through different methods
###################################################################################################



from addict import Dict
from base.branch_base import BranchBase
import copy
from func_modules import topo as topo_module

def gene_design_ops(**gene_ops):
    """
    Generate design operational parameters.

    Input:
        gene_ops: dict, input options for generating design operational parameters.

    Output:
        design_ops: dict, the generated design operational parameters.
    """
    gdo = GeneDesignOps(**gene_ops)
    return copy.deepcopy(gdo.branch_process())

class GeneDesignOps(BranchBase):
    def qasm_path(self, gene_ops):
        """
        Generate operational parameters based on the QASM file path.

        Input:
            gene_ops: dict, containing the following parameters:
                - qasm_path: str, the path to the QASM file.

        Output:
            ops: dict, the generated operational parameters.
        """
        qasm_path = gene_ops.qasm_path
        ops = Dict()
        ops.topology = topo_module.generate_topology(qasm_path=qasm_path)
        return copy.deepcopy(ops)
    
    def topo_col__topo_row(self, gene_ops):
        """
        Generate operational parameters based on topology column and row numbers.

        Input:
            gene_ops: dict, containing the following parameters:
                - topo_col: int, the number of columns in the topology.
                - topo_row: int, the number of rows in the topology.

        Output:
            ops: dict, the generated operational parameters.
        """
        topo_col = gene_ops.topo_col
        topo_row = gene_ops.topo_row

        ops = Dict()
        ops.topology = topo_module.generate_topology(topo_col=topo_col, topo_row=topo_row)

        return copy.deepcopy(ops)