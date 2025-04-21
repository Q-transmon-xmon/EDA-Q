############################################################################
#GDS layout object, including comprehensive operation methods for the layout.
############################################################################


from addict import Dict
from base.gds_base import GdsBase
import func_modules.cpls
import func_modules.qubits
import func_modules.qubits.primitives
import components, copy, func_modules, gdspy, routing
import toolbox
import simulation as sim

class Gds(GdsBase):
    """
    A GDS layout object that includes comprehensive operation methods for the layout.
    """

    def __init__(self, **init_ops):
        """
        Initializes the GDS object.

        Input:
            init_ops: dict, parameters used to initialize the GDS object.

        Output:
            None
        """
        self.initialization(**init_ops)
        return

    def initialization(self, **init_ops):
        """
        Initializes the GDS layout, including the creation of components and injection of parameters.

        Input:
            init_ops: dict, initialization parameters for generating the GDS layout.
        
        Output:
            None
        """
        # Retrieve the list of component names
        self.cmpnts_name_list = copy.deepcopy(components.module_name_list)
        # Dynamically create components
        for cmpnts_name in self.cmpnts_name_list:
            cmpnts_class_name = toolbox.convert_to_camel_case(cmpnts_name)
            cmpnts_class = getattr(components, cmpnts_class_name)
            super().__setattr__(cmpnts_name, cmpnts_class())
        # Initialize parameters
        options = func_modules.gds.generate_gds(**init_ops)
        self.inject_options(options)
        return
    
    def clear(self):
        """
        Clear the content of all components.

        Input:
            None

        Output:
            None
        """
        for cmpnts_name in self.cmpnts_name_list:
            getattr(self, cmpnts_name).clear()

    def extract_options(self):
        """
        Extract option parameters from components.

        Input:
            None

        Output:
            options: Dict, containing option parameters for all components.
        """
        options = Dict()
        for cmpnts_name in self.cmpnts_name_list:
            options[cmpnts_name] = getattr(self, cmpnts_name).options
        return copy.deepcopy(options)

    def inject_options(self, options):
        """
        Inject option parameters into components.

        Input:
            options: dict, containing option parameters for each component.

        Output:
            None
        """
        options = copy.deepcopy(options)
        self.clear()
        for cmpnts_name, cmpnts_ops in options.items():
            cmpnts_class_name = toolbox.convert_to_camel_case(cmpnts_name)
            cmpnts_class = getattr(components, cmpnts_class_name)
            super().__setattr__(cmpnts_name, cmpnts_class(options=cmpnts_ops))
        return

    def draw_gds(self):
        """
        Generate GDS layout based on component composition.

        Input:
            None

        Output:
            None
        """
        gdspy.library.use_current_library = False
        self.lib = gdspy.GdsLibrary()
        self.cell_Dict = Dict()
        # Draw GDS for each component
        for cmpnts_name in self.cmpnts_name_list:
            cmpnts = getattr(self, cmpnts_name)
            cmpnts.draw_gds()
        # Add each component's cell to the library
        for cmpnts_name in self.cmpnts_name_list:
            cmpnts = getattr(self, cmpnts_name)
            cmpnts_cell_Dict = copy.deepcopy(cmpnts.cell_Dict)
            for cell_name, cell in cmpnts_cell_Dict.items():
                if cell_name not in self.cell_Dict.keys():  # If the cell does not exist, create a new one
                    self.cell_Dict[cell_name] = self.lib.new_cell(cell_name)
                self.cell_Dict[cell_name].add(cell)
        # Layer by chip name
        for chip_name, cell in self.cell_Dict.items():
            layer_num = toolbox.custom_hash(chip_name)
            self.cell_Dict[chip_name].flatten(single_layer=layer_num, single_datatype=0)
        # Create the overall cell
        module_name = toolbox.convert_to_snake_case(self.__class__.__name__)
        self.cell = self.lib.new_cell(module_name)
        for chip_name, chip_cell in self.cell_Dict.items():
            self.cell.add(chip_cell)
        return

    def calc_general_ops(self):
        """
        Calculate general operations for all components.

        Input:
            None

        Output:
            None
        """
        for cmpnts_name in self.cmpnts_name_list:
            getattr(self, cmpnts_name).calc_general_ops()
        return

    def generate_qubits_from_topo(self, **gene_ops):
        """
        Generate qubits based on topology (deprecated, compatible with old versions).

        Input:
            gene_ops: dict, containing parameters for generating qubits.

        Output:
            None
        """
        ops = copy.deepcopy(self.options)
        ops.qubits = func_modules.qubits.generate_qubits_from_topo(**gene_ops)
        self.inject_options(ops)
        return
    
    def generate_qubits_from_topo1(self,
                                   topo_positions: Dict,
                                   qubits_type: str = "Transmon", 
                                   chip_name: str = "chip0", 
                                   dist: float = 2000):
        ops = self.options
        ops.qubits = func_modules.qubits.primitives.generate_qubits_from_topo(topo_positions=topo_positions,
                                                                              chip_name=chip_name,
                                                                              dist=dist,
                                                                              qubits_type=qubits_type)
        self.inject_options(ops)
        return
        
    def generate_qubits(self, **gene_ops):
        """
        Generate qubits.

        Input:
            gene_ops: dict, containing configurations for qubit parameters.
            
        Output:
            None
        """
        self.qubits.initialization(**gene_ops)
        return

    def generate_coupling_lines_from_qubits(self, **gene_ops):
        """
        Generate coupling lines based on qubits (forward compatible).

        Input:
            gene_ops: dict, containing parameters for generating coupling lines.
            
        Output:
            None
        """
        gene_ops["qubits_ops"] = copy.deepcopy(self.qubits.options)
        gds_ops = copy.deepcopy(self.options)
        gds_ops.coupling_lines = getattr(components, "CouplingLines")(**gene_ops).options
        self.inject_options(gds_ops)
        return
    
    def generate_coupling_lines_from_topo_and_qubits(self,
                                                     topo_ops: Dict,
                                                     cpls_type: str = "CouplineLineStraight",
                                                     chip_name: str = "chip0"):
        ops = self.options
        qubits_ops = ops.qubits
        cpls_ops = func_modules.cpls.primitives.generate_cpls(topo_ops=topo_ops,
                                                              qubits_ops=qubits_ops,
                                                              cpls_type=cpls_type,
                                                              chip_name=chip_name)
        ops.coupling_lines = cpls_ops
        self.inject_options(ops)
        return

    def generate_coupling_lines(self, **gene_ops):
        """
        Generate coupling lines.

        Input:
            gene_ops: dict, containing parameters for generating coupling lines.
            
        Output:
            None
        """
        if "qubits" in gene_ops.keys():
            if gene_ops["qubits"] == True:
                qubits_ops = copy.deepcopy(self.qubits.options)
                gene_ops["qubits_ops"] = copy.deepcopy(qubits_ops)
            del gene_ops["qubits"]
        
        self.coupling_lines.initialization(**gene_ops)
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
        Add a coupling line.

        Input:
            q0_name: str, the name of qubit 0.
            q0_pin_num: int, the pin number of qubit 0.
            q1_name: str, the name of qubit 1.
            q1_pin_num: int, the pin number of qubit 1.
            cp_type: str, the type of coupling line.
            chip: str, the name of the chip.
            geometric_ops: dict, the configuration of geometric parameters.
            
        Output:
            None
        """
        ops = self.options
        q0_ops = copy.deepcopy(ops.qubits[q0_name])
        q1_ops = copy.deepcopy(ops.qubits[q1_name])

        cpl_ops = func_modules.cpls.add_cpl(q0_ops=q0_ops,
                                                q0_pin_num=q0_pin_num,
                                                q1_ops=q1_ops,
                                                q1_pin_num=q1_pin_num,
                                                cp_type=cp_type,
                                                chip=chip,
                                                geometric_ops=geometric_ops)

        ops.coupling_lines[cpl_ops.name] = copy.deepcopy(cpl_ops)
        self.inject_options(ops)
        return

    def routing(self, **routing_ops):
        """
        Perform routing operations.

        Input:
            routing_ops: dict, containing parameters for routing operations, such as signal line layout, topology information, etc.

        Output:
            None
        """
        gds_ops = self.options
        routing_ops["gds_ops"] = copy.deepcopy(gds_ops)  # Pass GDS options as routing parameters
        gds_ops = routing.routing(**routing_ops)  # Call the routing module to generate routing information
        self.inject_options(gds_ops)  # Update GDS options
        return

    def add_chip(self, chip_name: str = "chip0", chip_type: str = "RecChip", geometric_ops: Dict = Dict()):
        """
        Add chip information to the GDS object.

        Input:
            chip_name: str, the name of the chip, default is "chip0".
            chip_type: str, the type of the chip, default is "RecChip".
            geometric_ops: Dict, the configuration of geometric parameters.

        Output:
            None
        """
        ops = self.options
        new_chip_ops = func_modules.chips.generate_chip_ops(chip_name=chip_name, 
                                                            chip_type=chip_type, 
                                                            geometric_ops=geometric_ops)
        ops.chips[chip_name] = copy.deepcopy(new_chip_ops)  # Add parameters for the new chip
        self.inject_options(ops)  # Update GDS options
        return

    def copy_chip(self, old_chip_name, new_chip_name):
        """
        Copy the parameters of an existing chip and create a new chip.

        Input:
            old_chip_name: str, the name of the old chip.
            new_chip_name: str, the name of the new chip.

        Output:
            None
        """
        gds_ops = copy.deepcopy(self.options)
        gds_ops.chips[new_chip_name] = copy.deepcopy(gds_ops.chips[old_chip_name])  # Copy chip parameters
        gds_ops.chips[new_chip_name].name = new_chip_name  # Update the name of the new chip
        self.inject_options(gds_ops)  # Update GDS options
        return

    def generate_readout_lines_from_qubits(self, **gene_ops):
        """
        Generate readout lines from qubits (backward compatible).

        Input:
            gene_ops: dict, containing parameters needed to generate readout lines.

        Output:
            None
        """
        gds_ops = copy.deepcopy(self.options)
        gene_ops["qubits_ops"] = copy.deepcopy(gds_ops.qubits)  # Pass qubit parameters
        gds_ops.readout_lines = getattr(components, "ReadoutLines")(**gene_ops).options  # Call component to generate readout lines
        self.inject_options(gds_ops)  # Update GDS options
        return

    def generate_readout_lines(self, **gene_ops):
        """
        Generate readout lines.

        Input:
            gene_ops: dict, containing parameters for generating readout lines, such as qubit parameters.

        Output:
            None
        """
        if "qubits" in gene_ops.keys():
            if gene_ops["qubits"] == True:
                gene_ops["qubits_ops"] = copy.deepcopy(self.qubits.options)  # Pass qubit parameters
            del gene_ops["qubits"]
        self.readout_lines.initialization(**gene_ops)  # Initialize readout lines
        return

    def generate_chip_from_qubits(self, **gene_ops):
        """
        Deprecated method: Generate a chip from qubits (compatible with old versions).

        Input:
            gene_ops: dict, containing parameters for generating a chip.

        Output:
            None
        """
        gds_ops = copy.deepcopy(self.options)
        qubits_ops = copy.deepcopy(gds_ops.qubits)
        chips_ops = copy.deepcopy(gds_ops.chips)

        gene_ops["qubits_ops"] = qubits_ops  # Pass qubit parameters
        new_chip_ops = func_modules.chips.generate_chip_ops(**gene_ops)  # Generate new chip parameters
        new_chip_name = new_chip_ops.name
        chips_ops[new_chip_name] = copy.deepcopy(new_chip_ops)  # Add new chip parameters

        gds_ops.chips = copy.deepcopy(chips_ops)  # Update chip options
        self.inject_options(gds_ops)
        return

    def generate_chip(self, **gene_ops):
        """
        Generate a chip.

        Input:
            gene_ops: dict, containing parameters for generating a chip.

        Output:
            None
        """
        gds_ops = copy.deepcopy(self.options)
        if "qubits" in gene_ops.keys():
            if gene_ops["qubits"] == True:
                qubits_ops = copy.deepcopy(gds_ops.qubits)
                gene_ops["qubits_ops"] = copy.deepcopy(qubits_ops)  # Pass qubit parameters
            del gene_ops["qubits"]
        self.chips.generate(**gene_ops)  # Call chip generation method
        return

    def change_qubits_type(self, qubits_type):
        """
        Change the type of qubits.

        Input:
            qubits_type: str, the new type of qubits.

        Output:
            None
        """
        self.qubits.change_qubits_type(qubits_type)  # Call the qubit module to change the type
        return

    def simulation(self, **sim_ops):
        """
        Perform simulation operations.

        Input:
            sim_ops: dict, containing parameters for simulation operations.

        Output:
            None
        """
        sim_ops["gds_ops"] = copy.deepcopy(self.options)  # Pass GDS options
        sim.simulation(**sim_ops)  # Call the simulation module
        return

    def change_chip_size_from_Flipchip_routing(self):
        """
        Change the size of the chip based on Flipchip routing.

        Input:
            None

        Output:
            None
        """
        gds_ops = copy.deepcopy(self.options)
        qubits_ops = copy.deepcopy(gds_ops.qubits)
        rdls_ops = copy.deepcopy(gds_ops.readout_lines)
        # Future logic implementation
        return

    def generate_cross_overs_from_cpls_and_tmls(self, **gene_ops):
        """
        Generate crossovers (compatible with old versions).

        Input:
            gene_ops: dict, containing parameters for generating crossovers.

        Output:
            None
        """
        gds_ops = copy.deepcopy(self.options)
        gene_ops["cpls_ops"] = copy.deepcopy(gds_ops.coupling_lines)  # Pass coupling line parameters
        gene_ops["tmls_ops"] = copy.deepcopy(gds_ops.transmission_lines)  # Pass transmission line parameters
        self.cross_overs.generate_cross_overs(**gene_ops)  # Call the crossover generation method
        return

    def generate_cross_overs(self, **gene_ops):
        """
        Generate crossovers.

        Input:
            gene_ops: dict, containing parameters for generating crossovers.

        Output:
            None
        """
        if "coupling_lines" in gene_ops.keys():
            if gene_ops["coupling_lines"] == True:
                gene_ops["cpls_ops"] = copy.deepcopy(self.coupling_lines.options)  # Pass coupling line parameters
            del gene_ops["coupling_lines"]
        if "transmission_lines" in gene_ops.keys():
            if gene_ops["transmission_lines"] == True:
                gene_ops["tmls_ops"] = copy.deepcopy(self.transmission_lines.options)  # Pass transmission line parameters
            del gene_ops["transmission_lines"]
        self.cross_overs.initialization(**gene_ops)  # Initialize crossovers
        return

    def auto_generate_indium_bumps(self, coord1, coord2, min_distance_points, min_distance_polygons, chip_name, type):
        """
        Automatically generate indium bumps.

        Input:
            coord1: list, the first set of coordinates.
            coord2: list, the second set of coordinates.
            min_distance_points: float, the minimum distance between points.
            min_distance_polygons: float, the minimum distance between polygons.
            chip_name: str, the name of the chip.
            type: str, the type of bump.

        Output:
            None
        """
        gds_ops = self.options
        temp_gds_file = self.save_gds("./for_auto_gene_indium.gds")  # Save temporary GDS file

        indium_ops = func_modules.indium_bumps.indium_primitive.process_gds_with_indium_optimized(
            temp_gds_file, 
            coord1, 
            coord2, 
            min_distance_points, 
            min_distance_polygons,
            chip_name,
            type
        )
        gds_ops.indium_bumps = copy.deepcopy(indium_ops)  # Save generated indium bump parameters
        self.inject_options(gds_ops)  # Update GDS options
        return

    def auto_generate_air_bridge(self, line_type, line_name, spacing=120, chip_name="chip3"):
        """
        Automatically generate an air bridge.

        Input:
            line_type: str, the type of line, supports "control_lines" or "transmission_lines".
            line_name: str, the name of the line.
            spacing: float, the spacing of the air bridge, default is 120.
            chip_name: str, the name of the chip, default is "chip3".

        Output:
            None
        """
        allow_type_list = ["control_lines", "transmission_lines"]
        if line_type not in allow_type_list:
            raise ValueError("Automatic generation of air bridges for {} has not been developed.".format(line_type))
        
        gds_ops = self.options
        line_ops = copy.deepcopy(gds_ops[line_type][line_name])  # Get line parameters
        
        if "pos" in line_ops.keys():
            path = gds_ops[line_type][line_name].pos
        elif "path" in line_ops.keys():
            path = gds_ops[line_type][line_name].path
        else:
            print(line_ops.keys())
            raise ValueError("The selected component properties do not have pos or path, unable to automatically generate an air bridge.")

        corner_radius = gds_ops[line_type][line_name].corner_radius
        ab_ops = func_modules.others.air_bridge_primitive.add_air_bridges(path, corner_radius, spacing, chip_name)  # Generate air bridge
        gds_ops.others.update(ab_ops)  # Update other component parameters
        self.inject_options(gds_ops)  # Update GDS options
        return

    def auto_generate_air_bridge2(self, line_type, line_name, spacing=120, chip_name="chip3", width=10, air_bridge_type="AirBridge"):
        """
        Automatically generate an air bridge (advanced version).

        Input:
            line_type: str, the type of line, supports "control_lines" or "transmission_lines".
            line_name: str, the name of the line.
            spacing: float, the spacing of the air bridge, default is 120.
            chip_name: str, the name of the chip, default is "chip3".
            width: float, the width of the air bridge, default is 10.
            air_bridge_type: str, the type of air bridge, default is "AirBridge".

        Output:
            None
        """
        allow_type_list = ["control_lines", "transmission_lines"]
        if line_type not in allow_type_list:
            raise ValueError("Automatic generation of air bridges for {} has not been developed.".format(line_type))
        
        gds_ops = self.options
        line_ops = copy.deepcopy(gds_ops[line_type][line_name])  # Get line parameters
        
        if "pos" in line_ops.keys():
            path = gds_ops[line_type][line_name].pos
        elif "path" in line_ops.keys():
            path = gds_ops[line_type][line_name].path
        else:
            print(line_ops.keys())
            raise ValueError("The selected component properties do not have pos or path, unable to automatically generate an air bridge.")

        corner_radius = gds_ops[line_type][line_name].corner_radius
        ab_ops = func_modules.air_bridges.auto_generate_air_bridges_ops(gds_ops=gds_ops,
                                                                        line_type=line_type,
                                                                        line_name=line_name,
                                                                        spacing=spacing,
                                                                        chip_name=chip_name,
                                                                        width=width,
                                                                        air_bridge_type=air_bridge_type)
        gds_ops.air_bridges = copy.deepcopy(ab_ops)
        self.inject_options(gds_ops)
        return
    
    def auto_generate_air_bridge3(self, line_type, line_name, spacing=120, chip_name="chip3", width=10, air_bridge_type="AirBridgeNb"):
        """
        Automatically generate an air bridge (advanced version).

        Input:
            line_type: str, the type of line, supports "control_lines" or "transmission_lines".
            line_name: str, the name of the line.
            spacing: float, the spacing of the air bridge, default is 120.
            chip_name: str, the name of the chip, default is "chip3".
            width: float, the width of the air bridge, default is 10.
            air_bridge_type: str, the type of air bridge, default is "AirBridgeNb".

        Output:
            None
        """
        allow_type_list = ["control_lines", "transmission_lines"]
        if line_type not in allow_type_list:
            raise ValueError("Automatic generation of air bridges for {} has not been developed.".format(line_type))
        
        gds_ops = self.options
        line_ops = copy.deepcopy(gds_ops[line_type][line_name])  # Get line parameters
        
        if "pos" in line_ops.keys():
            path = gds_ops[line_type][line_name].pos
        elif "path" in line_ops.keys():
            path = gds_ops[line_type][line_name].path
        else:
            print(line_ops.keys())
            raise ValueError("The selected component properties do not have pos or path, unable to automatically generate an air bridge.")

        corner_radius = gds_ops[line_type][line_name].corner_radius
        ab_ops = func_modules.air_bridges.auto_generate_air_bridges_ops(gds_ops=gds_ops,
                                                                        line_type=line_type,
                                                                        line_name=line_name,
                                                                        spacing=spacing,
                                                                        chip_name=chip_name,
                                                                        width=width,
                                                                        air_bridge_type=air_bridge_type)
        gds_ops.air_bridges = copy.deepcopy(ab_ops)
        self.inject_options(gds_ops)
        return
    
    def auto_generate_air_bridge4(self, line_type, line_name, spacing=120, chip_name="chip3", width=10, air_bridge_type="AirBridgeNb"):
        """
        Automatically generate an air bridge (advanced version).

        Input:
            line_type: str, the type of line, supports "control_lines" or "transmission_lines".
            line_name: str, the name of the line.
            spacing: float, the spacing of the air bridge, default is 120.
            chip_name: str, the name of the chip, default is "chip3".
            width: float, the width of the air bridge, default is 10.
            air_bridge_type: str, the type of air bridge, default is "AirBridgeNb".

        Output:
            None
        """
        allow_type_list = ["control_lines", "transmission_lines"]
        if line_type not in allow_type_list:
            raise ValueError("Automatic generation of air bridges for {} has not been developed.".format(line_type))
        
        gds_ops = self.options
        line_ops = copy.deepcopy(gds_ops[line_type][line_name])  # Get line parameters
        
        if "pos" in line_ops.keys():
            path = gds_ops[line_type][line_name].pos
        elif "path" in line_ops.keys():
            path = gds_ops[line_type][line_name].path
        else:
            print(line_ops.keys())
            raise ValueError("The selected component properties do not have pos or path, unable to automatically generate an air bridge.")

        corner_radius = gds_ops[line_type][line_name].corner_radius
        ab_ops = func_modules.air_bridges.auto_generate_air_bridges_ops2(gds_ops=gds_ops,
                                                                         line_type=line_type,
                                                                         line_name=line_name,
                                                                         spacing=spacing,
                                                                         chip_name=chip_name,
                                                                         width=width,
                                                                         air_bridge_type=air_bridge_type)
        gds_ops.air_bridges = copy.deepcopy(ab_ops)
        self.inject_options(gds_ops)
        return
    
    def auto_generate_air_bridge5(self, line_type, line_name, spacing=120, chip_name="chip3", width=10, air_bridge_type="AirBridgeNb"):
        """
        Automatically generate an air bridge (advanced version).

        Input:
            line_type: str, the type of line, supports "control_lines" or "transmission_lines".
            line_name: str, the name of the line.
            spacing: float, the spacing of the air bridge, default is 120.
            chip_name: str, the name of the chip, default is "chip3".
            width: float, the width of the air bridge, default is 10.
            air_bridge_type: str, the type of air bridge, default is "AirBridgeNb".

        Output:
            None
        """

        # parameters preparation
        gds_ops = self.options

        # Compatible with path and pos
        line_ops = copy.deepcopy(gds_ops[line_type][line_name])  # Get line parameters
        allow_type_list = ["control_lines", "transmission_lines"]
        if line_type not in allow_type_list:
            raise ValueError("Automatic generation of air bridges for {} has not been developed.".format(line_type))
        
        if "pos" in line_ops.keys():
            path = gds_ops[line_type][line_name].pos
        elif "path" in line_ops.keys():
            path = gds_ops[line_type][line_name].path
        else:
            print(line_ops.keys())
            raise ValueError("The selected component properties do not have pos or path, unable to automatically generate an air bridge.")

        # operation
        new_gds_ops = func_modules.air_bridges.auto_generate_air_bridges_ops3(gds_ops)
        self.inject_options(new_gds_ops)
        return
    
    def get_gds_bounding_box(self):
        min_coor, max_coor = toolbox.get_cell_bounding_box(self.cell)
        return min_coor, max_coor
    
    def custom_function(self, options1, options2):
        gds_ops = self.options

        ################################ 
        # update gds options (your code)
        ################################

        self.inject_options(gds_ops)
        return
    
    def custom_routing_method(self):
        gds_ops = self.options
        new_gds_ops = routing.new_routing_method(gds_ops)
        self.inject_options(gds_ops)
        return
    
    def custom_sim_method(self):
        gds_ops = self.options
        sim.new_sim_method(gds_ops)
        return
    
    def new_sim_method(self):
        gds_ops = self.options
        sim.new_sim_method(gds_ops)
        return
    
    def generate_qubits_1(self,
                          num: int,
                          num_cols: int,
                          num_rows: int,
                          type: str = "Transmon",
                          chip: str = "default_layer",
                          dist: int = 2000,
                          geometric_options: Dict = Dict()):
        gds_ops = self.options
        qubits_ops = func_modules.qubits.generate_qubits_1(num=num,
                                                           num_cols=num_cols,
                                                           num_rows=num_rows,
                                                           type=type,
                                                           chip=chip,
                                                           dist=dist,
                                                           geometric_options=geometric_options)
        gds_ops.qubits = qubits_ops
        self.inject_options(gds_ops)
        return
    
    def metal_lom_qubit_cpw(self, name_qubit, name_cpw):
        gds_ops = self.options
        sim.metal_lom_qubit_cpw(gds_ops=gds_ops,
                                name_qubit=name_qubit,
                                name_cpw=name_cpw)
        return