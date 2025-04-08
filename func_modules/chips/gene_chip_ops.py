#######################################################################
# Dynamically generate a set of geometric parameters for the chip based on input parameters (such as quantum bit layout, extension distance, chip width and height).
#######################################################################

from addict import Dict
import copy, func_modules
from base.branch_base import BranchBase
from library import chips as chips_lib

def gene_chip_ops(**gene_ops):
    """
    Generate a set of operational parameters for the chip.

    Input:
        gene_ops: dict, input options for generating chip operational parameters.

    Output:
        chip_ops: dict, the generated set of chip operational parameters.
    """
    gco = GeneChipOps(**gene_ops)
    return copy.deepcopy(gco.branch_process())

class GeneChipOps(BranchBase):
    def chip_name__qubits_ops(self, gene_ops):
        """
        Generate chip parameters based on chip name and quantum bit layout.

        Input:
            gene_ops: dict, containing the following parameters:
                - chip_name: str, chip name.
                - qubits_ops: dict, layout parameters of quantum bits (including gds_pos).

        Output:
            chip_ops: dict, the generated chip operational parameters.
        """
        chip_name = gene_ops.chip_name
        qubits_ops = copy.deepcopy(gene_ops.qubits_ops)
        dist = 2000
        chip_type = "RecChip"

        chip_ops = Dict()

        qubits_name = list(qubits_ops.keys())
        q0_name = qubits_name[0]
        q0_gds_pos = qubits_ops[q0_name].gds_pos
        xmin = q0_gds_pos[0]
        xmax = q0_gds_pos[0]
        ymin = q0_gds_pos[1]
        ymax = q0_gds_pos[1]

        for q_name, q_ops in qubits_ops.items():
            gds_pos = q_ops.gds_pos
            xmin = min(xmin, gds_pos[0])
            xmax = max(xmax, gds_pos[0])
            ymin = min(ymin, gds_pos[1])
            ymax = max(ymax, gds_pos[1])
        
        chip_ops.name = chip_name
        chip_ops.type = chip_type
        chip_ops.start_pos = (xmin-dist, ymin-dist)
        chip_ops.end_pos= (xmax+dist, ymax+dist)

        chip_ops = func_modules.chips.soak_chip(chip_ops)

        return copy.deepcopy(chip_ops)
    
    def chip_name__dist__qubits_ops(self, gene_ops):
        """
        Generate chip parameters based on chip name, quantum bit layout, and extension distance.

        Input:
            gene_ops: dict, containing the following parameters:
                - chip_name: str, chip name.
                - qubits_ops: dict, layout parameters of quantum bits (including gds_pos).
                - dist: float, extension distance.

        Output:
            chip_ops: dict, the generated chip operational parameters.
        """
        chip_name = gene_ops.chip_name
        qubits_ops = copy.deepcopy(gene_ops.qubits_ops)
        dist = gene_ops.dist
        chip_type = "RecChip"

        chip_ops = Dict()

        qubits_name = list(qubits_ops.keys())
        q0_name = qubits_name[0]
        q0_gds_pos = qubits_ops[q0_name].gds_pos
        xmin = q0_gds_pos[0]
        xmax = q0_gds_pos[0]
        ymin = q0_gds_pos[1]
        ymax = q0_gds_pos[1]

        for q_name, q_ops in qubits_ops.items():
            gds_pos = q_ops.gds_pos
            xmin = min(xmin, gds_pos[0])
            xmax = max(xmax, gds_pos[0])
            ymin = min(ymin, gds_pos[1])
            ymax = max(ymax, gds_pos[1])
        
        chip_ops.name = chip_name
        chip_ops.type = chip_type
        chip_ops.start_pos = (xmin-dist, ymin-dist)
        chip_ops.end_pos= (xmax+dist, ymax+dist)

        chip_ops = func_modules.chips.soak_chip(chip_ops)

        return copy.deepcopy(chip_ops)
    
    def qubits_ops(self, gene_ops):
        """
        Use the default chip name to generate chip parameters based on the quantum bit layout.

        Input:
            gene_ops: dict, containing the following parameters:
                - qubits_ops: dict, layout parameters of quantum bits (including gds_pos).

        Output:
            chip_ops: dict, the generated chip operational parameters.
        """
        chip_name = "chip0"
        qubits_ops = copy.deepcopy(gene_ops.qubits_ops)
        dist = 2000
        chip_type = "RecChip"

        chip_ops = Dict()

        qubits_name = list(qubits_ops.keys())
        q0_name = qubits_name[0]
        q0_gds_pos = qubits_ops[q0_name].gds_pos
        xmin = q0_gds_pos[0]
        xmax = q0_gds_pos[0]
        ymin = q0_gds_pos[1]
        ymax = q0_gds_pos[1]

        for q_name, q_ops in qubits_ops.items():
            gds_pos = q_ops.gds_pos
            xmin = min(xmin, gds_pos[0])
            xmax = max(xmax, gds_pos[0])
            ymin = min(ymin, gds_pos[1])
            ymax = max(ymax, gds_pos[1])
        
        chip_ops.name = chip_name
        chip_ops.type = chip_type
        chip_ops.start_pos = (xmin-dist, ymin-dist)
        chip_ops.end_pos= (xmax+dist, ymax+dist)

        chip_ops = func_modules.chips.soak_chip(chip_ops)

        return copy.deepcopy(chip_ops)
    
    def dist__qubits_ops(self, gene_ops):
        """
        Generate chip parameters based on quantum bit layout and extension distance.

        Input:
            gene_ops: dict, containing the following parameters:
                - qubits_ops: dict, layout parameters of quantum bits (including gds_pos).
                - dist: float, extension distance.

        Output:
            chip_ops: dict, the generated chip operational parameters.
        """
        chip_name = "chip0"
        qubits_ops = copy.deepcopy(gene_ops.qubits_ops)
        dist = gene_ops.dist
        chip_type = "RecChip"

        chip_ops = Dict()

        qubits_name = list(qubits_ops.keys())
        q0_name = qubits_name[0]
        q0_gds_pos = qubits_ops[q0_name].gds_pos
        xmin = q0_gds_pos[0]
        xmax = q0_gds_pos[0]
        ymin = q0_gds_pos[1]
        ymax = q0_gds_pos[1]

        for q_name, q_ops in qubits_ops.items():
            gds_pos = q_ops.gds_pos
            xmin = min(xmin, gds_pos[0])
            xmax = max(xmax, gds_pos[0])
            ymin = min(ymin, gds_pos[1])
            ymax = max(ymax, gds_pos[1])
        
        chip_ops.name = chip_name
        chip_ops.type = chip_type
        chip_ops.start_pos = (xmin-dist, ymin-dist)
        chip_ops.end_pos= (xmax+dist, ymax+dist)

        chip_ops = func_modules.chips.soak_chip(chip_ops)

        return copy.deepcopy(chip_ops)
    
    def chip_name__height__qubits_ops__width(self, gene_ops):
        """
        Generate chip parameters based on chip name, quantum bit layout, height, and width.

        Input:
            gene_ops: dict, containing the following parameters:
                - chip_name: str, chip name.
                - qubits_ops: dict, layout parameters of quantum bits (including gds_pos).
                - height: float, chip height.
                - width: float, chip width.

        Output:
            chip_ops: dict, the generated chip operational parameters.
        """
        chip_name = gene_ops.chip_name
        qubits_ops = copy.deepcopy(gene_ops.qubits_ops)
        chip_type = "RecChip"
        width = gene_ops.width
        height = gene_ops.height

        chip_ops = Dict()

        qubits_name = list(qubits_ops.keys())
        q0_name = qubits_name[0]
        q0_gds_pos = qubits_ops[q0_name].gds_pos
        xmin = q0_gds_pos[0]
        xmax = q0_gds_pos[0]
        ymin = q0_gds_pos[1]
        ymax = q0_gds_pos[1]

        for q_name, q_ops in qubits_ops.items():
            gds_pos = q_ops.gds_pos
            xmin = min(xmin, gds_pos[0])
            xmax = max(xmax, gds_pos[0])
            ymin = min(ymin, gds_pos[1])
            ymax = max(ymax, gds_pos[1])

        xmid = (xmin + xmax) / 2
        ymid = (ymin + ymax) / 2

        chip_ops.name = chip_name
        chip_ops.type = chip_type
        chip_ops.start_pos = (xmid-width/2, ymid-height/2)
        chip_ops.end_pos= (xmid+width/2, ymid+height/2)

        chip_ops = func_modules.chips.soak_chip(chip_ops)

        return copy.deepcopy(chip_ops)
    
    def chip_name__chip_type__geometric_ops(self, gene_ops):
        chip_name = gene_ops.chip_name
        chip_type = gene_ops.chip_type
        geometric_ops = copy.deepcopy(gene_ops.geometric_ops)

        chip_ops = Dict()
        chip_ops.name = chip_name
        chip_ops.type = chip_type
        for k, v in geometric_ops.items():
            chip_ops[k] = v
        return chip_ops