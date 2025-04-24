from gds_analysis import read_chip_code

def read_chip(file_path):
    read_chip_code.read_layout_gds(file_path=file_path)

def read_single_component(filepath: str, location: str):
    import gdstk
    import os
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
        polygon_data = [
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

def add_component_temporarily(path, components_type):
    import importlib
    import toolbox

    read_single_component(path, "")
    
    components_module = importlib.import_module("library.{}".format(components_type))    # Obtain component category modules
    new_component_module_name = toolbox.get_filename(path)    # Obtain the module name of the newly added component
    components_module.module_name_list.append(new_component_module_name)    # Add a new module name to the component category module

    # Add new component classes as attributes to the component category module
    new_component_class_name = toolbox.convert_to_camel_case(new_component_module_name)    # The class name of the new component
    new_component_module = importlib.import_module(new_component_module_name)    # Modules of new components
    new_component_class = getattr(new_component_module, new_component_class_name)    # Class of new components
    setattr(components_module, new_component_class_name, new_component_class)    # Add new component classes as attributes to the component category module

    # Print prompt information
    print("The new component was added in {} successfully. "
        "If you want to use the newly added component, the component type is {}."
        .format(components_type, new_component_class_name))