import copy, os, importlib, math
from addict import Dict
import gdspy

def get_module_Dict(dirpath, pre_path, exclusions: list = None):
    """
    Get all modules in a specific directory

    Inputs:
        path: The directory where the modules to be automatically imported are located
        pre_path: The prefix path for importing the modules

    Outputs:
        module_Dict: A dictionary of the exported modules
    """
        
    # 接口
    copy.deepcopy(exclusions)

    # 输入检测，__init__.py永远不在考虑范围内。
    if exclusions == None:
        exclusions = ["__init__.py"]
    else:
        exclusions.append("__init__.py")

    module_Dict = Dict()
    # 遍历目录下所有文件
    for filename in os.listdir(dirpath):
        if (filename.endswith(".py") or filename.endswith(".pyd")) and filename not in exclusions:
            # 构造模块名
            if filename.endswith(".py"):
                module_name = filename[:-3]  # 去掉文件扩展名 ".py"
            if filename.endswith(".pyd"):
                module_name = filename[:-4]  # 去掉文件扩展名 ".pyd"
            module = importlib.import_module(pre_path+module_name)
            module_Dict[module_name] = module

    return module_Dict

def get_pack_Dict(dirpath, pre_path, exclusions: list = None):
    """
        Get all packages in a specific directory

        Input:
            path: The directory containing the packages to be automatically imported
            pre_path: The prefix path of the package where the class is located

        Output:
            pack_Dict: Dictionary of exported packages
    """

    
    # 接口
    copy.deepcopy(exclusions)

    pack_Dict = Dict()
    # 遍历目录下所有文件
    for pack_name in os.listdir(dirpath):
        pack_path = os.path.join(dirpath, pack_name)
        if is_package(pack_path):
            pack = importlib.import_module(pre_path+pack_name)
            pack_Dict[pack_name] = pack

    return pack_Dict

def convert_to_camel_case(input_str):
    words = input_str.split('_')
    camel_case_str = words[0].capitalize() + ''.join(word.capitalize() for word in words[1:])
    return camel_case_str

def convert_to_snake_case(input_str):
    # 将字符串首字母小写
    input_str = input_str[0].lower() + input_str[1:]
    
    # 在大写字母前插入下划线，并转换为小写
    snake_case_str = ''.join(['_' + char.lower() if char.isupper() else char for char in input_str])
    
    return snake_case_str.lstrip('_')

def is_package(directory):
    init_file_path = os.path.join(directory, '__init__.py')
    init_file_path2 = os.path.join(directory, '__init__.pyd')
    return os.path.exists(init_file_path) or os.path.exists(init_file_path2)

def show_options(addict_obj, indent=0):
    if isinstance(addict_obj, dict):
        addict_obj = Dict(addict_obj)
    if isinstance(addict_obj, Dict):
        for key, value in addict_obj.items():
            if isinstance(value, Dict):
                print(f"{' ' * indent}{key}:")
                show_options(value, indent + 4)
            elif isinstance(value, list):
                print(f"{' ' * indent}{key}:", end = " ")
                if key == "edges":
                    print("")
                    print_nested_list(value, indent + 4)
                elif key == "positions":
                    print("")
                    num = 0
                    for pos in value:
                        if num == 0:
                            print("", end = " " * (indent + 4))
                        print(pos, end = " ")
                        num += 1
                        if num == 10:
                            print("")
                            num = 0
                    print("")
                else:
                    print("")
                    print(" " * (indent + 4) + str(value))
            else:
                print(f"{' ' * indent}{key}: {value}")
    else:
        print(addict_obj)

def print_nested_list(lst, indent=0):
    for item in lst:
        print(" " * indent + "-" + str(item))

def sort_and_join(strings, join_tool: str = "__"):
    sorted_strings = sorted(strings)
    result = join_tool.join(sorted_strings)
    return result

def is_number(var):
    return isinstance(var, (int, float, complex))

def get_filename_extension_from_path(path):
    # 使用os.path.splitext()拆分文件名和扩展名
    file_name, file_extension = os.path.splitext(os.path.basename(path))
    return file_name, file_extension

def get_filename(path):
    file_name, file_extension = os.path.splitext(os.path.basename(path))
    return file_name

def get_extension(path):
    file_name, file_extension = os.path.splitext(os.path.basename(path))
    return file_extension

