from addict import Dict
from base.base import Base
from api import topology, gds, tag, equivalent_circuit
import toolbox
import copy
import func_modules

class Design(Base):
    def __init__(self, **init_ops):
        """
        Initialize the design object, receiving variable parameters for initialization.

        Input:
            init_ops: Dictionary, containing the parameters required for initialization.
        
        Output:
            None
        """
        self.initialization(**init_ops)
        return

    def initialization(self, **init_ops):
        """
        Initialize the design object, setting related parameters and attributes.

        Input:
            init_ops: Dictionary, containing the options for initializing the design.
        
        Output:
            None
        """
        # Create instances of each submodule
        self.topology = topology.Topology()
        self.equivalent_circuit = equivalent_circuit.EquivalentCircuit()
        self.gds = gds.Gds()
        self.tag = tag.Tag()
        # Save the list of current object attribute names
        self.op_name_list = list(self.__dict__.keys())
        # Backup the current design parameters
        self.bk_ops = Dict()
        # Generate design parameters and inject them into the object
        options = func_modules.design.generate_design(**init_ops)
        self.inject_options(options)
        super().__setattr__("bk_ops", copy.deepcopy(options))
        return

    def clear(self):
        """
        Clear the attributes of the current design object.

        Input:
            None
        
        Output:
            None
        """
        self.topology = None
        self.gds = None
        self.tag = None
        return

    def extract_options(self):
        """
        Extract the current object's design options and return a deep copy.

        Input:
            None
        
        Output:
            options: Dict, containing a deep copy of the current design object's topology, GDS, and tag options.
        """
        options = Dict()
        options.topology = self.topology.options
        options.gds = self.gds.options
        options.tag = self.tag.options
        return copy.deepcopy(options)

    def inject_options(self, options):
        """
        Inject parameters into the design object.

        Input:
            options: Dict, containing the topology, GDS, and tag options to be injected.
        
        Output:
            None
        """
        self.clear()  # Clear existing object attributes
        super().__setattr__("topology", topology.Topology(options=options.topology))
        super().__setattr__("equivalent_circuit", equivalent_circuit.EquivalentCircuit(options=options.equivalent_circuit))
        super().__setattr__("gds", gds.Gds(options=options.gds))
        super().__setattr__("tag", tag.Tag(options=options.tag))
        return

    def draw_gds(self):
        """
        Draw GDS graphics.
        """
        self.gds.draw_gds()

    def calc_general_ops(self):
        """
        Calculate general operations.

        Input:
            None
        
        Output:
            None
        """
        self.gds.calc_general_ops()
        return

    def generate_topology(self, **init_ops):
        """
        Generate topology structure, receiving variable parameters.

        Input:
            init_ops: Dictionary, containing the parameters required for generating topology.
        
        Output:
            None
        """
        self.topology = topology.Topology(**init_ops)
        return

    def generate_qubits_from_topo(self, **gene_ops):
        """
        This method is deprecated, generate qubits based on topology.

        Input:
            gene_ops: Dictionary, containing the parameters for generating qubits.
        
        Output:
            None
        """
        topo_positions = copy.deepcopy(self.topology.positions)
        gene_ops = Dict(gene_ops)
        gene_ops.topo_positions = topo_positions
        self.gds.generate_qubits_from_topo(**gene_ops)
        return
    
    def generate_qubits_from_topo1(self, qubits_type: str = "Transmon", chip_name: str = "chip0", dist: float = 2000):
        self.gds.generate_qubits_from_topo1(topo_positions=self.topology.positions,
                                            qubits_type=qubits_type,
                                            chip_name=chip_name,
                                            dist=dist)
        return

    def generate_qubits(self, **gene_ops):
        """
        Generate qubits, supporting topology parameters.

        Input:
            gene_ops: Dictionary, containing the parameters for generating qubits, possibly including topology options.
        
        Output:
            None
        """
        if "topology" not in gene_ops.keys():
            gene_ops["topology"] = False
        if gene_ops["topology"] == True:
            topo_ops = copy.deepcopy(self.topology.options)
            gene_ops["topo_positions"] = copy.deepcopy(topo_ops.positions)
        del gene_ops["topology"]
        self.gds.generate_qubits(**gene_ops)
        return

    def generate_coupling_lines_from_topo_and_qubits(self, **gene_ops):
        """
        Backward compatible, generate coupling lines based on topology and qubits.

        Input:
            gene_ops: Dictionary, containing the parameters for generating coupling lines.
        
        Output:
            None
        """
        gene_ops["topo_ops"] = copy.deepcopy(self.topology.options)
        self.gds.generate_coupling_lines_from_qubits(**gene_ops)
        return
    
    def generate_coupling_lines_from_topo_and_qubits1(self,
                                                      cpls_type: str = "CouplineLineStraight",
                                                      chip_name: str = "chip0"):
        topo_ops = self.topology.options
        self.gds.generate_coupling_lines_from_topo_and_qubits(topo_ops=topo_ops,
                                                              cpls_type=cpls_type,
                                                              chip_name=chip_name)
        return

    def generate_coupling_lines(self, **gene_ops):
        """
        Generate coupling lines, supporting topology parameters.

        Input:
            gene_ops: Dictionary, containing the parameters for generating coupling lines, possibly including topology options.
        
        Output:
            None
        """
        if "topology" in gene_ops.keys():
            if gene_ops["topology"] == True:
                topo_ops = copy.deepcopy(self.topology.options)
                gene_ops["topo_ops"]  = copy.deepcopy(topo_ops)
            del gene_ops["topology"]
        
        self.gds.generate_coupling_lines(**gene_ops)
        return

    def add_cpl(self, 
                q0_name: str = None,
                q0_pin_num: int = 0,
                q1_name: str = None,
                q1_pin_num: int = 0,
                cp_type: str = "CouplingLineStraight", 
                chip: str = "chip0", 
                geometric_ops: Dict = Dict()):
        """
        Add a coupling line, specifying the qubit and its pin.

        Input:
            q0_name: str, the name of qubit 0.
            q0_pin_num: int, the pin number of qubit 0.
            q1_name: str, the name of qubit 1.
            q1_pin_num: int, the pin number of qubit 1.
            cp_type: str, the type of coupling line, default is "CouplingLineStraight".
            chip: str, the name of the chip, default is "chip0".
            geometric_ops: Dict, the parameters for geometric operations.
        
        Output:
            None
        """
        self.gds.add_cpl(q0_name=q0_name,
                         q0_pin_num=q0_pin_num,
                         q1_name=q1_name,
                         q1_pin_num=q1_pin_num,
                         cp_type=cp_type, 
                         chip=chip, 
                         geometric_ops=geometric_ops)
        
        self.topology.add_edge(q0_name, q1_name)
        return

    def routing(self, **routing_ops):
        """
        Perform routing operations.

        Input:
            routing_ops: Dictionary, containing the parameters for routing operations.
        
        Output:
            None
        """
        self.gds.routing(**routing_ops)
        return

    def add_chip(self, chip_name: str = "chip0", chip_type: str = "RecChip", geometric_ops: Dict = Dict()):
        """
        Add a chip, specifying the type and geometric operations.

        Input:
            chip_name: str, the name of the chip, default is "chip0".
            chip_type: str, the type of the chip, default is "RecChip".
            geometric_ops: Dict, the parameters for geometric operations.
        
        Output:
            None
        """
        self.gds.add_chip(chip_name=chip_name,
                          chip_type=chip_type,
                          geometric_ops=geometric_ops)
        return

    def copy_chip(self, old_chip_name, new_chip_name):
        """
        Copy a chip.

        Input:
            old_chip_name: str, the name of the old chip.
            new_chip_name: str, the name of the new chip.
        
        Output:
            None
        """
        self.gds.copy_chip(old_chip_name, new_chip_name)
        return

    def generate_readout_lines_from_qubits(self, **gene_ops):
        """
        Backward compatible, generate readout lines based on qubits.

        Input:
            gene_ops: Dictionary, containing the parameters for generating readout lines.
        
        Output:
            None
        """
        self.gds.generate_readout_lines_from_qubits(**gene_ops)
        return

    def generate_readout_lines(self, **gene_ops):
        """
        Generate readout lines.

        Input:
            gene_ops: Dictionary, containing the parameters for generating readout lines.
        
        Output:
            None
        """
        self.gds.generate_readout_lines(**gene_ops)
        return

    def generate_chip_from_qubits(self, **gene_ops):
        """
        Generate a chip based on qubits.

        Input:
            gene_ops: Dictionary, containing the parameters required for generating a chip.
        
        Output:
            None
        """
        self.gds.generate_chip_from_qubits(**gene_ops)
        return

    def generate_chip(self, **gene_ops):
        """
        Generate a chip, receiving variable parameters.

        Input:
            gene_ops: Dictionary, containing the parameters for generating a chip.
        
        Output:
           None
        """
        self.gds.generate_chip(**gene_ops)
        return

    def change_qubits_type(self, qubits_type):
        """
        Change the type of qubits.

        Input:
            qubits_type: str, the new type of qubits.
        
        Output:
            None
        """
        self.gds.change_qubits_type(qubits_type)
        return

    def simulation(self, **sim_ops):
        """
        Perform simulation operations.

        Input:
            sim_ops: Dictionary, containing the parameters required for simulation.
        
        Output:
            None
        """
        self.gds.simulation(**sim_ops)
        return

    def change_chip_size_from_Flipchip_routing(self):
        """
        Change the size of the chip based on the calculation results of Flipchip routing.

        Input:
            None
        
        Output:
            None
        """
        self.gds.change_chip_size_from_Flipchip_routing()
        return

    def generate_cross_overs_from_cpls_and_tmls(self, **gene_ops):
        """
        Generate crossovers based on coupling lines and transmission lines.

        Input:
            gene_ops: Dictionary, containing the parameters for generating crossovers.
        
        Output:
            None
        """
        self.gds.generate_cross_overs_from_cpls_and_tmls(**gene_ops)
        return

    def generate_cross_overs(self, **gene_ops):
        """
        Generate crossovers.

        Input:
            gene_ops: Dictionary, containing the parameters for generating crossovers.
        
        Output:
            None
        """
        self.gds.generate_cross_overs(**gene_ops)
        return

    def save_circuit_png(self, qasm_path, circ_path):
        """
        Save the quantum circuit as a PNG image.

        Input:
            qasm_path: str, the path to the QASM file.
            circ_path: str, the path to save the circuit diagram PNG file.
        
        Output:
            None
        """
        from qiskit import QuantumCircuit
        
        # Read the quantum program file
        f = open(qasm_path)
        code = f.read()
        # Build the quantum circuit using Qiskit
        circuit = QuantumCircuit.from_qasm_str(code)
        diagram = circuit.draw(output='mpl')
        diagram.savefig(circ_path)
        return

    def generate_equivalent_circuit(self):
        """
        Generate an equivalent circuit.

        Input:
            None
        
        Output:
            None
        """
        topo_ops = copy.deepcopy(self.topology.options)
        self.equivalent_circuit.generate_equ_circ_from_topo(topo_ops=topo_ops)
        return

    def generate_random_topo_edges(self, edges_num: int = None):
        """
        Generate random topology edges.

        Input:
            edges_num: int, the number of edges to generate, default is None (which may indicate generating a default number of edges).
        
        Output:
            None
        """
        self.topology.generate_random_edges(edges_num)
        return

    def generate_pins(self, **gene_ops):
        """
        Generate pins.

        Input:
            gene_ops: Dictionary, containing the parameters for generating pins.
        
        Output:
            None
        """
        self.gds.generate_pins(**gene_ops)
        return

    def custom_function(self, options1, options2):
        design_ops = self.options

        ################################ 
        # update design options (your code)
        ################################

        self.inject_options(design_ops)
        return