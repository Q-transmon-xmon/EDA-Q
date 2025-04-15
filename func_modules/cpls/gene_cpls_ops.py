#######################################################################
# Dynamically generate a set of geometric parameters for coupling lines based on input parameters (such as quantum bit topology, coupling line types, etc.)
#######################################################################

from addict import Dict
from base.branch_base import BranchBase
import copy
from func_modules.cpls import primitives

def gene_cpls_ops(**gene_ops):
    """
    Generate a set of operational parameters for coupling lines.

    Input:
        gene_ops: dict, input options for generating operational parameters of coupling lines.

    Output:
        cpls_ops: dict, the generated set of operational parameters for coupling lines.
    """
    gco = GeneCplsOps(**gene_ops)
    return copy.deepcopy(gco.branch_process())

class GeneCplsOps(BranchBase):
    """
    A class used to dynamically generate geometric operational parameters for coupling lines.
    """

    def options(self, gene_ops):
        """
        Return a deep copy of the input options.

        Input:
            gene_ops: dict, parameters containing configuration options.

        Output:
            options: dict, a deep copy of the input parameters options.
        """
        return copy.deepcopy(gene_ops.options)

    def qubits_ops__topo_ops(self, gene_ops):
        """
        Generate coupling line parameters based on quantum bit layout and topology information.

        Input:
            gene_ops: dict, containing the following parameters:
                - qubits_ops: dict, layout parameters of quantum bits.
                - topo_ops: dict, topological relationships between quantum bits.

        Output:
            cpls_ops: dict, the generated operational parameters for coupling lines.
        """
        topo_ops = copy.deepcopy(gene_ops.topo_ops)
        qubits_ops = copy.deepcopy(gene_ops.qubits_ops)
        cpls_type = "CouplingLineStraight"  # Default coupling line type
        chip_name = "chip0"  # Default chip name

        cpls_ops = primitives.generate_cpls(topo_ops=topo_ops,
                                            qubits_ops=qubits_ops,
                                            cpls_type=cpls_type,
                                            chip_name=chip_name)
        return copy.deepcopy(cpls_ops)
    
    def chip_name__qubits_ops__topo_ops(self, gene_ops):
        """
        Generate coupling line parameters based on quantum bit layout and topology information.

        Input:
            gene_ops: dict, containing the following parameters:
                - qubits_ops: dict, layout parameters of quantum bits.
                - topo_ops: dict, topological relationships between quantum bits.

        Output:
            cpls_ops: dict, the generated operational parameters for coupling lines.
        """
        topo_ops = copy.deepcopy(gene_ops.topo_ops)
        qubits_ops = copy.deepcopy(gene_ops.qubits_ops)
        cpls_type = "CouplingLineStraight"  # Default coupling line type
        chip_name = gene_ops.chip_name  # Default chip name

        cpls_ops = primitives.generate_cpls(topo_ops=topo_ops,
                                            qubits_ops=qubits_ops,
                                            cpls_type=cpls_type,
                                            chip_name=chip_name)
        return copy.deepcopy(cpls_ops)

    def cpls_type__qubits_ops__topo_ops(self, gene_ops):
        """
        Generate coupling line parameters based on coupling line type, quantum bit layout, and topology information.

        Input:
            gene_ops: dict, containing the following parameters:
                - cpls_type: str, type of coupling line.
                - qubits_ops: dict, layout parameters of quantum bits.
                - topo_ops: dict, topological relationships between quantum bits.

        Output:
            cpls_ops: dict, the generated operational parameters for coupling lines.
        """
        topo_ops = copy.deepcopy(gene_ops.topo_ops)
        qubits_ops = copy.deepcopy(gene_ops.qubits_ops)
        cpls_type = gene_ops.cpls_type
        chip_name = "chip0"  # Default chip name

        cpls_ops = primitives.generate_cpls(topo_ops=topo_ops,
                                            qubits_ops=qubits_ops,
                                            cpls_type=cpls_type,
                                            chip_name=chip_name)
        return copy.deepcopy(cpls_ops)

    def chip__cpls_type__qubits_ops__topo_ops(self, gene_ops):
        """
        Generate coupling line parameters based on chip name, coupling line type, quantum bit layout, and topology information.

        Input:
            gene_ops: dict, containing the following parameters:
                - chip: str, chip name (will be reassigned to chip_name).
                - cpls_type: str, type of coupling line.
                - qubits_ops: dict, layout parameters of quantum bits.
                - topo_ops: dict, topological relationships between quantum bits.

        Output:
            cpls_ops: dict, the generated operational parameters for coupling lines.
        """
        gene_ops.chip_name = gene_ops.chip
        del gene_ops.chip
        return self.chip_name__cpls_type__qubits_ops__topo_ops(gene_ops)

    def chip_name__cpls_type__qubits_ops__topo_ops(self, gene_ops):
        """
        Generate coupling line parameters based on chip name, coupling line type, quantum bit layout, and topology information.

        Input:
            gene_ops: dict, containing the following parameters:
                - chip_name: str, chip name.
                - cpls_type: str, type of coupling line.
                - qubits_ops: dict, layout parameters of quantum bits.
                - topo_ops: dict, topological relationships between quantum bits.

        Output:
            cpls_ops: dict, the generated operational parameters for coupling lines.
        """
        topo_ops = copy.deepcopy(gene_ops.topo_ops)
        qubits_ops = copy.deepcopy(gene_ops.qubits_ops)
        cpls_type = gene_ops.cpls_type
        chip_name = gene_ops.chip_name

        cpls_ops = primitives.generate_cpls(topo_ops=topo_ops,
                                            qubits_ops=qubits_ops,
                                            cpls_type=cpls_type,
                                            chip_name=chip_name)
        return copy.deepcopy(cpls_ops)