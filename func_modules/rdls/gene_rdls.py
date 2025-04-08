#######################################################################
# Dynamically generate the set of operational parameters for the qubit readout cavities based on input parameters
#######################################################################

from addict import Dict
from base.branch_base import BranchBase
import copy

def gene_rdls(**gene_ops):
    """
    Generate the set of operational parameters for the readout cavities.

    Input:
        gene_ops: dict, contains the input options required for generating readout cavities.

    Output:
        rdls_ops: dict, the generated set of operational parameters for the readout cavities.
    """
    gr = GeneRdls(**gene_ops)
    return copy.deepcopy(gr.branch_process())

class GeneRdls(BranchBase):
    """
    A class used for dynamically generating the operational parameters of qubit readout cavities.
    """
    def qubits_ops(self, gene_ops):
        """
        Generate readout cavity operational parameters based on qubit operational parameters.

        Input:
            gene_ops: dict, contains the following parameters:
                - qubits_ops: dict, operational parameters of the qubits.

        Output:
            rdls_ops: dict, the generated set of operational parameters for the readout cavities.
        """
        qubits_ops = copy.deepcopy(gene_ops.qubits_ops)
        rdls_type = "ReadoutCavity"
        chip_name = "chip0"

        rdls_ops = Dict()
        
        for q_name, q_ops in qubits_ops.items():
            rdl_name = q_name + "_readout"
            rdls_ops[rdl_name].name = rdl_name
            rdls_ops[rdl_name].type = rdls_type
            rdls_ops[rdl_name].chip = chip_name
            rdls_ops[rdl_name].start_pos = copy.deepcopy(q_ops.readout_pins[0])
            rdls_ops[rdl_name].end_pos = (q_ops.readout_pins[0][0], q_ops.readout_pins[0][1] + 1000)
        
        return copy.deepcopy(rdls_ops)

    def qubits_ops__rdls_type(self, gene_ops):
        """
        Generate readout cavity operational parameters based on qubit operational parameters and readout cavity type.

        Input:
            gene_ops: dict, contains the following parameters:
                - qubits_ops: dict, operational parameters of the qubits.
                - rdls_type: str, type of the readout cavity.

        Output:
            rdls_ops: dict, the generated set of operational parameters for the readout cavities.
        """
        qubits_ops = copy.deepcopy(gene_ops.qubits_ops)
        rdls_type = gene_ops.rdls_type
        chip_name = "chip0"

        rdls_ops = Dict()
        
        for q_name, q_ops in qubits_ops.items():
            rdl_name = q_name + "_readout"
            rdls_ops[rdl_name].name = rdl_name
            rdls_ops[rdl_name].type = rdls_type
            rdls_ops[rdl_name].chip = chip_name
            rdls_ops[rdl_name].start_pos = copy.deepcopy(q_ops.readout_pins[0])
            rdls_ops[rdl_name].end_pos = (q_ops.readout_pins[0][0], q_ops.readout_pins[0][1] + 1000)

        return copy.deepcopy(rdls_ops)
    
    def pin_num__qubits_ops__rdls_type(self, gene_ops):
        """
        Generate readout cavity operational parameters based on pin number, qubit operational parameters, and readout cavity type.

        Input:
            gene_ops: dict, contains the following parameters:
                - qubits_ops: dict, operational parameters of the qubits.
                - rdls_type: str, type of the readout cavity.
                - pin_num: int, specified pin number.

        Output:
            rdls_ops: dict, the generated set of operational parameters for the readout cavities.
        """
        qubits_ops = copy.deepcopy(gene_ops.qubits_ops)
        rdls_type = gene_ops.rdls_type
        chip_name = "chip0"
        pin_num = gene_ops.pin_num

        rdls_ops = Dict()
        
        for q_name, q_ops in qubits_ops.items():
            rdl_name = q_name + "_readout"
            rdls_ops[rdl_name].name = rdl_name
            rdls_ops[rdl_name].type = rdls_type
            rdls_ops[rdl_name].chip = chip_name
            rdls_ops[rdl_name].start_pos = copy.deepcopy(q_ops.readout_pins[pin_num])
            rdls_ops[rdl_name].end_pos = (q_ops.readout_pins[pin_num][0], q_ops.readout_pins[pin_num][1] + 1000)

        return copy.deepcopy(rdls_ops)
    
    def chip_name__qubits_ops__rdls_type(self, gene_ops):
        """
        Generate readout cavity operational parameters based on chip name, qubit operational parameters, and readout cavity type.

        Input:
            gene_ops: dict, contains the following parameters:
                - qubits_ops: dict, operational parameters of the qubits.
                - rdls_type: str, type of the readout cavity.
                - chip_name: str, name of the chip.

        Output:
            rdls_ops: dict, the generated set of operational parameters for the readout cavities.
        """
        qubits_ops = copy.deepcopy(gene_ops.qubits_ops)
        rdls_type = gene_ops.rdls_type
        chip_name = gene_ops.chip_name

        rdls_ops = Dict()
        
        for q_name, q_ops in qubits_ops.items():
            rdl_name = q_name + "_readout"
            rdls_ops[rdl_name].name = rdl_name
            rdls_ops[rdl_name].type = rdls_type
            rdls_ops[rdl_name].chip = chip_name
            rdls_ops[rdl_name].start_pos = copy.deepcopy(q_ops.readout_pins[0])
            rdls_ops[rdl_name].end_pos = (q_ops.readout_pins[0][0], q_ops.readout_pins[0][1] + 1000)

        return copy.deepcopy(rdls_ops)
    

    def chip_name__geometric_options__qubits_ops__rdls_type(self, gene_ops):
        """
        Generate readout cavity operational parameters based on chip name, geometric options, qubit operational parameters, and readout cavity type.

        Input:
            gene_ops: dict, contains the following parameters:
                - qubits_ops: dict, operational parameters of the qubits.
                - rdls_type: str, type of the readout cavity.
                - chip_name: str, name of the chip.
                - geometric_options: dict, geometric options.

        Output:
            rdls_ops: dict, the generated set of operational parameters for the readout cavities.
        """
        qubits_ops = copy.deepcopy(gene_ops.qubits_ops)
        rdls_type = gene_ops.rdls_type
        chip_name = gene_ops.chip_name
        geometric_options = copy.deepcopy(gene_ops.geometric_options)

        rdls_ops = Dict()

        for q_name, q_ops in qubits_ops.items():
            rdl_name = q_name + "_readout"
            rdls_ops[rdl_name].name = rdl_name
            rdls_ops[rdl_name].type = rdls_type
            rdls_ops[rdl_name].chip = chip_name
            rdls_ops[rdl_name].start_pos = copy.deepcopy(q_ops.readout_pins[0])
            rdls_ops[rdl_name].end_pos = (q_ops.readout_pins[0][0], q_ops.readout_pins[0][1] + 1000)
            for op_name, op_value in geometric_options.items():
                rdls_ops[rdl_name][op_name] = copy.deepcopy(op_value)

        return copy.deepcopy(rdls_ops)

    def geometric_options__qubits_ops__rdls_type(self, gene_ops):
        """
        Generate readout cavity operational parameters based on geometric options, qubit operational parameters, and readout cavity type.

        Input:
            gene_ops: dict, contains the following parameters:
                - qubits_ops: dict, operational parameters of the qubits.
                - rdls_type: str, type of the readout cavity.
                - geometric_options: dict, geometric options.

        Output:
            rdls_ops: dict, the generated set of operational parameters for the readout cavities.
        """
        qubits_ops = copy.deepcopy(gene_ops.qubits_ops)
        rdls_type = gene_ops.rdls_type
        chip_name = "chip0"
        geometric_options = copy.deepcopy(gene_ops.geometric_options)

        rdls_ops = Dict()

        for q_name, q_ops in qubits_ops.items():
            rdl_name = q_name + "_readout"
            rdls_ops[rdl_name].name = rdl_name
            rdls_ops[rdl_name].type = rdls_type
            rdls_ops[rdl_name].chip = chip_name
            rdls_ops[rdl_name].start_pos = copy.deepcopy(q_ops.readout_pins[0])
            rdls_ops[rdl_name].end_pos = (q_ops.readout_pins[0][0], q_ops.readout_pins[0][1] + 1000)
            for op_name, op_value in geometric_options.items():
                rdls_ops[rdl_name][op_name] = copy.deepcopy(op_value)

        return copy.deepcopy(rdls_ops)