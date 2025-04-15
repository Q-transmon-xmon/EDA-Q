############################
#a base class for components
############################

from addict import Dict
import copy, gdspy, library
from base.gds_base import GdsBase
import toolbox


class CmpntsBase(GdsBase):
    """
    The CmpntsBase class, a base class for components, includes common methods for all components.
    """

    def __init__(self, **init_ops):
        """
        Initializes the CmpntsBase object.
        """
        return

    def clear(self):
        """
        Clears all component instances and the name list.

        Input:
            None

        Output:
            None
        """
        for cmpnt_name in self.cmpnt_name_list:
            delattr(self, cmpnt_name)  # Delete component attributes
        self.cmpnt_name_list.clear()  # Clear the component name list
        return

    def extract_options(self):
        """
        Extracts parameters from each component and combines them into a parameter dictionary.

        Input:
            None

        Output:
            options: Dict, a dictionary containing parameters of all components.
        """
        options = Dict()
        for cmpnt_name in self.cmpnt_name_list:
            cmpnt_inst = getattr(self, cmpnt_name)  # Get component instance
            options[cmpnt_name] = copy.deepcopy(getattr(cmpnt_inst, "options"))  # Deep copy parameters
        return copy.deepcopy(options)

    def inject_options(self, options):
        """
        Injects component parameters into component instances.

        Input:
            options: dict, a dictionary containing component parameters.

        Output:
            None

        Exception:
            ValueError: Throws an exception when the component type is empty or not defined in the library.
        """
        options = copy.deepcopy(options)
        self.clear()  # Clear existing components
        for cmpnt_name, cmpnt_ops in options.items():
            cmpnt_type = cmpnt_ops.type

            ### Error checking ###
            if cmpnt_type == Dict():
                raise ValueError("{}'s type is empty!".format(cmpnt_name))  # Exception for empty type

            module_name = toolbox.convert_to_snake_case(self.__class__.__name__)
            module_name_list = getattr(getattr(library, module_name), "module_name_list")
            class_name_list = [toolbox.convert_to_camel_case(i) for i in module_name_list]
            if cmpnt_type not in class_name_list:
                raise ValueError("{} not in {}".format(cmpnt_type, class_name_list))  # Exception for undefined type

            ### Inject component instances ###
            super().__setattr__(cmpnt_name, getattr(getattr(library, module_name), cmpnt_type)(options=cmpnt_ops))
            self.cmpnt_name_list.append(cmpnt_name)
        return

    def draw_gds(self):
        """
        Draws the GDS layout of the components.

        Input:
            None

        Output:
            None
        """
        gdspy.library.use_current_library = False
        self.lib = gdspy.GdsLibrary()
        self.cell_Dict = Dict()

        # Generate libs for each component
        for cmpnt_name in self.cmpnt_name_list:
            cmpnt = getattr(self, cmpnt_name)
            cmpnt.draw_gds()

        # Traverse components and add component cells by chip
        for cmpnt_name in self.cmpnt_name_list:
            cmpnt = getattr(self, cmpnt_name)
            chip_name = cmpnt.chip
            if chip_name is None or chip_name == Dict():
                chip_name = "None"
            if chip_name not in self.cell_Dict.keys():
                self.cell_Dict[chip_name] = self.lib.new_cell(chip_name)
            self.cell_Dict[chip_name].add(cmpnt.cell)

            # Special handling for qubit's jj_chip
            if hasattr(cmpnt, "jj_cell"):
                jj_chip_name = cmpnt.jj_chip
                if jj_chip_name is None or jj_chip_name == Dict():
                    jj_chip_name = "None"
                if jj_chip_name not in self.cell_Dict.keys():
                    self.cell_Dict[jj_chip_name] = self.lib.new_cell(jj_chip_name)
                self.cell_Dict[jj_chip_name].add(cmpnt.jj_cell)

        # Layer by chip
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
        Calculates common parameters for each component.

        Input:
            None

        Output:
            None
        """
        for cmpnt_name in self.cmpnt_name_list:
            getattr(self, cmpnt_name).calc_general_ops()
        return

    def move(self, pos_name, dx: float = 0, dy: float = 0):
        """
        Moves components by a specified displacement.

        Input:
            pos_name: str, the name of the position parameter to move.
            dx: float, displacement in the x-direction.
            dy: float, displacement in the y-direction.

        Output:
            None
        """
        for cmpnt_name in self.cmpnt_name_list:
            cmpnt_ops = copy.deepcopy(getattr(self, cmpnt_name).options)
            pos = copy.deepcopy(cmpnt_ops[pos_name])
            pos = list(pos)
            pos = (pos[0] + dx, pos[1] + dy)
            cmpnt_ops[pos_name] = copy.deepcopy(pos)
            getattr(self, cmpnt_name).inject_options(cmpnt_ops)
        return

    def change_option(self, op_name, op_value):
        """
        Modifies the value of a single option.

        Input:
            op_name: str, the name of the option to modify.
            op_value: any type, the new value.

        Output:
            None
        """
        for cmpnt_name in self.cmpnt_name_list:
            cmpnt_ops = copy.deepcopy(getattr(self, cmpnt_name).options)
            cmpnt_ops[op_name] = copy.deepcopy(op_value)
            getattr(self, cmpnt_name).inject_options(cmpnt_ops)
            self.calc_general_ops()  # Recalculate common parameters
        return

    def change_options(self, new_options):
        """
        Modifies the values of multiple options.

        Input:
            new_options: dict, containing the names and values of options to modify.

        Output:
            None
        """
        new_options = copy.deepcopy(new_options)
        for cmpnt_name in self.cmpnt_name_list:
            cmpnt_ops = copy.deepcopy(getattr(self, cmpnt_name).options)
            for op_name, op_value in new_options.items():
                cmpnt_ops[op_name] = copy.deepcopy(op_value)
            getattr(self, cmpnt_name).inject_options(cmpnt_ops)
            self.calc_general_ops()  # Recalculate common parameters
        return

    def add(self, options):
        """
        Adds a new component.

        Input:
            options: dict, containing parameters for the new component.

        Output:
            None

        Exception:
            ValueError: Throws an exception when the component name or type is not specified.
        """
        name = options.name
        type = options.type

        # Error checking
        if name is None:
            raise ValueError("Please specify a name!")
        if type is None:
            raise ValueError("Please specify a type")

        old_ops = copy.deepcopy(self.options)
        new_ops = copy.deepcopy(old_ops)

        new_ops[name] = copy.deepcopy(options)
        self.inject_options(new_ops)
        return

    def copy_component(self, old_name, new_name):
        """
        Copies a specified component.

        Input:
            old_name: str, the name of the original component.
            new_name: str, the name of the new component.

        Output:
            None
        """
        ops = self.options
        ops[new_name] = copy.deepcopy(ops[old_name])
        self.inject_options(ops)
        return

    def generate_row(self, start_pos, dist, key, num, pre_name, type, geometric_options: Dict = None):
        """
        Generates a row of components.

        Input:
            start_pos: tuple, the starting position.
            dist: float, the distance between adjacent components.
            key: str, the key name of the position parameter.
            num: int, the number of components.
            pre_name: str, the prefix of the component name.
            type: str, the type of component.
            geometric_options: dict, the configuration of geometric parameters (optional).

        Output:
            None
        """
        ops = self.options
        for i in range(num):
            op = Dict()
            name = pre_name + "_{}".format(i)
            op.name = name
            op.type = type
            pos = (start_pos[0] + i * dist, start_pos[1])
            op[key] = copy.deepcopy(pos)
            if geometric_options is not None:
                for k, v in geometric_options.items():
                    op[k] = copy.deepcopy(v)
            ops[name] = copy.deepcopy(op)
        self.inject_options(ops)
        return 

    def generate_row_middle(self, mid_pos, dist, key, num, pre_name, type, geometric_options: Dict = None):
        ops = self.options
        # 生成坐标点的集合
        pos_list = []
        for i in range(num):
            pos = (mid_pos[0]+i*dist, mid_pos[1])
            pos_list.append(copy.deepcopy(pos))
        move_dist = (pos_list[0][0] + pos_list[-1][0]) / 2
        for i in range(num):
            pos = copy.deepcopy(pos_list[i])
            pos_list[i] = (pos[0]-move_dist, pos[1])
        # print(pos_list)
        # 生成每个组件的参数
        for i in range(num):
            op = Dict()
            name = pre_name + "_{}".format(i)
            op.name = name
            op.type = type
            pos = copy.deepcopy(pos_list[i])
            op[key] = copy.deepcopy(pos)
            if geometric_options is not None:
                for k, v in geometric_options.items():
                    op[k] = copy.deepcopy(v)
            ops[name]  = copy.deepcopy(op)
        self.inject_options(ops)
        return
    
    def batch_generate(self, pos_list, key, pre_name, type, geometric_options: Dict = None):
        """
        Batch generate components.

        Input:
            pos_list: list, a list containing the positions of the components.
            key: str, the key name for the position parameter.
            pre_name: str, the prefix for the component names.
            type: str, the type of the component.
            geometric_options: dict, the configuration of geometric parameters (optional).

        Output:
            None
        """
        ops = self.options
        for i in range(len(pos_list)):
            pos = copy.deepcopy(pos_list[i])
            name = pre_name + "_{}".format(i)
            options = Dict()
            options.name = name
            options.type = type
            options[key] = copy.deepcopy(pos)
            if geometric_options is not None:
                for k, v in geometric_options.items():
                    options[k] = copy.deepcopy(v)
            ops[name] = copy.deepcopy(options)
        self.inject_options(ops)
        return

    def batch_change(self, name_list, op_name, op_value):
        """
        Batch modify component options.

        Input:
            name_list: list, a list of component names to be modified.
            op_name: str, the name of the option to be modified.
            op_value: any type, the new value.

        Output:
            None
        """
        ops = self.options
        for i in range(len(name_list)):
            name = name_list[i]
            options = copy.deepcopy(ops[name])
            options[op_name] = copy.deepcopy(op_value)
            ops[name] = copy.deepcopy(options)
        self.inject_options(ops)
        return

    def batch_add(self, options_list):
        """
        Fast add components.

        Input:
            options_list: dict, containing parameters for the new component.

        Output:
            None

        Exception:
            ValueError: Throws an exception when the component name or type is not specified.
        """
        # 批量操作，避免多次拷贝和注入
        new_ops = self.options.copy()
        for options in options_list:
            name = options.name
            type = options.type
            if name is None or type is None:
                raise ValueError(f"无效的选项：{options}")

            new_ops[name] = options
        
        self.inject_options(new_ops)