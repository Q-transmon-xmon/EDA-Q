############################################################################################
# File Name: airbridge_nb.py
# Description: This file primarily contains the construction code for the AirbridgeNb (air bridge without base).
############################################################################################
import gdspy, copy
from addict import Dict
import math as mt
from base.library_base import LibraryBase

class AirbridgeNb(LibraryBase):
    """
    AirbridgeNb class for creating air bridge structures without a base.

    Attributes:
        default_options: Dict, containing default parameters for air bridges without a base.
    """
    default_options = Dict(
        name="AirbridgeNb0",
        type="AirbridgeNb",
        chip="chip0",
        gds_pos=(0, 0),
        topo_pos=(0, 0),
        outline=[],
        rotation=0
    )

    def __init__(self, options: Dict=None):
        """
        Initializes the AirbridgeNb class.

        Input:
            options: Dict, user-defined parameters for air bridges without a base.

        Output:
            None.
        """
        super().__init__(options)
        return

    def _add_polygons_to_cell(self):
        """
        Adds polygons to the cell.

        Output:
            None.
        """
        polygon_data = [
            ([[-18.0, -57.0], [18.0, -57.0], [18.0, -30.0], [10.0, -22.0], [10.0, 22.0], [18.0, 30.0], [18.0, 57.0], [-18.0, 57.0], [-18.0, 30.0], [-10.0, 22.0], [-10.0, -22.0], [-18.0, -30.0]], 3),
            ([[-22.0, 24.5], [-15.5, 18.0], [15.5, 18.0], [22.0, 24.5], [22.0, 61.0], [-22.0, 61.0]], 2),
            ([[-22.0, -61.0], [22.0, -61.0], [22.0, -24.5], [15.5, -18.0], [-15.5, -18.0], [-22.0, -24.5]], 2),
            ([[-26.0, 14.0], [26.0, 14.0], [26.0, 65.0], [-26.0, 65.0]], 4),
            ([[-26.0, -65.0], [26.0, -65.0], [26.0, -14.0], [-26.0, -14.0]], 4),
        ]

        for points in polygon_data:
            layer = points[-1]
            polygon_points = points[0]
            self.cell.add(gdspy.Polygon(polygon_points, layer=layer))

    def _calculate_bounding_box(self):
        """
        Calculates the bounding box.

        Output:
            Coordinates of the bounding box (min_x, min_y, max_x, max_y).
        """
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
        """
        Transforms polygons.

        Input:
            dx: Displacement in the x-coordinate.
            dy: Displacement in the y-coordinate.
            rotation: Rotation angle.
            center: Rotation center point.

        Output:
            None.
        """
        for polygon in self.cell.polygons:
            polygon.translate(dx, dy)
            polygon.rotate(rotation, center=center)

    def calc_general_ops(self):
        """
        Calculates general operations.

        Output:
            None.
        """
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
        """
        Draws the GDS.

        Output:
            None.
        """
        self.calc_general_ops()