# svg
def save_svg(cell, width: float = 500, path: str = "./svg/temp/svg"):
    """将一个cell以某个宽度保存为svg

    输入：
        cell: gdspy的cell
        width: 要保存的svg的宽度
    
    输入：
        无
    """
    jg_and_create_path(path)
    cell_width = get_width(cell)
    if cell_width == 0:
        raise ValueError("{}的宽度是0，无法生成svg！".format(cell.name))
        return False
    # print("width = {}, cell_width = {}".format(width, cell_width))
    cell.write_svg(path, scaling = width/cell_width)
    print("svg文件保存在：{}".format(path))
    return True

def get_width(cell):
    # Get the bounding box of the Cell
    box = cell.get_bounding_box()
    if box is None:
        return 0
    min_point, max_point = box

    # Extract the minimum and maximum x coordinates
    min_x, _ = min_point
    max_x, _ = max_point

    width = max_x - min_x

    return width

# 目录
def jg_and_create_path(path):
    """判断该路径中的目录是否都存在，如果不存在则创建

    输入：
        path: 是否存在某个目录

    输出：
        无
    """
    dirname = os.path.dirname(path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    return

def create_xlsx(file_path):
    import os
    from openpyxl import Workbook
    # 确保目录存在
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    # 创建工作簿和工作表
    workbook = Workbook()
    sheet = workbook.active
    
    # 保存文件
    workbook.save(file_path)
    print(f'Excel file created at: {file_path}')
def get_file_info(file_path):
    directory, file_name = os.path.split(file_path)
    file_name_no_ext, file_extension = os.path.splitext(file_name)
    return {
        'directory': directory,
        'file_name': file_name_no_ext,
        'file_extension': file_extension
    }
def jg_and_create_path_plus(path):
    if not os.path.exists(path):
        # 如果路径不存在，创建目录或文件
        if path.endswith('/'):  # 如果是目录
            os.makedirs(path)
            print(f"目录 '{path}' 已创建。")
        else:  # 如果是文件
            directory = os.path.dirname(path)
            if not os.path.exists(directory):
                os.makedirs(directory)
                
            file_info = get_file_info(path)
            if file_info['file_extension'] == ".xlsx":
                create_xlsx(path)
            else:
                with open(path, 'w') as file:
                    file.write('')  # 创建一个空文件
                print(f"文件 '{path}' 已创建。")

def change_layer_of_entire_cell(cell, layer, datatype=None):
    # Get dependency cells recursively
    all_cells = cell.get_dependencies(True)
    # Include original cell in the set
    all_cells.add(cell)
    for c in all_cells:
        # Process all polygons
        for polygon in c.polygons:
            # Substitute layer list for a new one with the
            # the same length and the desired layer number
            polygon.layers = [layer] * len(polygon.layers)
            # Proecessing datatype
            if datatype != None:
                polygon.datatypes = [datatype] * len(polygon.layers)
        # Process all paths
        for path in c.paths:
            path.layers = [layer] * len(path.layers)
        # Process all labels
        for label in c.labels:
            label.layer = layer

def custom_hash(s):
    """
    字符串哈希为数字
    """
    result = 0
    prime = 31  # 选择一个质数作为乘法因子，可以减小冲突概率

    for char in s:
        result = (result * prime + ord(char)) % (255)  # 防止溢出，取模
    return result

def jg_dir(topo_pos0, topo_pos1):
    """
    根据两个拓扑坐标判断topo_pos0在topo_pos1的方位
    """
    
    edge_sub = [topo_pos0[0] - topo_pos1[0], topo_pos0[1] - topo_pos1[1]]
    if edge_sub == [-1, 0]:    # q0在q1的左边
        return "left"
    elif edge_sub == [1, 0]:    # q0在q1的右边
        return "right"
    elif edge_sub == [0, 1]:    # q0在q1的上边
        return "top"
    elif edge_sub == [0, -1]:    # q0在q1的下边
        return "bot"
    else:
        raise ValueError("两个拓扑坐标不相邻！")
    
def delete_file_if_exists(path):
    """
    判断文件是否存在，如果存在则删除
    :param file_path: 文件路径
    """
    if os.path.exists(path):
        os.remove(path)
    else:
        pass

def find_rightmost_coordinate(coordinates):
    rightmost_coordinate = max(coordinates, key=lambda c: c[0])
    return rightmost_coordinate
def find_leftmost_coordinate(coordinates):
    rightmost_coordinate = min(coordinates, key=lambda c: c[0])
    return rightmost_coordinate
def find_topmost_coordinate(coordinates):
    rightmost_coordinate = max(coordinates, key=lambda c: c[1])
    return rightmost_coordinate
def find_botmost_coordinate(coordinates):
    rightmost_coordinate = min(coordinates, key=lambda c: c[1])
    return rightmost_coordinate

def export_options(data, path):
    """
    Export supported data types to a specified path in a txt file.

    Supported data types:

    Basic data types:
    - String (str)
    - Number (int, float)
    - Boolean (True/False)
    - None (None)

    Container data types:
    - List (list)
    - Dictionary (dict)
    - Tuple (tuple)

    Parameters:
    - data: Data to be exported.
    - path: Path to export the data.
    """

    def format_data(data):
        """ 
        Format data for exporting to txt file.
        """
        if isinstance(data, Dict):
            data = dict(data)
            
        if isinstance(data, str):
            return "\"" + data + "\""
        elif isinstance(data, (int, float, bool, type(None))):
            return str(data)
        elif isinstance(data, list):
            return '[' + ', '.join(format_data(item) for item in data) + ']'
        elif isinstance(data, tuple):
            ans = "("
            # print(data)
            for item in data:
                # print(format(item))
                temp = str(item) + ", "
                ans += temp
            ans = ans[:-2]
            ans += ")"
            return ans
            # return '(' + ', '.join(format_data(item) for item in data) + ')'
        elif isinstance(data, dict):
            return '{' + ', '.join(f'{format_data(k)}: {format_data(v)}' for k, v in data.items()) + '}'
        
    # Define the supported data types
    supported_types = (Dict, str, int, float, bool, type(None), list, dict, tuple)

    # Check if the data type is supported
    if type(data) not in supported_types:
        raise ValueError(f"Unsupported data type: {type(data)}")

    # Export the data to the specified path
    with open(path, 'w') as f:
        # Write data to the file
        f.write(format_data(data))

    print(f"Data exported successfully to {path}")
    
def import_options(path):
    import ast
    try:
        with open(path, 'r') as file:
            data = file.read()
            options = ast.literal_eval(data)
            return Dict(options)
    except FileNotFoundError:
        print("File not found.")
        return None
    except SyntaxError:
        print("Syntax error in file. Please check the file format.")
        return None
    
def get_file_name_from_path(path):
    # 使用os.path.splitext()拆分文件名和扩展名
    file_name, file_extension = os.path.splitext(os.path.basename(path))
    return file_name, file_extension

def display_dataframe(path):
    import pathlib
    import re
    import pandas as pd
    from IPython.display import display
    p=pathlib.Path(path)
    m=p.read_text().split('\n')

    cm=m[m.index('Capacitance Matrix'):m.index('Conductance Matrix')-1]

    pattern='(?<=C Units:)(.+?)((?<![^a-zA-Z0-9_\u4e00-\u9fa5])(?=[^a-zA-Z0-9_\u4e00-\u9fa5])|(?<=[^a-zA-Z0-9_\u4e00-\u9fa5])(?![^a-zA-Z0-9_\u4e00-\u9fa5])|$)'

    unit=re.findall(pattern, p.read_text())[0][0]

    rowLabels = []
    column_labels = []
    data=[]
    j=[]
    for i in range(len(cm)):
            a=[x for x in cm[i].split('\t') if x!='']
            if(len(a)==0):
                break
            if i==1:
                j=a.copy()
                    
            if i==1:
                column_labels=a
            elif i>1:
                rowLabels.append(a[0])
                data.append([f"{str(round(float(x),5))}" for x in a[1:]])
    df1 = pd.DataFrame(data, index=column_labels, columns=rowLabels) 
    display(df1)
    return df1

def calculate_direction_angle(coord1, coord2):
    x1, y1 = coord1
    x2, y2 = coord2

    # 计算坐标差值
    dx = x2 - x1
    dy = y2 - y1

    # 使用math.atan2计算方向角
    angle_rad = math.atan2(dy, dx)
    return angle_rad

def write_txt(data, path, mode: str = "w"):
    jg_and_create_path(path)
    with open(path, mode) as f:
        f.write(data)

def calc_itscts(path1, path2):
    path1 = copy.deepcopy(path1)
    path2 = copy.deepcopy(path2)

    segs1 = []
    segs2 = []

    for i in range(0, len(path1) - 1):
        segs1.append([path1[i], path1[i + 1]])
    for i in range(0, len(path2) - 1):
        segs2.append([path2[i], path2[i + 1]])

    itscts = []
    for i in range(0, len(segs1)):
        for j in range(0, len(segs2)):
            seg1 = segs1[i]
            seg2 = segs2[j]
            itsct = find_itsct(seg1, seg2)
            if itsct is None:
                pass
            else:
                itscts.append(itsct)
    return copy.deepcopy(itscts)

def find_itsct(segment1, segment2):
    x1 = segment1[0][0]
    y1 = segment1[0][1]
    x2 = segment1[1][0]
    y2 = segment1[1][1]
    x3 = segment2[0][0]
    y3 = segment2[0][1]
    x4 = segment2[1][0]
    y4 = segment2[1][1]

    def cross_product(v1, v2):
        return v1[0] * v2[1] - v1[1] * v2[0]

    def subtract(v1, v2):
        return (v1[0] - v2[0], v1[1] - v2[1])

    def line_params(p1, p2):
        a = p2[1] - p1[1]
        b = p1[0] - p2[0]
        c = a * p1[0] + b * p1[1]
        return a, b, c

    det = cross_product((x1 - x2, y1 - y2), (x3 - x4, y3 - y4))

    if det == 0:
        # Lines are parallel, no intersection
        return None

    # Calculate intersection point
    intersection_x = cross_product((x1 * y2 - y1 * x2, x1 - x2), (x3 * y4 - y3 * x4, x3 - x4)) / det
    intersection_y = cross_product((x1 * y2 - y1 * x2, y1 - y2), (x3 * y4 - y3 * x4, y3 - y4)) / det

    # Check if the intersection point is within the bounds of both line segments
    if (
        min(x1, x2) <= intersection_x <= max(x1, x2) and
        min(y1, y2) <= intersection_y <= max(y1, y2) and
        min(x3, x4) <= intersection_x <= max(x3, x4) and
        min(y3, y4) <= intersection_y <= max(y3, y4)
    ):
        return [intersection_x, intersection_y]
    else:
        # Intersection point is outside the bounds of at least one line segment
        return None
    
def rotate_point(point, center, angle):
    # 将角度转换为弧度
    angle_rad = math.radians(angle)

    # 计算旋转后的点的坐标
    x = center[0] + (point[0] - center[0]) * math.cos(angle_rad) - (point[1] - center[1]) * math.sin(angle_rad)
    y = center[1] + (point[0] - center[0]) * math.sin(angle_rad) + (point[1] - center[1]) * math.cos(angle_rad)

    # 返回旋转后的点的坐标
    return (x, y)

def clear_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'w') as file:
            file.truncate(0)

