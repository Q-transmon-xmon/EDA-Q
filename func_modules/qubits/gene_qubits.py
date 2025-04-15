from base.branch_base import BranchBase
from addict import Dict
import copy, math, toolbox

def gene_qubits(**gene_ops):
    """
    Generate a set of operational parameters for quantum bits.

    Input:
        gene_ops: dict, containing input options required for generating quantum bits.

    Output:
        qubits_ops: dict, the generated set of operational parameters for quantum bits.
    """
    gq = GeneQubits(**gene_ops)
    return copy.deepcopy(gq.branch_process())

class GeneQubits(BranchBase):
    # Helper methods
    def generate_gds_pos(self, col, row, dist):
        """
        Generate GDS coordinates for quantum bits based on column and row numbers and spacing.

        Input:
            col: int, the number of columns.
            row: int, the number of rows.
            dist: float, the spacing between quantum bits.

        Output:
            gds_pos: list, a list of GDS coordinates for quantum bits.
        """
        gds_pos = []
        for x in range(0, col):
            for y in range(0, row):
                gds_pos.append((x*dist, y*dist))
        return copy.deepcopy(gds_pos)

    def generate_topo_pos(self, col, row):
        """
        Generate topological positions for quantum bits based on column and row numbers.

        Input:
            col: int, the number of columns.
            row: int, the number of rows.

        Output:
            topo_pos: list, a list of topological positions for quantum bits.
        """
        gds_pos = []
        for x in range(0, col):
            for y in range(0, row):
                gds_pos.append((x, y))
        return copy.deepcopy(gds_pos)

    def generate_gds_pos2(self, topo_positions, dist):
        """
        Generate GDS coordinates based on topological positions.

        Input:
            topo_positions: dict, a dictionary of topological positions.
            dist: float, the spacing between quantum bits.

        Output:
            gds_pos: dict, a dictionary of GDS coordinates for quantum bits.
        """
        gds_pos = Dict()
        for q_name, topo_pos in topo_positions.items():
            gds_pos[q_name] = (topo_pos[0]*dist, topo_pos[1]*dist)
        return copy.deepcopy(gds_pos)
    
    # Functional methods
    def num(self, gene_ops):
        """
        Generate operational parameters based on the number of quantum bits.

        Input:
            gene_ops: dict, containing the number of quantum bits.

        Output:
            qubits_ops: dict, the generated set of operational parameters for quantum bits.
        """
        num = gene_ops.num
        type = "Transmon"

        col = math.ceil(math.sqrt(num))
        row = math.ceil(num/col)

        topo_pos_list = self.generate_topo_pos(col=col, row=row)[:num]
        gds_pos_list = self.generate_gds_pos(col=col, row=row, dist=2000)[:num]

        qubits_ops = Dict()
        for i in range(num):
            q_name = "q" + str(i)
            qubits_ops[q_name].name = q_name
            qubits_ops[q_name].type = type
            qubits_ops[q_name].gds_pos = copy.deepcopy(gds_pos_list[i])
            qubits_ops[q_name].topo_pos = copy.deepcopy(topo_pos_list[i])
            qubits_ops[q_name].chip = "chip0"
        return copy.deepcopy(qubits_ops)
    def col__num(self, gene_ops):
        """
        Generate operational parameters based on the number of columns and quantum bits.

        Input:
            gene_ops: dict, containing the number of columns and quantum bits.

        Output:
            qubits_ops: dict, the generated set of operational parameters for quantum bits.
        """
        num = gene_ops.num
        type = "Transmon"
        col = gene_ops.col
        row = math.ceil(num/col)

        topo_pos_list = self.generate_topo_pos(col=col, row=row)
        gds_pos_list = self.generate_gds_pos(col=col, row=row, dist=2000)

        qubits_ops = Dict()
        for i in range(gene_ops.num):
            qname = "q" + str(i)
            qubits_ops[qname].name = "q" + str(i)
            qubits_ops[qname].type = type
            qubits_ops[qname].gds_pos = copy.deepcopy(gds_pos_list[i])
            qubits_ops[qname].topo_pos = copy.deepcopy(topo_pos_list[i])
            qubits_ops[qname].chip = "chip0"
        return copy.deepcopy(qubits_ops)
    
    def col__dist__num(self, gene_ops):
        """
        Generate operational parameters based on the number of columns, spacing, and quantum bits.

        Input:
            gene_ops: dict, containing the number of columns, spacing, and quantum bits.

        Output:
            qubits_ops: dict, the generated set of operational parameters for quantum bits.
        """
        num = gene_ops.num
        type = "Transmon"
        col = gene_ops.col
        row = math.ceil(num/col)
        dist=gene_ops.dist

        topo_pos_list = self.generate_topo_pos(col=col, row=row)
        gds_pos_list = self.generate_gds_pos(col=col, row=row, dist=dist)

        qubits_ops = Dict()
        for i in range(gene_ops.num):
            qname = "q" + str(i)
            qubits_ops[qname].name = "q" + str(i)
            qubits_ops[qname].type = type
            qubits_ops[qname].gds_pos = copy.deepcopy(gds_pos_list[i])
            qubits_ops[qname].topo_pos = copy.deepcopy(topo_pos_list[i])
            qubits_ops[qname].chip = "chip0"
        return copy.deepcopy(qubits_ops)
    
    def col__dist__geometric_options__num(self, gene_ops):
        """
        Generate operational parameters based on the number of columns, spacing, geometric options, and quantum bits.

        Input:
            gene_ops: dict, containing the number of columns, spacing, geometric options, and quantum bits.

        Output:
            qubits_ops: dict, the generated set of operational parameters for quantum bits.
        """
        num = gene_ops.num
        type = "Transmon"
        col = gene_ops.col
        row = math.ceil(num/col)
        dist = gene_ops.dist
        geometric_options = copy.deepcopy(gene_ops.geometric_options)

        topo_pos_list = self.generate_topo_pos(col=col, row=row)
        gds_pos_list = self.generate_gds_pos(col=col, row=row, dist=dist)

        qubits_ops = Dict()
        for i in range(gene_ops.num):
            qname = "q" + str(i)
            qubits_ops[qname].name = "q" + str(i)
            qubits_ops[qname].type = type
            qubits_ops[qname].gds_pos = copy.deepcopy(gds_pos_list[i])
            qubits_ops[qname].topo_pos = copy.deepcopy(topo_pos_list[i])
            qubits_ops[qname].chip = "chip0"
            for op_name, op_value in geometric_options.items():
                qubits_ops[qname][op_name] = copy.deepcopy(op_value)
        return copy.deepcopy(qubits_ops)
    
    def num__qubits_type(self, gene_ops):
        """
        Generate operational parameters based on the number of quantum bits and type.

        Input:
            gene_ops: dict, containing the number of quantum bits and type.

        Output:
            qubits_ops: dict, the generated set of operational parameters for quantum bits.
        """
        num = gene_ops.num
        type = gene_ops.qubits_type

        col = math.ceil(math.sqrt(num))
        row = math.ceil(num/col)

        topo_pos_list = self.generate_topo_pos(col=col, row=row)
        gds_pos_list = self.generate_gds_pos(col=col, row=row, dist=2000)

        qubits_ops = Dict()
        for i in range(gene_ops.num):
            q_name = "q" + str(i)
            qubits_ops[q_name].name = q_name
            qubits_ops[q_name].type = type
            qubits_ops[q_name].gds_pos = copy.deepcopy(gds_pos_list[i])
            qubits_ops[q_name].topo_pos = copy.deepcopy(topo_pos_list[i])
            qubits_ops[q_name].chip = "chip0"
        return copy.deepcopy(qubits_ops)
    
    def chip__dist__qubits_type__topo_positions(self, gene_ops):
        return self.chip_name__dist__qubits_type__topo_positions(gene_ops)
    
    def topo_positions(self, gene_ops):
        """
        Generate operational parameters for quantum bits based on topological positions.

        Input:
            gene_ops: dict, containing the topological positions of quantum bits.

        Output:
            qubits_ops: dict, the generated set of operational parameters for quantum bits.
        """
        gene_ops = copy.deepcopy(gene_ops)

        topo_positions = copy.deepcopy(gene_ops.topo_positions)
        gene_ops.chip_name = "chip0"
        gene_ops.dist = 2000
        gene_ops.qubits_type = "Transmon"

        return self.chip_name__dist__qubits_type__topo_positions(gene_ops)
    
    def chip_name__dist__qubits_type__topo_positions(self, gene_ops):
        """
        Generate operation parameters based on chip name, distance, qubit type, and topological positions.

        Input:
            gene_ops: dict, contains chip name, distance, qubit type, and topological positions.

        Output:
            qubits_ops: dict, a set of generated qubit operation parameters.
        """
        topo_positions = copy.deepcopy(gene_ops.topo_positions)
        chip_name = gene_ops.chip_name
        dist = gene_ops.dist
        qubits_type = gene_ops.qubits_type

        gds_pos = self.generate_gds_pos2(topo_positions=topo_positions, dist=dist)
        
        qubits_ops = Dict()
        for q_name, topo_pos in topo_positions.items():
            qubits_ops[q_name].name = q_name
            qubits_ops[q_name].type = qubits_type
            qubits_ops[q_name].gds_pos = copy.deepcopy(gds_pos[q_name])
            qubits_ops[q_name].topo_pos = copy.deepcopy(topo_pos)
            qubits_ops[q_name].chip = chip_name

        return copy.deepcopy(qubits_ops)

    def qubits_type__topo_positions(self, gene_ops):
        """
        Generate operation parameters based on qubit type and topological positions.

        Input:
            gene_ops: dict, contains qubit type and topological positions.

        Output:
            qubits_ops: dict, a set of generated qubit operation parameters.
        """
        topo_positions = copy.deepcopy(gene_ops.topo_positions)
        chip_name = "chip0"
        dist = 2000
        qubits_type = gene_ops.qubits_type

        gds_pos = self.generate_gds_pos2(topo_positions=topo_positions, dist=dist)
        
        qubits_ops = Dict()
        for q_name, topo_pos in topo_positions.items():
            qubits_ops[q_name].name = q_name
            qubits_ops[q_name].type = qubits_type
            qubits_ops[q_name].gds_pos = copy.deepcopy(gds_pos[q_name])
            qubits_ops[q_name].topo_pos = copy.deepcopy(topo_pos)
            qubits_ops[q_name].chip = chip_name

        return copy.deepcopy(qubits_ops)

    def geometric_ops__qubits_type__topo_positions(self, gene_ops):
        """
        Generate operation parameters based on geometric options, qubit type, and topological positions.

        Input:
            gene_ops: dict, contains geometric options, qubit type, and topological positions.

        Output:
            qubits_ops: dict, a set of generated qubit operation parameters.
        """
        topo_positions = copy.deepcopy(gene_ops.topo_positions)
        chip_name = "chip0"
        dist = 2000
        qubits_type = gene_ops.qubits_type
        geometric_ops = copy.deepcopy(gene_ops.geometric_ops)

        gds_pos = self.generate_gds_pos2(topo_positions=topo_positions, dist=dist)
        
        qubits_ops = Dict()
        for q_name, topo_pos in topo_positions.items():
            qubits_ops[q_name].name = q_name
            qubits_ops[q_name].type = qubits_type
            qubits_ops[q_name].gds_pos = copy.deepcopy(gds_pos[q_name])
            qubits_ops[q_name].topo_pos = copy.deepcopy(topo_pos)
            qubits_ops[q_name].chip = chip_name
            for op_name, op_value in geometric_ops.items():
                qubits_ops[q_name][op_name] = copy.deepcopy(op_value)

        return copy.deepcopy(qubits_ops)

    def dist__qubits_type__topo_positions(self, gene_ops):
        """
        Generate qubit operation parameters based on distance, qubit type, and topological positions.

        Input:
            gene_ops: dict, contains the following parameters:
                - topo_positions: dict, a dictionary of qubit topological positions.
                - dist: float, the distance between qubits.
                - qubits_type: str, the type of qubits.

        Output:
            qubits_ops: dict, a set of generated qubit operation parameters, including topological positions and geometric information.
        """
        topo_positions = copy.deepcopy(gene_ops.topo_positions)
        chip_name = "chip0"
        dist = gene_ops.dist
        qubits_type = gene_ops.qubits_type

        gds_pos = self.generate_gds_pos2(topo_positions=topo_positions, dist=dist)
        
        qubits_ops = Dict()
        for q_name, topo_pos in topo_positions.items():
            qubits_ops[q_name].name = q_name
            qubits_ops[q_name].type = qubits_type
            qubits_ops[q_name].gds_pos = copy.deepcopy(gds_pos[q_name])
            qubits_ops[q_name].topo_pos = copy.deepcopy
            qubits_ops[q_name].chip = chip_name

        return copy.deepcopy(qubits_ops)
    
    def chip_name__qubits_type__topo_positions(self, gene_ops):
        """
        Generate qubit operation parameters based on chip name, qubit type, and topological positions.

        Input:
            gene_ops: dict, contains the following parameters:
                - topo_positions: dict, a dictionary of qubit topological positions.
                - chip_name: str, the name of the chip.
                - qubits_type: str, the type of the qubits.

        Output:
            qubits_ops: dict, a set of generated qubit operation parameters, including topological positions and geometric information.
        """
        topo_positions = copy.deepcopy(gene_ops.topo_positions)
        chip_name = gene_ops.chip_name
        dist = 2000
        qubits_type = gene_ops.qubits_type

        gds_pos = self.generate_gds_pos2(topo_positions=topo_positions, dist=dist)
        
        qubits_ops = Dict()
        for q_name, topo_pos in topo_positions.items():
            qubits_ops[q_name].name = q_name
            qubits_ops[q_name].type = qubits_type
            qubits_ops[q_name].gds_pos = copy.deepcopy(gds_pos[q_name])
            qubits_ops[q_name].topo_pos = copy.deepcopy(topo_pos)
            qubits_ops[q_name].chip = chip_name

        return copy.deepcopy(qubits_ops)
