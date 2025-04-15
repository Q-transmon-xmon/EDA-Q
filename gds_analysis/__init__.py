import sys
sys.path.append("..")
import re
import shutil
import cv2
import os
import importlib
#from toolbox import generate_python_class_from_gds
import math
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
        self.polygon_data = []
        return

    def _add_polygons_to_cell(self):
        self.polygon_data = [
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

        for points in self.polygon_data:
            layer = points[-1]
            polygon_points = points[0]
            self.cell.add(gdspy.Polygon(polygon_points, layer=layer))
            
    def print_polygons(self):
    
        print(self.polygon_data)


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
    output_dir = os.path.join("../library", location)
    os.makedirs(output_dir, exist_ok=True)

    # Write the class to a file
    output_filename = os.path.join(output_dir, f"{base_name}.py")
    with open(output_filename, "w") as py_file:
        py_file.write(class_definition)

    print(f"Python class written to {output_filename}")
def read_layout_gds(file_path):
    """Reads a Gos layout file and automatically parses the layout components into Python classes.
    
    Input:
        file path(str):Path to the Gs file to be read

    0utput:
        output path (str):A file directory containing the parsed component results

    """
        #Enter the path to the gds layout
    file_path = os.path.abspath(file_path)
    filename = os.path.basename(file_path)
    filename_without_extension = os.path.splitext(filename)[0]
    parent_parent_dir = os.path.dirname(file_path)#Get the directories of the previous two levels
    librarypath = os.path.join(parent_parent_dir, f"{filename_without_extension}_library")#Build class directory

    os.makedirs(librarypath, exist_ok=True)
    generate_python_class_from_gds(file_path, librarypath)#Generates the corresponding class of the layout

    gds_library_path = os.path.join(librarypath,f"{filename_without_extension}.py")
    svgpath = os.path.join(parent_parent_dir, f"{filename_without_extension}_svg")#Generate SVG image directory
    os.makedirs(svgpath, exist_ok=True)
    pngpath = os.path.join(parent_parent_dir, f"{filename_without_extension}_png")#Generate a PNG image directory
    os.makedirs(pngpath, exist_ok=True)
    #Read information about a class in a file
    module_name = os.path.basename(gds_library_path)[:-3]
    sys.path.append(os.path.dirname(gds_library_path))
    with open(gds_library_path, 'r') as file:
        content = file.read()

    class_pattern = re.compile(r'class (\w+)\(', re.MULTILINE)
    classes = class_pattern.findall(content)
    module = importlib.import_module(module_name)
    for class_name in classes:
        cls = getattr(module, class_name)
        base = cls()
        base._add_polygons_to_cell()
        #full_path = os.path.join(svgpath, module_name + ".svg")
        #Generate a class for each component
        parts_index = 0#Number of components
        for item in base.polygon_data:
            part_name = f'part_{parts_index}'
            globals()[part_name] = item[0]
            if(is_rectangle(item[0])):
                continue
            generate_python_class_from_layout(item[0],librarypath, part_name)
            parts_index += 1

    files = [f for f in os.listdir(librarypath) if f.startswith("part_") and f.endswith(".py")]
    for file in files:
        module_part = file[:-3]

        module_name = f"{filename_without_extension}_library.{module_part}"
        class_name = module_part
    # Dynamic import module
        module = importlib.import_module(module_name)
    # Adds the imported class to the global variable
        globals()[class_name] = getattr(module, class_name)
        full_path = os.path.join(svgpath, module_part + ".svg")
        createpart = globals()[class_name]()
        createpart._add_polygons_to_cell()
        polygon_data = createpart.polygon_data
        createpart.show_svg(path = full_path)
        svg_file = full_path
        png_file = full_path = os.path.join(pngpath, module_part + ".png")
        convert_svg_to_png(svg_file, png_file)

    def extract_number(filename):
        try:
            parts = filename.split('part_')
            number_part = parts[1].split('.')[0]
            return int(number_part)
        except (IndexError, ValueError):
            return None

    source_dir = pngpath
    destination_dir = os.path.join(parent_parent_dir, f"{filename_without_extension}_Similarparts_png")#Generates a PNG image directory of the target component library
    os.makedirs(destination_dir, exist_ok=True)
    destination_pydir = os.path.join(parent_parent_dir, f"{filename_without_extension}_Similarparts_py")#Generates the class directory corresponding to the target component library
    os.makedirs(destination_pydir, exist_ok=True)
    target_file_path = None
    filename1_without_extension = None
    # Obtain all PNG files in the source directory
    proto_files = [f for f in os.listdir(source_dir) if f.endswith('.png')]
    files = [f for f in proto_files if extract_number(f) is not None]
    # Sort files using functions that securely extract numbers
    files.sort(key=extract_number)

    # Compare files and move
    for i in range(len(files) - 1):
        file1 = files[i]
        for j in range(i+1, len(files)):
            file2 = files[j]
            file1path = os.path.join(source_dir, file1)
            file2path = os.path.join(source_dir, file2)

            if selectparts(file1path, file2path):
            # Using the ORB method in computer vision, a BF matcher is constructed to match the Corner points
            # If the similarity is high, check whether similar files already exist in the destination folder
                exists = False
                filename1 = os.path.basename(file1path)
                filename1_without_extension = os.path.splitext(filename1)[0]
                target_file_path = os.path.join(librarypath, f"{filename1_without_extension}" + ".py")

                for existing_file in os.listdir(destination_dir):
                    existing_file_path = os.path.join(destination_dir, existing_file)
                    try:
                        path1 = target_file_path
                        with open(path1, 'r') as f:
                            content = f.read()
                        data1 = extract_polygon_data(content)
                        if data1 == 0:
                            print(f"No data extracted from {path1}")
                    except Exception as e:
                        print(f"Error processing {path1}: {e}")

                    try:
                        filename2 = os.path.basename(existing_file_path)
                        filename2_without_extension = os.path.splitext(filename2)[0]
                        path2 = os.path.join(librarypath, f"{filename2_without_extension}" + ".py")

                        with open(path2, 'r') as f:
                            content = f.read()
                        data2 = extract_polygon_data(content)
                        if data2 == 0:
                            print(f"No data extracted from {path2}")
                    except Exception as e:
                        print(f"Error processing {path2}: {e}")

                    # Set the tolerance
                    tolerance = 10.0

                    # Determine whether two polygons are similar,Use the polygon similarity matching method
                    similar = are_polygons_similar_based_on_distances(data1, data2, tolerance)
                    if similar:
                        print(f"{file1path} is similar to {existing_file_path}")
                        exists = True
                        break
                        
            # If there are no similar files in the destination folder, move file1
                if not exists:
                    shutil.copy(file1path, os.path.join(destination_dir, file1))
                    shutil.copy(target_file_path,os.path.join(destination_pydir, f"{filename1_without_extension}" + ".py"))
                    break
                if exists:
                    break
    #Returns the image library path and class library path corresponding to the selected component library
    print("To be continued...")
    return(destination_dir,destination_pydir)



def convert_svg_to_png(input_file, output_file):
    import cairosvg
    from cairocffi import CairoError
#Convert svg files to png files
    try:
        cairosvg.svg2png(url=input_file, write_to=output_file)
    except CairoError as e:
        print(f"Error converting {input_file} to {output_file}: {e}")

def generate_python_class_from_layout(arr, location: str, name: str):
#arr: polygonal array of layout; location: generated directory; name: The name of the generated class
    import gdstk
    '''''''''''
    # Load the GDS file
    filename = os.path.basename(filepath)
    gds_lib = gdstk.read_gds(filepath)
    cells = gds_lib.cells
    '''''''''''
    # Generate class name from file name
    base_name = name
    #class_name = ''.join(word.capitalize() for word in base_name.split('_'))
    class_name = base_name

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
        self.polygon_data = []
        return

    def _add_polygons_to_cell(self):
        # Initialize polygon_data with the arr array passed in
        self.polygon_data = [({arr},0),]

        for points in self.polygon_data:
            layer = points[-1]
            polygon_points = points[0]
            self.cell.add(gdspy.Polygon(polygon_points, layer=layer))
            
    def print_polygons(self):
    
        print(self.polygon_data)


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
    output_dir = os.path.join("../library", location)
    os.makedirs(output_dir, exist_ok=True)

    # Write the class to a file
    output_filename = os.path.join(output_dir, f"{base_name}.py")
    with open(output_filename, "w") as py_file:
        py_file.write(class_definition)

    print(f"Python class written to {output_filename}")
def selectparts_RANSAC(location1: str, location2: str):
    import numpy as np
    try:
        # Using the ORB method,RANSAC in computer vision, a FLNN matcher is constructed to match the Feature points
        # Read image
        img1 = cv2.imread(location1)
        img2 = cv2.imread(location2)
        img2 = cv2.rotate(img2, cv2.ROTATE_90_COUNTERCLOCKWISE)

        # Initialize the ORB detector
        orb = cv2.ORB_create()

        # Use the ORB to find key points and descriptors
        kp1, des1 = orb.detectAndCompute(img1, None)
        kp2, des2 = orb.detectAndCompute(img2, None)

        # Create a FLANN Matcher object
        index_params = dict(algorithm=6, table_number=6, key_size=32, multi_probe_level=2)
        search_params = dict(checks=50)
        flann = cv2.FlannBasedMatcher(index_params, search_params)

        matches = flann.knnMatch(des1, des2, k=2)
        # Screen for good matches
        good_matches = []
        for match in matches:
            if len(match) == 2:  # Make sure match is a tuple of two elements
                m, n = match
                if m.distance < 1 * n.distance:
                    good_matches.append(m)
        if len(good_matches) >= 4:
            # Gets the coordinates of the matching points
            src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

            # Find the Homography matrix using RANSAC
            M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

            # Calculate the number of inside points
            inliers_count = np.sum(mask)

            if inliers_count > 4:
                print(location1,location2,'1bestmatch!')
                return 1

            else:
                return 0
        else:
            return 0
            
    except Exception as e:
        print(f"An error occurred during matching: {e}")
        print(f"Location 1: {location1}")
        print(f"Location 2: {location2}")
        return 0

'''''
    # Draw matching results
        draw_params = dict(matchColor=(0, 255, 0), singlePointColor=None, matchesMask=matchesMask, flags=2)
        img3 = cv2.drawMatches(img1, kp1, img2, kp2, good_matches, None, **draw_params)
'''''
def selectparts(location1: str, location2: str):
    try:
        # Using the ORB method in computer vision, a BF matcher is constructed to match the Corner points
        # Read image
        img1 = cv2.imread(location1)
        img2 = cv2.imread(location2)
        img2 = cv2.rotate(img2, cv2.ROTATE_90_COUNTERCLOCKWISE)

        gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        corners1 = cv2.goodFeaturesToTrack(gray1, maxCorners=100, qualityLevel=0.01, minDistance=10)
        corners2 = cv2.goodFeaturesToTrack(gray2, maxCorners=100, qualityLevel=0.01, minDistance=10)

        # Initialize the ORB detector
        orb = cv2.ORB_create()

        # Use the ORB to find key points and descriptors
        kp1 = [cv2.KeyPoint(x=float(x), y=float(y), size=20) for x, y in corners1[:, 0, :]]
        kp2 = [cv2.KeyPoint(x=float(x), y=float(y), size=20) for x, y in corners2[:, 0, :]]

        des1 = orb.compute(gray1, kp1)[1]
        des2 = orb.compute(gray2, kp2)[1]
        # Create a BFMatcher object
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        # Matching descriptor
        matches = bf.match(des1, des2)
        # Sort by distance
        matches = sorted(matches, key=lambda x: x.distance)
        matches_count = len(matches)

        if matches_count >= 4:
            print(location1,location2,'1bestmatch!')
            return 1
        else:
            return 0

    except Exception as e:
        print(f"An error occurred during matching: {e}")
        print(f"Location 1: {location1}")
        print(f"Location 2: {location2}")
        return 0

'''''
    # Draw matching results
        draw_params = dict(matchColor=(0, 255, 0), singlePointColor=None, matchesMask=matchesMask, flags=2)
        img3 = cv2.drawMatches(img1, kp1, img2, kp2, good_matches, None, **draw_params)
'''''

def is_rectangle(points):
    #Determine whether it is rectangular (connecting lines)
    if len(points) != 4:
        return False

    # Calculate the distance between two points
    def distance(p1, p2):
        return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5

    # Stores the distance between all point pairs
    distances = []
    for i in range(4):
        for j in range(i + 1, 4):
            distances.append((distance(points[i], points[j]), i, j))

    # Sort by distance
    distances.sort()
    return (distances[0][0] == distances[1][0] and
            distances[2][0] == distances[3][0] and
            distances[4][0] == distances[5][0])

def are_polygons_similar_based_on_distances(polygon1, polygon2, tolerance):
    #Use the polygon similarity matching method
    def calculate_centroid(polygon):
    #Calculate the center of mass of the polygon
        x_coords = [p[0] for p in polygon]
        y_coords = [p[1] for p in polygon]
        centroid_x = sum(x_coords) / len(x_coords)
        centroid_y = sum(y_coords) / len(y_coords)
        return (centroid_x, centroid_y)
    def sort_polygon_vertices(polygon, centroid):
    #Sort the vertices according to their Angle relative to the center of mass
        return sorted(polygon, key=lambda point: math.atan2(point[1] - centroid[1], point[0] - centroid[0]))
    def calculate_distance_to_centroid(polygon, centroid):
    #Calculate the distance from each vertex to the center of mass
        return [math.dist(point, centroid) for point in polygon]
    
    #Determine whether two polygons are similar based on the distance from the vertex to the center of mass
    centroid1 = calculate_centroid(polygon1)
    centroid2 = calculate_centroid(polygon2)
    
    sorted_polygon1 = sort_polygon_vertices(polygon1, centroid1)
    sorted_polygon2 = sort_polygon_vertices(polygon2, centroid2)

    distances1 = calculate_distance_to_centroid(sorted_polygon1, centroid1)
    distances2 = calculate_distance_to_centroid(sorted_polygon2, centroid2)
    distances1.sort()
    distances2.sort()


    if len(distances1) != len(distances2):
        return False  #The number of vertices is different, and the direct judgment is not similar
    
    for d1, d2 in zip(distances1, distances2):
        if abs(d1 - d2) > tolerance:
            return False  # If the distance difference between any pair of vertices exceeds the tolerance, it is not similar
    return True  

def extract_polygon_data(file_content):
    # The regular expression matches the list of coordinates
    pattern = re.compile(r'self\.polygon_data = \[\(\[([\s\S]*?)\],0\),\]', re.DOTALL)
    match = pattern.search(file_content)
    if match:
        # Extract the coordinate list string
        coordinates_str = match.group(1)
        # Converts a string to a list of coordinate pairs
        coordinates_list = eval(f'[{coordinates_str}]')
        return coordinates_list
    else:
        return None
    
