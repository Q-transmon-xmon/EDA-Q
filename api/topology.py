#########################  
#Quantum Chip Topology 
#########################


import networkx as nx
import matplotlib.pyplot as plt
from addict import Dict
from base.base import Base
import equ_circ, copy
import func_modules
import func_modules.topo
import func_modules.topo.primitives

class Topology(Base):
    """
    Defines and operates on the topology of a quantum chip, including nodes, edges, and visualization features.
    """

    def __init__(self, **init_ops):
        """
        Initializes the Topology object.

        Input:
            init_ops: dict, parameters for initializing the topology structure.

        Output:
            None
        """
        self.initialization(**init_ops)
        return

    def initialization(self, **init_ops):
        """
        Initializes the topology structure, including defining node positions, edges, number of rows, and columns.

        Input:
            init_ops: dict, initialization parameters for generating the topology.

        Output:
            None
        """
        # Initialize parameters
        super().__setattr__("positions", Dict())  # Node positions
        super().__setattr__("edges", [])  # Edge list
        super().__setattr__("col_num", 0)  # Number of columns
        super().__setattr__("row_num", 0)  # Number of rows
        # Save the list of parameter names
        super().__setattr__("op_name_list", list(self.__dict__.keys()))
        # Call the module to generate topology options
        options = func_modules.topo.generate_topology(**init_ops)
        self.inject_options(options)  # Inject the generated options
        return

    def extract_options(self):
        """
        Extract current option parameters from the topology structure.

        Input:
            None

        Output:
            options: Dict, containing option parameters for node positions and edges.
        """
        options = Dict()
        options.positions = copy.deepcopy(self.positions)  # Node positions
        options.edges = copy.deepcopy(self.edges)  # Edge list
        return copy.deepcopy(options)  # Return a deep copy of the options

    def inject_options(self, options):
        """
        Inject option parameters into the topology structure.

        Input:
            options: dict, containing node positions, edges, number of rows, and columns to be injected.

        Output:
            None
        """
        for k, v in options.items():
            if k == "positions":
                super().__setattr__(k, copy.deepcopy(v))
            elif k == "edges":
                super().__setattr__(k, copy.deepcopy(v))
            elif k == "col_num":
                super().__setattr__(k, copy.deepcopy(v))
            elif k == "row_num":
                super().__setattr__(k, copy.deepcopy(v))
        return

    def show_image(self):
        """
        Draw the topology structure image.

        Input:
            None

        Output:
            None
        """
        # Interface
        positions = copy.deepcopy(self.positions)  # Node positions
        edges = copy.deepcopy(self.edges)  # Edges
        nodes = list(self.positions.keys())  # Node list
        col_num = self.col_num
        row_num = self.row_num

        # Create graph
        G = nx.Graph()
        for node in nodes:
            G.add_node(node)  # Add node
        for edge in edges:
            G.add_edge(edge[0], edge[1])  # Add edge

        plt.figure(figsize=(0.8 * col_num + 5, 0.8 * row_num + 5))  # Set image size
        pos = {node: (positions[node][0], positions[node][1]) for node in nodes}  # Node position dictionary

        # Draw nodes and edges
        nx.draw_networkx_nodes(G, pos, node_size=500, node_color="#ccebc5")
        nx.draw_networkx_edges(G, pos, width=5, edge_color="#80b1d3")

        # Add node labels
        labels = {node: node for node in nodes}
        nx.draw_networkx_labels(G, pos, labels, font_size=10, font_color='black')

        plt.axis('off')
        plt.show()
        return

    def save_image(self, path: str = "./topology.png"):
        """
        Save the topology image as a PNG file.

        Input:
            path: str, the path to save the image, default is "./topology.png".

        Output:
            None
        """
        # Interface
        positions = copy.deepcopy(self.positions)
        edges = copy.deepcopy(self.edges)
        nodes = list(self.positions.keys())
        col_num = self.col_num
        row_num = self.row_num

        # Create graph
        G = nx.Graph()
        for node in nodes:
            G.add_node(node)
        for edge in edges:
            G.add_edge(edge[0], edge[1])

        plt.figure(figsize=(0.8 * col_num, 0.8 * row_num))
        pos = {node: (positions[node][0], positions[node][1]) for node in nodes}

        # Draw nodes and edges
        nx.draw_networkx_nodes(G, pos, node_size=500, node_color="#ccebc5")
        nx.draw_networkx_edges(G, pos, width=5, edge_color="#80b1d3")

        # Add node labels
        labels = {node: node for node in nodes}
        nx.draw_networkx_labels(G, pos, labels, font_size=10, font_color='black')

        plt.axis('off')

        # Save image
        import toolbox
        toolbox.jg_and_create_path(path)
        plt.savefig(path)
        return

    def change_equ_circ(self, **change_ops):
        """
        Modify the equivalent circuit parameters.

        Input:
            change_ops: dict, parameters for modifying the equivalent circuit.

        Output:
            equ_circ_ops: dict, the modified equivalent circuit parameters.
        """
        change_ops["equ_circ_ops"] = self.calc_equ_circ()  # Calculate the current parameters of the equivalent circuit
        equ_circ_ops = equ_circ.change_equ_circ(**change_ops)  # Modify the equivalent circuit
        return copy.deepcopy(equ_circ_ops)

    def show_equ_circ(self, equ_circ_ops):
        """
        Visualize and display the equivalent circuit.

        Input:
            equ_circ_ops: dict, parameters of the equivalent circuit.

        Output:
            None
        """
        equ_circ.show_equ_circ_image(equ_circ_ops)
        return

    def add_edge(self, q0_name, q1_name):
        """
        Add an edge.

        Input:
            q0_name: str, the name of the starting node.
            q1_name: str, the name of the ending node.

        Output:
            None
        """
        self.edges.append([q0_name, q1_name])
        return

    def remove_edge(self, edge: tuple = None):
        """
        Remove a specified edge.

        Input:
            edge: tuple, the edge to be removed.

        Output:
            None
        """
        print(self.edges)
        print("edge = {}".format(edge))
        self.edges.remove(edge)
        return

    def add_edges(self, edges: list = None):
        """
        Add edges in bulk.

        Input:
            edges: list, the list of edges to be added.

        Output:
            None
        """
        super().__setattr__("edges", self.edges + edges)
        return

    def calc_equ_circ(self):
        """
        Calculate the equivalent circuit parameters.

        Input:
            None

        Output:
            equ_circ_ops: dict, the calculated equivalent circuit parameters.
        """
        topo_ops = copy.deepcopy(self.options)
        equ_circ.generate_equ_circ(topo_ops)  # Call the module to calculate the equivalent circuit
        return

    def find_qname(self, pos):
        """
        Find the name of a qubit based on its position.

        Input:
            pos: tuple, the position coordinates of the node.

        Output:
            q: str, the corresponding qubit name. If not found, return None.
        """
        ops = self.options
        for q, p in ops.positions.items():
            if p == pos:
                return q
        print("No qubit found for {}".format(pos))
        return

    def if_edge(self, edge):
        """
        Determine if an edge exists in the current topology.

        Input:
            edge: list, two nodes representing the edge, e.g., [node1, node2].

        Output:
            bool: If the edge exists (including both orientations of an undirected edge), return True; otherwise, return False.
        """
        ops = self.options
        for e in ops.edges:
            if edge == e:
                return True
            else:
                eedge = [edge[1], edge[0]]  # Reverse edge
                if eedge == e:
                    return True
        return False

    def generate_random_edges(self, edges_num: int = None):
        """
        Generate random edges and inject them into the topology.

        Input:
            edges_num: int, the number of edges to generate. If None, use the default number.

        Output:
            None
        """
        topo_ops = copy.deepcopy(self.options)
        topo_ops.edges = func_modules.topo.generate_random_edges(topo_ops.positions, edges_num)  # Call the module to generate random edges
        self.inject_options(topo_ops)  
        return

    def batch_add_edges(self, y=None, x=None):
        """
        Batch add edges based on specified rows or columns.

        Input:
            y: int, the specified row number. If None, it is ignored.
            x: int, the specified column number. If None, it is ignored.

        Output:
            None

        Exception:
            ValueError: If the specified row or column is out of range.
        """
        max_y = 0  # Maximum row number
        max_x = 0  # Maximum column number
        old_ops = self.options

        # Get the maximum row and column numbers of all nodes
        for q, pos in old_ops.positions.items():
            max_y = max(max_y, pos[1])
            max_x = max(max_x, pos[0])
        
        # Check if the row or column is out of range
        if y is not None:
            if y > max_y:
                raise ValueError("Row overflow, y = {}, max_y = {}".format(y, max_y))
        if x is not None:
            if x > max_x:
                raise ValueError("Column overflow, x = {}, max_x = {}".format(x, max_x))

        new_ops = copy.deepcopy(old_ops)

        # Batch add edges in the row direction
        if y is not None:
            for x in range(0, max_x):
                if not self.if_edge([self.find_qname((x, y)), self.find_qname((x + 1, y))]):
                    new_ops.edges.append((self.find_qname((x, y)), self.find_qname((x + 1, y))))
        # Batch add edges in the column direction
        elif x is not None:
            for y in range(0, max_y):
                if not self.if_edge([self.find_qname((x, y)), self.find_qname((x, y + 1))]):
                    new_ops.edges.append((self.find_qname((x, y)), self.find_qname((x, y + 1))))
        else:
            raise ValueError("Either y or x must be specified!")  # If neither y nor x is specified, throw an exception

        self.inject_options(new_ops)  # Inject the new edges into the options
        return

    def batch_add_edges_list(self, y=None, x=None):
        """
        Batch add edges based on multiple specified rows or columns.

        Input:
            y: list, a list of specified row numbers. If None, it is ignored.
            x: list, a list of specified column numbers. If None, it is ignored.

        Output:
            None
        """
        if y is not None:
            for r in y:  # Iterate over all rows
                self.batch_add_edges(y=r)
        elif x is not None:
            for c in x:  # Iterate over all columns
                self.batch_add_edges(x=c)
        return

    def generate_hex_full_edges(self):
        """
        Generate edges based on the complete connection rules of hexagons.

        Input:
            None

        Output:
            None
        """
        self.edges = func_modules.topo.generate_hex_full_edges(self.positions)  # Call the module to generate edges connected by hexagons
        return
    
    def generate_topology1(self, num_rows: int = 4, num_cols: int = 4):
        num_qubits = num_rows * num_cols
        topo_positions = func_modules.topo.primitives.generate_topo_positions(qubits_num=num_qubits,
                                                                        topo_col = num_cols,
                                                                        topo_row = num_rows)
        topo_ops = Dict()
        topo_ops.positions = topo_positions
        self.inject_options(topo_ops)
        return
    
    def generate_full_edges(self):
        topo_ops = self.options
        edges = func_modules.topo.primitives.generate_full_edges(topo_ops.positions)
        topo_ops.edges = edges
        self.inject_options(topo_ops)
        return
    
    def custom_function(self, options1, options2):
        topo_ops = self.options

        ################################ 
        # update topology options (your code)
        ################################

        self.inject_options(topo_ops)
        return