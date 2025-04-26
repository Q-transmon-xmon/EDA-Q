from base.cmpnts_base import CmpntsBase
from addict import Dict
import gdspy
import toolbox
import func_modules
import routing
import copy

class Chips(CmpntsBase):
    """
    Chips class, inherited from CmpntsBase, used for managing and operating a collection of multiple chip components.
    """

    def __init__(self, **init_ops):
        """
        Initialize the Chips object.

        Input:
            init_ops: dict, parameters required for initialization.

        Output:
            None
        """
        self.initialization(**init_ops)  # Call initialization method
        return
    
    def initialization(self, **init_ops):
        """
        Initialize the set of chip components.

        Input:
            init_ops: dict, parameters for generating the set of chip components.

        Output:
            None
        """
        # Initialize component name list
        self.cmpnt_name_list = []
        # Call the function module to generate chip options
        options = func_modules.chips.generate_chips(**init_ops)
        self.inject_options(options)  # Inject parameters
        return
    
    def draw_gds(self):
        """
        Draw GDS layout for multiple chip components.

        Input:
            None

        Output:
            None
        """
        gdspy.library.use_current_library = False
        self.lib = gdspy.GdsLibrary()  # Create a new GDS library
        self.cell_Dict = Dict()

        # Generate lib for each component
        for cmpnt_name in self.cmpnt_name_list:
            cmpnt = getattr(self, cmpnt_name)
            cmpnt.draw_gds()

        # Traverse components, add each component to the corresponding chip cell center
        for cmpnt_name in self.cmpnt_name_list:
            cmpnt = getattr(self, cmpnt_name)
            chip_name = cmpnt.name
            if chip_name not in self.cell_Dict.keys():
                self.cell_Dict[chip_name] = self.lib.new_cell(chip_name)
            self.cell_Dict[chip_name].add(cmpnt.cell)

        # Layer by chip name (set layer number)
        for chip_name, cell in self.cell_Dict.items():
            layer_num = toolbox.custom_hash(chip_name)
            self.cell_Dict[chip_name].flatten(single_layer=layer_num, single_datatype=0)

        # Create an overall cell, and integrate all chip cells into the total cell center
        module_name = toolbox.convert_to_snake_case(self.__class__.__name__)
        self.cell = self.lib.new_cell(module_name)
        for chip_name, chip_cell in self.cell_Dict.items():
            self.cell.add(chip_cell)
        return
    
    def change_size_from_Flipichip_routing(self, chip_name, qubits_ops, rdls_ops):
        """
        Adjust chip size based on Flipchip routing.

        Input:
            chip_name: str, chip name.
            qubits_ops: dict, option parameters for quantum bits.
            rdls_ops: dict, option parameters for readout lines.

        Output:
            None

        Current Logic:
            Call routing.Flipchip's calculate_chip_size method to adjust chip size (specific logic not implemented).
        """
        chip_ops = copy.deepcopy(getattr(self, chip_name).options)  # Extract chip parameters
        routing.Flipchip.calculate_chip_size()  # Call the routing module to calculate the chip size
        return
    
    def change_size_from_pins(self, chip_name, pins_ops):
        """
        Adjust chip size based on pin positions.

        Input:
            chip_name: str, chip name.
            pins_ops: dict, option parameters for pins.

        Output:
            None

        Current Logic:
            Call routing.Flipchip's calculate_chip_size method to adjust chip size (specific logic not implemented).
        """
        chip_ops = copy.deepcopy(getattr(self, chip_name).options)  # Extract chip parameters
        routing.Flipchip.calculate_chip_size()  # Call the routing module to calculate the chip size
        return
    
    def generate(self, **gene_ops):
        """
        Add a new chip component based on the generated parameters.

        Input:
            gene_ops: dict, parameters for generating the chip.

        Output:
            None
        """
        chip_ops = func_modules.chips.generate_chip(**gene_ops)  # Call the function module to generate chip options
        chip_name = chip_ops.name  # Get chip name
        chips_ops = copy.deepcopy(self.options)  # Get options for the current chip set
        chips_ops[chip_name] = copy.deepcopy(chip_ops)  # Add the new chip to the option dictionary
        self.inject_options(chips_ops)  # Inject updated options
        return
    
    def copy_chip(self, old_chip_name, new_chip_name):
        """
        Copy an existing chip component.

        Input:
            old_chip_name: str, original chip name to be copied.
            new_chip_name: str, the name of the new chip.

        Output:
            None
        """
        chips_ops = self.extract_options()  # Extract parameters of the current chip set
        chips_ops[new_chip_name] = copy.deepcopy(chips_ops[old_chip_name])  # Copy the original chip parameters
        chips_ops[new_chip_name].name = new_chip_name  # Update the name of the new chip
        self.inject_options(chips_ops)  # Inject updated parameters
        return