def convert_tuple_to_list(input_dict: Dict = Dict()):
    output_dict = Dict()
    
    for key, value in input_dict.items():
        if isinstance(value, dict):
            output_dict[key] = convert_tuple_to_list(value)
        elif isinstance(value, tuple):
            output_dict[key] = list(value)
        elif isinstance(value, list):
            new_value = list()
            for op in value:
                if isinstance(op, tuple):
                    new_value.append(list(op))
                else:
                    new_value.append(op)
            output_dict[key] = copy.deepcopy(new_value)
        else:
            output_dict[key] = value
    
    return output_dict

def check_tuple(input_dict: Dict = Dict()):
    output_dict = Dict()
    
    for key, value in input_dict.items():
        if isinstance(value, dict):
            output_dict[key] = convert_tuple_to_list(value)
        elif isinstance(value, tuple):
            raise ValueError("{}的类型是元组：{}，应改为列表。".format(key, value))
        elif isinstance(value, list):
            new_value = list()
            for op in value:
                if isinstance(op, tuple):
                    raise ValueError("{}中的元素类型为元组：{}，应该为列表。".format(key, value))
                else:
                    new_value.append(op)
            output_dict[key] = copy.deepcopy(new_value)
        else:
            output_dict[key] = value
    
    return output_dict

