import gdspy
import math, copy
import numpy as np
from addict import Dict
from base.library_base import LibraryBase

# We still need to add a coverage bridge for straight line segments now，Then improve the algorithm for adding coverage bridges
# Let's do it next week. This week is too tiring

def draw_isosceles_trapezoid(vertices):
    """
    Draw an isosceles trapezoid based on vertex coordinates。

    :param vertices: The coordinates of the four vertices of a trapezoid，The format is [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
    """
    # create GDSII library
    # Create a trapezoid
    trapezoid = gdspy.Polygon(vertices, layer=1)
    return trapezoid

class CoverBridge(LibraryBase):
    default_options = Dict(
        # framework
        name="bridgecover1",
        type="bridgecover",
        chip = "chip3",
        outline = [],   
        # geometrical parameter  ZFG890 6
        length = 5,
        corner_radius = np.pi / 4,
        width = 2,
        bg_width = 0,
        bg_inner_r = 0,
        direction = 1,
        line1_out = (0 , 0),
        line1_in = (0 , 1),
        line2_out = (0 , 2),
        line2_in = (0 , 3),
    )


    def __init__(self, options: Dict = None):
        super().__init__(options)
        if options is None:
            options = self.default_options  # If no options are provided，Then use default options
        
        self.lib = gdspy.GdsLibrary()
        gdspy.library.use_current_library = False
        self.cell = self.lib.new_cell(self.name + "_cell")
        return
    
    def calc_general_ops(self):
        return

    def calculate_angle(self , point1, point2):
        """
        Calculate line segments (point1, point2) give x Angle in the positive direction of the axis。
        :param point1: Starting point of line segment (x1, y1)
        :param point2: The endpoint of a line segment (x2, y2)
        :return: give x Angle in the positive direction of the axis（unit：linear measure）
        """
        # Calculate the direction vector of the line segment
        direction_vector = np.array(point2) - np.array(point1)

        # use atan2 Calculation and x Axis angle（The result is radians）
        angle_radians = np.arctan2(direction_vector[1], direction_vector[0])

        # Convert radians to degrees
        angle_degrees = np.degrees(angle_radians)

        # Ensure that the angle is within [0, 360) in range
        if angle_degrees < 0:
            angle_degrees += 360

        angle_degrees = angle_degrees * (np.pi / 180)

        return angle_degrees

    def get_extern_point(self , point1 , point2):
        """
        follow point2 direction point1 的方direction延伸指定长度，Return the coordinates of the new point。

        :param point1: First point (x1, y1)
        :param point2: The second point (x2, y2)
        :param length: Extended length
        :return: Coordinates of the new point (x_new, y_new)
        """
        # Calculate direction vector
        direction = np.array(point1) - np.array(point2)
        
        # Calculate the size of the length
        direction_length = np.linalg.norm(direction)
        
        # If the length of the direction is 0，Return point2The coordinates（Avoid dividing by zero）
        if direction_length == 0:
            return point1
        
        # Normalized direction vector
        unit_direction = direction / direction_length
        
        # Calculate the coordinates of the new point
        new_point = np.array(point1) + unit_direction * (self.width / 2 ) 
        
        return tuple(new_point)


    def add_bg(self , path):
        self.cell.add(path)

    def create_clockwise_perpendicular_line(self,point1, point2 , flag):  #point2 It's foot drop
        """
        follow point2 set out，Create a line segment with (point1, point2) Clockwise vertical line segment，
        And the length is equal to the length of the line segment。

        :param point1: Starting point of line segment (x1, y1)
        :param point2: The endpoint of a line segment (x2, y2)
        :return: The endpoint coordinates of the vertical line segment (end_point)
        """
        # Calculate the direction vector of the line segment
        direction = np.array(point2) - np.array(point1)
        
        # Calculate the length of a line segment
        length = np.linalg.norm(direction)
        
        # Calculate the vector in the clockwise perpendicular direction（clockwise rotation90linear measure）
        perp_direction = np.array([direction[1], -direction[0]])
        
        # Normalized vertical direction vector
        perp_direction /= np.linalg.norm(perp_direction)

        # Calculate the endpoints of the perpendicular line（follow point2 set out）
        if flag == 1:
            end_point = point2 - perp_direction * length
        elif flag == 0 :
            end_point = point2 + perp_direction * length
        return tuple(end_point)

    def draw_triangle(self , point1, point2, point3):
        """
        Draw a triangle using the given three points。

        :param point1: The first vertex of a triangle (x1, y1)
        :param point2: The second vertex of a triangle (x2, y2)
        :param point3: The third vertex of a triangle (x3, y3)
        """
        # Create a list of vertices for a triangle
        triangle_points = [point1, point2, point3]

        # Create a triangle polygon
        triangle = gdspy.Polygon(triangle_points, layer=2, datatype=0)

        # Add polygons to cells
        self.cell.add(triangle)

        # save GDS file

    def draw_gds(self ):
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

        #Calculate the coordinates of the extension point
        line1_extern_p = self.get_extern_point(self.line1_out ,self.line1_in)
        print(line1_extern_p)

        line1_inner_p = self.get_extern_point(self.line1_in ,self.line1_out)

        middle_p = ((self.line1_in[0] + self.line1_out[0]) / 2 , (self.line1_in[1] + self.line1_out[1]) / 2)

        print(self.line1_in)
        print(self.line1_out)
        
        #Sir, become a key line segment ， Prepare for drawing arcs
        path = gdspy.Path(self.width , (line1_extern_p))
        path1 = gdspy.Path(self.width , (line1_inner_p))

        path2 = gdspy.Path(self.bg_width , middle_p)

        angle = self.calculate_angle(self.line1_out , self.line1_in)
       
        print('angle :' + str(angle))
        
        #Determine the direction of extension application
        if(self.direction == 1):
           angle += np.pi / 2 

        elif self.direction == 0 :
           angle -= np.pi / 2  

        if self.corner_radius == 0 :  #straight line
            path.segment( self.length , direction = angle , layer=2)
            #path.segment(self.length , "+y")
            path1.segment(self.length , direction = angle, layer=2)
            path2.segment(self.length , direction = angle, layer=2)   

        elif self.corner_radius != 0:   #arc
            path.segment(0 , direction = angle)
            #path.segment(0 , "+y")
            path1.segment(0 , direction = angle)
            path2.segment(0 , direction = angle)       
        
            '''
            path2 = gdspy.Path(1, (self.line1_out))
            path2.segment(2,"+y")
            self.cell.add(path2)'''
            #camber line
            if self.direction == 1:
                path2.turn((self.bg_inner_r) , self.corner_radius , layer = 2)

                #outer arc
                path.turn(self.width/2  + (self.bg_inner_r) + self.bg_width / 2, self.corner_radius , layer = 2)
                #inner arc
                path1.turn(- self.width/2  + (self.bg_inner_r) - self.bg_width / 2, self.corner_radius ,layer = 2 )

            elif self.direction == 0 :
                path2.turn((self.bg_inner_r) , -self.corner_radius , layer = 2)

                #outer arc
                path.turn(self.width/2  + (self.bg_inner_r) + self.bg_width / 2, -self.corner_radius , layer = 2)
                #inner arc
                path1.turn(- self.width/2  + (self.bg_inner_r) - self.bg_width / 2, -self.corner_radius ,layer = 2 )

        self.cell.add(path)
        self.cell.add(path1)
        self.cell.add(path2)

        #Triangle part

        if self.direction == 1:
            #line1 Inner triangle
            triangle_p = self.create_clockwise_perpendicular_line(line1_inner_p , self.line1_in , 1)
            # line1 Outer triangle
            triangle_p1 = self.create_clockwise_perpendicular_line(line1_extern_p , self.line1_out , 0)
            #line2 Outer triangle
            line2_extern_p = self.get_extern_point(self.line2_out ,self.line2_in)
            triangle_p2 = self.create_clockwise_perpendicular_line(line2_extern_p , self.line2_out , 1)
            #line2 Inner triangle
            line2_inner_p = self.get_extern_point(self.line2_in ,self.line2_out)
            triangle_p3 = self.create_clockwise_perpendicular_line(line2_inner_p , self.line2_in , 0)

        elif self.direction == 0:
            #line1 Inner triangle
            triangle_p = self.create_clockwise_perpendicular_line(line1_inner_p , self.line1_in , 0)
            # line1 Outer triangle
            triangle_p1 = self.create_clockwise_perpendicular_line(line1_extern_p , self.line1_out , 1)
            #line2 Outer triangle
            line2_extern_p = self.get_extern_point(self.line2_out ,self.line2_in)
            triangle_p2 = self.create_clockwise_perpendicular_line(line2_extern_p , self.line2_out , 0)
            #line2 Inner triangle
            line2_inner_p = self.get_extern_point(self.line2_in ,self.line2_out)
            triangle_p3 = self.create_clockwise_perpendicular_line(line2_inner_p , self.line2_in , 1)


        self.draw_triangle(line1_inner_p , self.line1_in , triangle_p)
        self.draw_triangle(line1_extern_p , self.line1_out , triangle_p1)
        self.draw_triangle(line2_extern_p , self.line2_out , triangle_p2)
        self.draw_triangle(line2_inner_p , self.line2_in , triangle_p3)


    
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
 

