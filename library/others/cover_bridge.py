import gdspy
import math, copy
import numpy as np
from addict import Dict
from base.library_base import LibraryBase

# 现在还需要添加直线段的覆盖桥，然后完善覆盖桥的添加算法
# 下周再做吧这周太累了

def draw_isosceles_trapezoid(vertices):
    """
    根据顶点坐标绘制等腰梯形。

    :param vertices: 梯形的四个顶点坐标，格式为 [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
    """
    # 创建 GDSII 库
    # 创建梯形
    trapezoid = gdspy.Polygon(vertices, layer=1)
    return trapezoid

class CoverBridge(LibraryBase):
    default_options = Dict(
        # 框架
        name="bridgecover1",
        type="bridgecover",
        chip = "chip3",
        outline = [],   
        # 几何参数  ZFG890 6
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
            options = self.default_options  # 如果没有提供选项，则使用默认选项
        
        self.lib = gdspy.GdsLibrary()
        gdspy.library.use_current_library = False
        self.cell = self.lib.new_cell(self.name + "_cell")
        return
    
    def calc_general_ops(self):
        return

    def calculate_angle(self , point1, point2):
        """
        计算线段 (point1, point2) 与 x 轴正方向的夹角。
        :param point1: 线段的起点 (x1, y1)
        :param point2: 线段的终点 (x2, y2)
        :return: 与 x 轴正方向的夹角（单位：度）
        """
        # 计算线段的方向向量
        direction_vector = np.array(point2) - np.array(point1)

        # 使用 atan2 计算与 x 轴的夹角（结果为弧度）
        angle_radians = np.arctan2(direction_vector[1], direction_vector[0])

        # 将弧度转换为度
        angle_degrees = np.degrees(angle_radians)

        # 确保夹角在 [0, 360) 范围内
        if angle_degrees < 0:
            angle_degrees += 360

        angle_degrees = angle_degrees * (np.pi / 180)

        return angle_degrees

    def get_extern_point(self , point1 , point2):
        """
        从 point2 向 point1 的方向延伸指定长度，返回新点的坐标。

        :param point1: 第一个点 (x1, y1)
        :param point2: 第二个点 (x2, y2)
        :param length: 延伸的长度
        :return: 新点的坐标 (x_new, y_new)
        """
        # 计算方向向量
        direction = np.array(point1) - np.array(point2)
        
        # 计算长度的大小
        direction_length = np.linalg.norm(direction)
        
        # 如果方向长度为 0，返回点2的坐标（避免除以零）
        if direction_length == 0:
            return point1
        
        # 归一化方向向量
        unit_direction = direction / direction_length
        
        # 计算新点的坐标
        new_point = np.array(point1) + unit_direction * (self.width / 2 ) 
        
        return tuple(new_point)


    def add_bg(self , path):
        self.cell.add(path)

    def create_clockwise_perpendicular_line(self,point1, point2 , flag):  #point2 是垂足
        """
        从 point2 出发，创建一条与线段 (point1, point2) 顺时针垂直的线段，
        并且长度等于线段的长度。

        :param point1: 线段的起点 (x1, y1)
        :param point2: 线段的终点 (x2, y2)
        :return: 垂线段的端点坐标 (end_point)
        """
        # 计算线段的方向向量
        direction = np.array(point2) - np.array(point1)
        
        # 计算线段的长度
        length = np.linalg.norm(direction)
        
        # 计算顺时针垂线方向向量（顺时针旋转90度）
        perp_direction = np.array([direction[1], -direction[0]])
        
        # 归一化垂线方向向量
        perp_direction /= np.linalg.norm(perp_direction)

        # 计算垂线的端点（从 point2 出发）
        if flag == 1:
            end_point = point2 - perp_direction * length
        elif flag == 0 :
            end_point = point2 + perp_direction * length
        return tuple(end_point)

    def draw_triangle(self , point1, point2, point3):
        """
        使用给定的三个点绘制一个三角形。

        :param point1: 三角形的第一个顶点 (x1, y1)
        :param point2: 三角形的第二个顶点 (x2, y2)
        :param point3: 三角形的第三个顶点 (x3, y3)
        """
        # 创建三角形的顶点列表
        triangle_points = [point1, point2, point3]

        # 创建三角形多边形
        triangle = gdspy.Polygon(triangle_points, layer=2, datatype=0)

        # 将多边形添加到单元中
        self.cell.add(triangle)

        # 保存 GDS 文件

    def draw_gds(self ):
        # 计算直线和弧线的点

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

        #计算延伸点的坐标
        line1_extern_p = self.get_extern_point(self.line1_out ,self.line1_in)
        print(line1_extern_p)

        line1_inner_p = self.get_extern_point(self.line1_in ,self.line1_out)

        middle_p = ((self.line1_in[0] + self.line1_out[0]) / 2 , (self.line1_in[1] + self.line1_out[1]) / 2)

        print(self.line1_in)
        print(self.line1_out)
        
        #先生成关键线段 ， 为画弧线做准备
        path = gdspy.Path(self.width , (line1_extern_p))
        path1 = gdspy.Path(self.width , (line1_inner_p))

        path2 = gdspy.Path(self.bg_width , middle_p)

        angle = self.calculate_angle(self.line1_out , self.line1_in)
       
        print('angle :' + str(angle))
        
        #判断延申方向
        if(self.direction == 1):
           angle += np.pi / 2 

        elif self.direction == 0 :
           angle -= np.pi / 2  

        if self.corner_radius == 0 :  #直线
            path.segment( self.length , direction = angle , layer=2)
            #path.segment(self.length , "+y")
            path1.segment(self.length , direction = angle, layer=2)
            path2.segment(self.length , direction = angle, layer=2)   

        elif self.corner_radius != 0:   #弧线
            path.segment(0 , direction = angle)
            #path.segment(0 , "+y")
            path1.segment(0 , direction = angle)
            path2.segment(0 , direction = angle)       
        
            '''
            path2 = gdspy.Path(1, (self.line1_out))
            path2.segment(2,"+y")
            self.cell.add(path2)'''
            #中弧线
            if self.direction == 1:
                path2.turn((self.bg_inner_r) , self.corner_radius , layer = 2)

                #外弧
                path.turn(self.width/2  + (self.bg_inner_r) + self.bg_width / 2, self.corner_radius , layer = 2)
                #内弧
                path1.turn(- self.width/2  + (self.bg_inner_r) - self.bg_width / 2, self.corner_radius ,layer = 2 )

            elif self.direction == 0 :
                path2.turn((self.bg_inner_r) , -self.corner_radius , layer = 2)

                #外弧
                path.turn(self.width/2  + (self.bg_inner_r) + self.bg_width / 2, -self.corner_radius , layer = 2)
                #内弧
                path1.turn(- self.width/2  + (self.bg_inner_r) - self.bg_width / 2, -self.corner_radius ,layer = 2 )

        self.cell.add(path)
        self.cell.add(path1)
        self.cell.add(path2)

        #三角形部分

        if self.direction == 1:
            #line1 内侧三角
            triangle_p = self.create_clockwise_perpendicular_line(line1_inner_p , self.line1_in , 1)
            # line1 外侧三角
            triangle_p1 = self.create_clockwise_perpendicular_line(line1_extern_p , self.line1_out , 0)
            #line2 外侧三角
            line2_extern_p = self.get_extern_point(self.line2_out ,self.line2_in)
            triangle_p2 = self.create_clockwise_perpendicular_line(line2_extern_p , self.line2_out , 1)
            #line2 内侧三角
            line2_inner_p = self.get_extern_point(self.line2_in ,self.line2_out)
            triangle_p3 = self.create_clockwise_perpendicular_line(line2_inner_p , self.line2_in , 0)

        elif self.direction == 0:
            #line1 内侧三角
            triangle_p = self.create_clockwise_perpendicular_line(line1_inner_p , self.line1_in , 0)
            # line1 外侧三角
            triangle_p1 = self.create_clockwise_perpendicular_line(line1_extern_p , self.line1_out , 1)
            #line2 外侧三角
            line2_extern_p = self.get_extern_point(self.line2_out ,self.line2_in)
            triangle_p2 = self.create_clockwise_perpendicular_line(line2_extern_p , self.line2_out , 0)
            #line2 内侧三角
            line2_inner_p = self.get_extern_point(self.line2_in ,self.line2_out)
            triangle_p3 = self.create_clockwise_perpendicular_line(line2_inner_p , self.line2_in , 1)


        self.draw_triangle(line1_inner_p , self.line1_in , triangle_p)
        self.draw_triangle(line1_extern_p , self.line1_out , triangle_p1)
        self.draw_triangle(line2_extern_p , self.line2_out , triangle_p2)
        self.draw_triangle(line2_inner_p , self.line2_in , triangle_p3)


    
        '''   def draw_gds(self):
        """
        绘制紫色区域的布局。
        """
        # 绘制中心矩形
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

        trapezoid_p2 = (pos[0][0] - length/2 - height/2 , pos[0][1])  #左下
        trapezoid_p3 = (pos[0][0] + length/2 + height/2 , pos[0][1])   #右下
        trapezoid_p1 = (pos[0][0] - length/2  , pos[0][1] + height/2)  #左上
        trapezoid_p4 = (pos[0][0] + length/2  , pos[0][1] + height/2)  #右上

        vertices.append(trapezoid_p1)
        vertices.append(trapezoid_p2)
        vertices.append(trapezoid_p3)
        vertices.append(trapezoid_p4)
        trapezoid = draw_isosceles_trapezoid(vertices)
        self.cell.add(trapezoid)
        '''
 

