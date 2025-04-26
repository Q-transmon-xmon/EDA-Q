import gdspy
import math, copy
import numpy as np
from addict import Dict
from base.library_base import LibraryBase

# We still need to add a coverage bridge for straight line segments now, then improve the algorithm for adding coverage bridges
# Let's do it next week. This week is too tiring

def draw_isosceles_trapezoid(vertices):
    """
    Draw an isosceles trapezoid based on vertex coordinates.

    :param vertices: The coordinates of the four vertices of a trapezoid, in the format [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
    """
    # Create a trapezoid
    trapezoid = gdspy.Polygon(vertices, layer=1)
    return trapezoid

class CoverBridge(LibraryBase):
    default_options = Dict(
        # framework
        name="bridgecover1",
        type="bridgecover",
        chip="chip3",
        outline=[],   
        # geometrical parameter  ZFG890 6
        length=5,
        corner_radius=np.pi / 4,
        width=2,
        bg_width=0,
        bg_inner_r=0,
        direction=1,
        line1_out=(0, 0),
        line1_in=(0, 1),
        line2_out=(0, 2),
        line2_in=(0, 3),
    )

    def __init__(self, options: Dict=None):
        super().__init__(options)
        if options is None:
            options = self.default_options  # If no options are provided, then use default options
        
        self.lib = gdspy.GdsLibrary()
        gdspy.library.use_current_library = False
        self.cell = self.lib.new_cell(self.name + "_cell")
        return
    
    def calc_general_ops(self):
        return

    def calculate_angle(self, point1, point2):
        """
        Calculate the angle of the line segment (point1, point2) with respect to the positive direction of the x-axis.

        :param point1: Starting point of the line segment (x1, y1)
        :param point2: Endpoint of the line segment (x2, y2)
        :return: Angle with respect to the positive direction of the x-axis (unit: radians)
        """
        # Calculate the direction vector of the line segment
        direction_vector = np.array(point2) - np.array(point1)

        # Calculate the angle with the x-axis using atan2 (result is in radians)
        angle_radians = np.arctan2(direction_vector[1], direction_vector[0])

        # Convert radians to degrees
        angle_degrees = np.degrees(angle_radians)

        # Ensure the angle is within the range [0, 360)
        if angle_degrees < 0:
            angle_degrees += 360

        angle_degrees = angle_degrees * (np.pi / 180)

        return angle_degrees

    def get_extern_point(self, point1, point2):
        """
        Extend the line segment from point2 in the direction of point1 by a specified length and return the coordinates of the new point.

        :param point1: First point (x1, y1)
        :param point2: Second point (x2, y2)
        :param length: Extension length
        :return: Coordinates of the new point (x_new, y_new)
        """
        # Calculate the direction vector
        direction = np.array(point1) - np.array(point2)
        
        # Calculate the length of the direction vector
        direction_length = np.linalg.norm(direction)
        
        # If the length of the direction vector is 0, return the coordinates of point2 (to avoid division by zero)
        if direction_length == 0:
            return point1
        
        # Normalize the direction vector
        unit_direction = direction / direction_length
        
        # Calculate the coordinates of the new point
        new_point = np.array(point1) + unit_direction * (self.width / 2)
        
        return tuple(new_point)

    def add_bg(self, path):
        self.cell.add(path)

    def create_clockwise_perpendicular_line(self, point1, point2, flag):
        """
        Create a line segment perpendicular to (point1, point2) in the clockwise direction, with the same length as the original line segment.

        :param point1: Starting point of the line segment (x1, y1)
        :param point2: Endpoint of the line segment (x2, y2)
        :param flag: Direction flag (1 for clockwise, 0 for counterclockwise)
        :return: Endpoint coordinates of the perpendicular line segment (end_point)
        """
        # Calculate the direction vector of the line segment
        direction = np.array(point2) - np.array(point1)
        
        # Calculate the length of the line segment
        length = np.linalg.norm(direction)
        
        # Calculate the vector in the clockwise perpendicular direction (90 degrees clockwise rotation)
        perp_direction = np.array([direction[1], -direction[0]])
        
        # Normalize the perpendicular direction vector
        perp_direction /= np.linalg.norm(perp_direction)

        # Calculate the endpoint of the perpendicular line (starting from point2)
        if flag == 1:
            end_point = point2 - perp_direction * length
        elif flag == 0:
            end_point = point2 + perp_direction * length
        return tuple(end_point)

    def draw_triangle(self, point1, point2, point3):
        """
        Draw a triangle using the given three points.

        :param point1: First vertex of the triangle (x1, y1)
        :param point2: Second vertex of the triangle (x2, y2)
        :param point3: Third vertex of the triangle (x3, y3)
        """
        # Create a list of vertices for the triangle
        triangle_points = [point1, point2, point3]

        # Create a triangle polygon
        triangle = gdspy.Polygon(triangle_points, layer=2, datatype=0)

        # Add the polygon to the cell
        self.cell.add(triangle)

    def draw_gds(self):
        # Calculate the points of straight lines and arcs

        self.line1_in = self.options.line1_in
        self.line1_out = self.options.line1_out
        self.line2_out = self.options.line2_out
        self.line2_in = self.options.line2_in
        self.bg_width = self.options.bg_width
        self.bg_inner_r = self.options.bg_inner_r
        self.corner_radius = self.options.corner_radius
        self.length = self.options.length
        self.angle = self.options.angle
        self.direction = self.options.direction

        # Calculate the coordinates of the extension point
        line1_extern_p = self.get_extern_point(self.line1_out, self.line1_in)
        print(line1_extern_p)

        line1_inner_p = self.get_extern_point(self.line1_in, self.line1_out)

        middle_p = ((self.line1_in[0] + self.line1_out[0]) / 2, (self.line1_in[1] + self.line1_out[1]) / 2)

        print(self.line1_in)
        print(self.line1_out)
        
        # Create a key line segment, prepare for drawing arcs
        path = gdspy.Path(self.width, line1_extern_p)
        path1 = gdspy.Path(self.width, line1_inner_p)

        path2 = gdspy.Path(self.bg_width, middle_p)

        angle = self.calculate_angle(self.line1_out, self.line1_in)
       
        print('angle :' + str(angle))
        
        # Determine the direction of extension application
        if self.direction == 1:
            angle += np.pi / 2 

        elif self.direction == 0:
            angle -= np.pi / 2  

        if self.corner_radius == 0:  # straight line
            path.segment(self.length, direction=angle, layer=2)
            path1.segment(self.length, direction=angle, layer=2)
            path2.segment(self.length, direction=angle, layer=2)   

        elif self.corner_radius != 0:   # arc
            path.segment(0, direction=angle)
            path1.segment(0, direction=angle)
            path2.segment(0, direction=angle)       

            # Camber line
            if self.direction == 1:
                path2.turn(self.bg_inner_r, self.corner_radius, layer=2)

                # Outer arc
                path.turn(self.width/2 + self.bg_inner_r + self.bg_width/2, self.corner_radius, layer=2)
                # Inner arc
                path1.turn(-self.width/2 + self.bg_inner_r - self.bg_width/2, self.corner_radius, layer=2)

            elif self.direction == 0:
                path2.turn(self.bg_inner_r, -self.corner_radius, layer=2)

                # Outer arc
                path.turn(self.width/2 + self.bg_inner_r + self.bg_width/2, -self.corner_radius, layer=2)
                # Inner arc
                path1.turn(-self.width/2 + self.bg_inner_r - self.bg_width/2, -self.corner_radius, layer=2)

        self.cell.add(path)
        self.cell.add(path1)
        self.cell.add(path2)

        # Triangle part

        if self.direction == 1:
            # Line1 inner triangle
            triangle_p = self.create_clockwise_perpendicular_line(line1_inner_p, self.line1_in, 1)
            # Line1 outer triangle
            triangle_p1 = self.create_clockwise_perpendicular_line(line1_extern_p, self.line1_out, 0)
            # Line2 outer triangle
            line2_extern_p = self.get_extern_point(self.line2_out, self.line2_in)
            triangle_p2 = self.create_clockwise_perpendicular_line(line2_extern_p, self.line2_out, 1)
            # Line2 inner triangle
            line2_inner_p = self.get_extern_point(self.line2_in, self.line2_out)
            triangle_p3 = self.create_clockwise_perpendicular_line(line2_inner_p, self.line2_in, 0)

        elif self.direction == 0:
            # Line1 inner triangle
            triangle_p = self.create_clockwise_perpendicular_line(line1_inner_p, self.line1_in, 0)
            # Line1 outer triangle
            triangle_p1 = self.create_clockwise_perpendicular_line(line1_extern_p, self.line1_out, 1)
            # Line2 outer triangle
            line2_extern_p = self.get_extern_point(self.line2_out, self.line2_in)
            triangle_p2 = self.create_clockwise_perpendicular_line(line2_extern_p, self.line2_out, 0)
            # Line2 inner triangle
            line2_inner_p = self.get_extern_point(self.line2_in, self.line2_out)
            triangle_p3 = self.create_clockwise_perpendicular_line(line2_inner_p, self.line2_in, 1)

        self.draw_triangle(line1_inner_p, self.line1_in, triangle_p)
        self.draw_triangle(line1_extern_p, self.line1_out, triangle_p1)
        self.draw_triangle(line2_extern_p, self.line2_out, triangle_p2)
        self.draw_triangle(line2_inner_p, self.line2_in, triangle_p3)
    
        '''   def draw_gds(self):
        """
        Draw the layout of the purple area。
        """
        # Draw a central rectangle
        name = self.name
        type = self.type
        chip = self.chip
        outline = copy.deepcopy(self.outline)
        pos = copy.deepcopy(self.pos)
        gap = self.gap
        length = self.length
        height = self.height
        corner_radius = self.corner_radius

        self.lib = gdspy.GdsLibrary()
        gdspy.library.use_current_library = False
        self.cell = self.lib.new_cell(self.name + "_cell")


        rectangle = gdspy.Rectangle((pos[0][0] - length/2 , pos[0][1] + height/2),(pos[0][0] + length/2 , pos[0][1] + height) , layer=1)
        self.cell.add(rectangle)

        vertices = []

        trapezoid_p2 = (pos[0][0] - length/2 - height/2 , pos[0][1])  #lower left
        trapezoid_p3 = (pos[0][0] + length/2 + height/2 , pos[0][1])   #lower right
        trapezoid_p1 = (pos[0][0] - length/2  , pos[0][1] + height/2)  #Top Left
        trapezoid_p4 = (pos[0][0] + length/2  , pos[0][1] + height/2)  #upper right

        vertices.append(trapezoid_p1)
        vertices.append(trapezoid_p2)
        vertices.append(trapezoid_p3)
        vertices.append(trapezoid_p4)
        trapezoid = draw_isosceles_trapezoid(vertices)
        self.cell.add(trapezoid)
        '''
 

