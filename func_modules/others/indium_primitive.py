#######################################################################
# Process GDS files, extract polygons, and arrange indium bumps, ensuring they meet minimum distance constraints
#######################################################################

def process_gds_with_indium_optimized(gds_file, coord1, coord2, min_distance_points, min_distance_polygons):
    """
    Process the GDS file and arrange indium bumps, using pyclipper to optimize distance calculations.

    Input:
        gds_file: str, the path to the GDS file.
        coord1: tuple, the starting coordinates (x1, y1) of the area.
        coord2: tuple, the ending coordinates (x2, y2) of the area.
        min_distance_points: float, the minimum distance between indium bumps.
        min_distance_polygons: float, the minimum distance between indium bumps and polygons.

    Output:
        options: Dict, a collection of operational parameters for the arranged indium bumps.
    """
    import numpy as np
    import gdspy
    from shapely.geometry import Polygon, box
    import pyclipper
    from scipy.spatial import KDTree
    import matplotlib.pyplot as plt
    from addict import Dict
    
    def extract_elements_optimized(gds_file, coord1, coord2):
        """
        Extract polygons from the GDS file that are within the specified rectangular area, clipping parts outside the area.

        Input:
            gds_file: str, the path to the GDS file.
            coord1: tuple, the starting coordinates (x1, y1) of the rectangular area.
            coord2: tuple, the ending coordinates (x2, y2) of the rectangular area.

        Output:
            elements: list, a list of extracted polygons.
        """
        lib = gdspy.GdsLibrary(infile=gds_file)
        x_min, y_min = min(coord1[0], coord2[0]), min(coord1[1], coord2[1])
        x_max, y_max = max(coord1[0], coord2[0]), max(coord1[1], coord2[1])
        region = box(x_min, y_min, x_max, y_max)

        elements = []

        for cell in lib.cells.values():
            for polygon in cell.get_polygons(by_spec=False):
                poly = Polygon(polygon)
                if poly.is_empty:
                    continue

                if poly.intersects(region):
                    clipped = poly.intersection(region)

                    if clipped.is_empty:
                        continue
                    elif clipped.geom_type == 'Polygon':
                        elements.append(np.array(clipped.exterior.coords))
                        for interior in clipped.interiors:
                            elements.append(np.array(interior.coords))
                    elif clipped.geom_type == 'MultiPolygon':
                        for part in clipped.geoms:
                            elements.append(np.array(part.exterior.coords))
                            for interior in part.interiors:
                                elements.append(np.array(interior.coords))

        return elements

    def preprocess_polygons(elements, margin):
        """
        Preprocess the expanded area of polygons using pyclipper.

        Input:
            elements: list, a list of polygon points.
            margin: float, the distance to expand.

        Output:
            expanded_polygons: list, a list of expanded polygons.
        """
        expanded_polygons = []
        pco = pyclipper.PyclipperOffset()

        for element in elements:
            pco.Clear()
            pco.AddPath(element.tolist(), pyclipper.JT_ROUND, pyclipper.ET_CLOSEDPOLYGON)
            expanded = pco.Execute(margin)
            expanded_polygons.extend(expanded)

        return expanded_polygons

    def point_inside_polygons(point, expanded_polygons):
        """
        Check if a point is inside the expanded polygons.

        Input:
            point: tuple, the coordinates of the point to check.
            expanded_polygons: list, a list of expanded polygons.

        Output:
            bool, whether the point is inside the expanded polygons.
        """
        for poly in expanded_polygons:
            if pyclipper.PointInPolygon(point, poly) != 0:
                return True
        return False

    def optimized_distance_check(point, tree, expanded_polygons, min_distance_points):
        """
        Check if a point meets distance and position constraints.

        Input:
            point: tuple, the coordinates of the point to check.
            tree: KDTree, a tree of positions where indium bumps have been arranged.
            expanded_polygons: list, a list of expanded polygons.
            min_distance_points: float, the minimum distance between indium bumps.

        Output:
            bool, whether the point meets the constraints.
        """
        if tree and tree.query(point, k=1)[0] < min_distance_points:
            return False
        if point_inside_polygons(point, expanded_polygons):
            return False
        return True

    def add_indium(elements, coord1, coord2, step=100, min_distance_points=200, min_distance_polygons=20):
        """
        Arrange indium bumps within a specified area.

        Input:
            elements: list, a list of extracted polygons.
            coord1: tuple, the starting coordinates of the area.
            coord2: tuple, the ending coordinates of the area.
            step: float, the spacing of the point grid, default is 100.
            min_distance_points: float, the minimum distance between indium bumps.
            min_distance_polygons: float, the minimum distance between indium bumps and polygons.

        Output:
            indium_points: list, a list of positions where indium bumps are arranged.
        """
        x_min, y_min = min(coord1[0], coord2[0]), min(coord1[1], coord2[1])
        x_max, y_max = max(coord1[0], coord2[0]), max(coord1[1], coord2[1])

        grid_x = np.arange(x_min, x_max, step)
        grid_y = np.arange(y_min, y_max, step)

        indium_points = []
        tree = None

        expanded_polygons = preprocess_polygons(elements, min_distance_polygons)

        for x in grid_x:
            for y in grid_y:
                point = (x, y)
                if optimized_distance_check(point, tree, expanded_polygons, min_distance_points):
                    indium_points.append(point)
                    tree = KDTree(indium_points)

        return indium_points

    def plot_elements_and_indium(coord1, coord2, elements, indium_points):
        """
        Visualize the arrangement of polygons and indium bumps.

        Input:
            coord1: tuple, the starting coordinates of the area.
            coord2: tuple, the ending coordinates of the area.
            elements: list, a list of extracted polygons.
            indium_points: list, a list of positions where indium bumps are arranged.
        """
        fig, ax = plt.subplots(figsize=(10, 8))

        rect_x = [coord1[0], coord2[0], coord2[0], coord1[0], coord1[0]]
        rect_y = [coord1[1], coord1[1], coord2[1], coord2[1], coord1[1]]
        ax.plot(rect_x, rect_y, 'r--', label="Bounding Box")

        for polygon in elements:
            polygon = np.array(polygon)
            ax.plot(polygon[:, 0], polygon[:, 1], 'b-')

        if indium_points:
            indium_x, indium_y = zip(*indium_points)
            ax.scatter(indium_x, indium_y, color='g', s=10)

        ax.set_xlabel("X Coordinate")
        ax.set_ylabel("Y Coordinate")
        ax.set_aspect('equal', 'box')
        plt.title("GDS Elements and Indium Pillars")
        plt.show()

    elements = extract_elements_optimized(gds_file, coord1, coord2)
    indium_pillars = add_indium(elements, coord1, coord2, step=100, 
                            min_distance_points=min_distance_points, 
                            min_distance_polygons=min_distance_polygons)
    plot_elements_and_indium(coord1, coord2, elements, indium_pillars)

    def return_indium_options(indium_positions):
        """
        Convert the positions of indium bumps to operational parameters.

        Input:
            indium_positions: list, a list of center positions of indium bumps.

        Output:
            options: Dict, a collection of operational parameters for indium bumps.
        """
        options = Dict()
        for pos in indium_positions:
            option = Dict(
                name="In_{}_{}".format(pos[0], pos[1]),
                type="IndiumBump",
                chip="chip0",
                outline=[],
                center_pos=pos,
                radius=10
            )
            options[option.name] = option
        return options
    
    options = return_indium_options(indium_pillars)

    return options