def import_list_from_txt(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            # 使用eval函数将字符串转换为列表
            my_list = eval(content)
            return my_list
    except FileNotFoundError:
        print("File not found.")
        return []
    
def generate_python_class_from_gds(filepath: str, location: str):
    import gdstk
    # Load the GDS file
    filename = os.path.basename(filepath)
    gds_lib = gdstk.read_gds(filepath)
    cells = gds_lib.cells

    # Generate class name from file name
    base_name = os.path.splitext(filename)[0]
    class_name = ''.join(word.capitalize() for word in base_name.split('_'))

    # Create class content
    class_definition = f"""
import gdspy, copy
from addict import Dict
import math as mt
from base.library_base import LibraryBase

class {class_name}(LibraryBase):
    default_options = Dict(
        name="{class_name}0",
        type="{class_name}",
        chip="chip0",
        gds_pos=(0, 0),
        topo_pos=(0, 0),
        outline=[],
        rotation=0
    )

    def __init__(self, options: Dict = None):
        super().__init__(options)
        return

    def _add_polygons_to_cell(self):
        polygoascqcqewqwdqwdqwdqwdn_data = [
"""

    # Add polygons for each cell
    for cell in cells:
        for polygon in cell.polygons:
            points = polygon.points.tolist()
            layer = polygon.layer
            class_definition += f"""
            ({points}, {layer}),
"""

    class_definition += """
        ]

        for points in polygon_data:
            layer = points[-1]
            polygon_points = points[0]
            self.cell.add(gdspy.Polygon(polygon_points, layer=layer))

    def _calculate_bounding_box(self):
        min_x, min_y = float("inf"), float("inf")
        max_x, max_y = float("-inf"), float("-inf")

        for polygon in self.cell.polygons:
            bbox = polygon.get_bounding_box()
            if bbox is not None:
                min_x = min(min_x, bbox[0][0])
                min_y = min(min_y, bbox[0][1])
                max_x = max(max_x, bbox[1][0])
                max_y = max(max_y, bbox[1][1])

        if min_x == float("inf") or min_y == float("inf"):
            raise ValueError("No valid polygons found in the cell.")

        return min_x, min_y, max_x, max_y

    def _transform_polygons(self, dx, dy, rotation, center):
        for polygon in self.cell.polygons:
            polygon.translate(dx, dy)
            polygon.rotate(rotation, center=center)

    def calc_general_ops(self):
        self.lib = gdspy.GdsLibrary()
        gdspy.library.use_current_library = False
        self.cell = self.lib.new_cell(self.name + "_cell")

        self._add_polygons_to_cell()

        # Bounding box calculations
        min_x, min_y, max_x, max_y = self._calculate_bounding_box()
        current_center_x = (min_x + max_x) / 2
        current_center_y = (min_y + max_y) / 2

        # Target center
        target_center_x, target_center_y = self.options.gds_pos
        dx = target_center_x - current_center_x
        dy = target_center_y - current_center_y

        # Update gds_pos to match adjusted center
        self.options.gds_pos = (target_center_x, target_center_y)

        # Apply transformations
        self._transform_polygons(dx, dy, self.rotation, center=(target_center_x, target_center_y))
        self.outline = [
            points for polygon in self.cell.polygons for points in polygon.get_bounding_box().tolist()
        ]
        return

    def draw_gds(self):
        self.calc_general_ops()
"""

    # Define the output directory
    output_dir = os.path.join("./", location)
    os.makedirs(output_dir, exist_ok=True)

    # Write the class to a file
    output_filename = os.path.join(output_dir, f"{base_name}.py")
    with open(output_filename, "w") as py_file:
        py_file.write(class_definition)

    print(f"Python class written to {output_filename}")

def generate_gds_pos2(topo_positions, dist):
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

def get_cell_bounding_box(cell):
    if not cell.polygons and not cell.references:
        return None  # 如果 Cell 为空，返回 None

    # 初始化最小和最大坐标
    min_x, min_y = float('inf'), float('inf')
    max_x, max_y = -float('inf'), -float('inf')

    # 遍历所有多边形
    for polygon in cell.polygons:
        bbox = polygon.get_bounding_box()
        if bbox.any():
            min_x = min(min_x, bbox[0][0])
            min_y = min(min_y, bbox[0][1])
            max_x = max(max_x, bbox[1][0])
            max_y = max(max_y, bbox[1][1])

    # 遍历所有引用（CellReference 和 CellArray）
    for ref in cell.references:
        bbox = ref.get_bounding_box()
        if bbox.any():
            min_x = min(min_x, bbox[0][0])
            min_y = min(min_y, bbox[0][1])
            max_x = max(max_x, bbox[1][0])
            max_y = max(max_y, bbox[1][1])

    # 如果没有有效的包围盒，返回 None
    if min_x == float('inf'):
        return None

    return (min_x, min_y), (max_x, max_y)

def custom_calculation(options1, options2):
    
    return

def read_layout_gds(file_path):
    """Reads a GDS layout file and automatically parses the layout components into Python classes.
    
    Input:
        file_path (str): Path to the GDS file to be read.
        
    Output:
        output_path (str): A file directory containing the parsed component results.
    """
    
    return