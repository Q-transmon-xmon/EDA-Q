def add_air_bridges_czy(pos, bend_radius, spacing=120, chip_type="chip3", width=10, air_bridge_type="AirbriageNb"):
    """
    Add air bridges to ensure they are within the valid range of the path, considering both the curved and straight segments of the path.

    Input:
        pos: list, a list of coordinates of path points defining the key points of the path.
        bend_radius: float, the radius of the rounded corners of the path (used to determine the curvature of the path).
        spacing: float, the spacing between air bridges (default is 120).
        chip_type: str, the type of chip to which the air bridges belong (default is "chip3").
        width: float, the width of the path, used to determine the geometric shape of the path (default is 10).
        air_bridge_type: str, the type of air bridge (default is "AirBridgeNb").

    Output:
        options: Dict, a dictionary containing the parameters of the air bridges, with each air bridge's name as the key.

    Functions:
        1. Add air bridges to the middle and corner sections of the path, ensuring they are within the path range.
        2. Use `gdspy.FlexPath` and polygon checking tools to implement precise geometric calculations.
        3. Check if the air bridge positions are within the path range using `is_point_in_flexpath`.
        4. Calculate the center position and rotation angle of the air bridges.
    """
    from addict import Dict
    import math
    import numpy as np
    import gdspy

    def find_nearest_segment_center(polygons, curr_point, line_width):
        """
        寻找距离 curr_point 最近的线段的中心点，并根据线宽调整中心位置。
        """
        path_points = np.concatenate(polygons)  # 展开多边形点集为连续路径点
        curr_x, curr_y = curr_point

        # 初始化最小距离和最近中心点
        min_distance = float('inf')
        nearest_center = None

        # 遍历路径的每段线段
        for i in range(len(path_points) - 1):
            # 计算线段两端点
            x1, y1 = path_points[i]
            x2, y2 = path_points[i + 1]

            # 计算线段方向向量和长度
            dx, dy = x2 - x1, y2 - y1
            length = math.sqrt(dx**2 + dy**2)

            # 单位方向向量
            direction_x = dx / length
            direction_y = dy / length

            # 正交方向向量（法向量）
            normal_x = -direction_y
            normal_y = direction_x

            # 计算线段中心点
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2

            # 根据线宽调整中心点
            adjusted_center_x = center_x + normal_x * (line_width / 2)
            adjusted_center_y = center_y + normal_y * (line_width / 2)

            # 计算调整后中心点到 curr_point 的距离
            distance = np.sqrt((adjusted_center_x - curr_x)**2 + (adjusted_center_y - curr_y)**2)

            # 更新最近的中心点
            if distance < min_distance:
                min_distance = distance
                nearest_center = (adjusted_center_x, adjusted_center_y)

        return nearest_center



    def adjust_air_bridge_position_for_bend(prev_point, curr_point, next_point, bend_radius,width):
        """
        优化空气桥偏移量，精确计算圆角与路径的接触点，动态调整修正因子。
        """

        path_points = [prev_point, curr_point, next_point]
        path = gdspy.FlexPath(
            path_points,
            width=width,
            corners="circular bend",
            bend_radius=bend_radius
        )
        polygons = path.to_polygonset().polygons  # 提取多边形点集
        gds_pos = find_nearest_segment_center(polygons,curr_point,width)

        # 向量计算
        v1x, v1y = prev_point[0] - curr_point[0], prev_point[1] - curr_point[1]
        v2x, v2y = next_point[0] - curr_point[0], next_point[1] - curr_point[1]

        # 归一化向量
        v1_length = math.sqrt(v1x**2 + v1y**2)
        v2_length = math.sqrt(v2x**2 + v2y**2)
        v1x, v1y = v1x / v1_length, v1y / v1_length
        v2x, v2y = v2x / v2_length, v2y / v2_length


        # 计算角平分线向量
        bisector_x = v1x + v2x
        bisector_y = v1y + v2y
        bisector_length = math.sqrt(bisector_x**2 + bisector_y**2)
        bisector_x /= bisector_length
        bisector_y /= bisector_length

        # 计算切线方向的旋转角度
        rotation_angle = math.atan2(bisector_y, bisector_x)

        return gds_pos, rotation_angle + math.pi / 2  # 顺时针旋转90度


    def is_point_in_flexpath(point, polygons, tolerance):
        """
        检查点是否在路径的多边形范围内，并允许一定容差。
        """
        px, py = point

        # 判断点是否在多边形内（严格条件）
        for poly in polygons:
            if gdspy.inside([point], [poly], short_circuit=True)[0]:
                return True

            # 判断点到多边形边界的最短距离
            for i in range(len(poly)):
                x1, y1 = poly[i - 1]
                x2, y2 = poly[i]

                # 计算点到线段的最短距离
                dx, dy = x2 - x1, y2 - y1
                length_squared = dx**2 + dy**2
                if length_squared == 0:
                    distance = math.sqrt((px - x1)**2 + (py - y1)**2)
                else:
                    t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / length_squared))
                    proj_x = x1 + t * dx
                    proj_y = y1 + t * dy
                    distance = math.sqrt((px - proj_x)**2 + (py - proj_y)**2)

                if distance <= tolerance:
                    return True

        return False
    
    def do_lines_intersect(p1, p2, q1, q2):
        """
        判断两条线段 (p1, p2) 和 (q1, q2) 是否相交。
        
        参数:
        p1, p2: 第一条线段的起点和终点 (x1, y1), (x2, y2)
        q1, q2: 第二条线段的起点和终点 (x3, y3), (x4, y4)
        
        返回:
        bool: 如果相交，则返回 True；否则返回 False。
        """

        def orientation(p, q, r):
            """
            计算三个点的方向。
            0 -> p, q 和 r 在同一条直线上
            1 -> 顺时针
            2 -> 逆时针
            """
            val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
            if val == 0:
                return 0  # collinear
            elif val > 0:
                return 1  # clockwise
            else:
                return 2  # counterclockwise

        def on_segment(p, q, r):
            """检查点 q 是否在线段 pr 上"""
            return (min(p[0], r[0]) <= q[0] <= max(p[0], r[0]) and
                    min(p[1], r[1]) <= q[1] <= max(p[1], r[1]))

        # 找到四个方向
        o1 = orientation(p1, p2, q1)
        o2 = orientation(p1, p2, q2)
        o3 = orientation(q1, q2, p1)
        o4 = orientation(q1, q2, p2)

        # 普通情况
        if o1 != o2 and o3 != o4:
            return True

        # 特殊情况
        # p1, p2 和 q1 在同一条直线上，检查 q1 是否在线段 p1p2 上
        if o1 == 0 and on_segment(p1, q1, p2):
            return True
        # p1, p2 和 q2 在同一条直线上，检查 q2 是否在线段 p1p2 上
        if o2 == 0 and on_segment(p1, q2, p2):
            return True
        # q1, q2 和 p1 在同一条直线上，检查 p1 是否在线段 q1q2 上
        if o3 == 0 and on_segment(q1, p1, q2):
            return True
        # q1, q2 和 p2 在同一条直线上，检查 p2 是否在线段 q1q2 上
        if o4 == 0 and on_segment(q1, p2, q2):
            return True

        return False
    

    def angle_to_path_vector(angle, length):
        """
        根据给定的角度和长度计算路径向量。
        
        参数:
        angle: 以弧度表示的角度
        length: 向量的长度
        
        返回:
        path_vector: 计算得到的路径向量 (dx, dy)
        """
        dx = length * math.cos(angle)  # x 分量
        dy = length * math.sin(angle)  # y 分量
        return (dx, dy)
    def is_point_intersect(point , path_vector , last_point , last_path_vector ):
        
        def get_line(point , path_vector ):
            line = []
            # 垂线的长度
            perpendicular_length = 65

            # 计算垂线方向
            perp_dx = -path_vector[1]  # 垂线方向 x 分量
            perp_dy = path_vector[0]   # 垂线方向 y 分量

            # 垂线的两个端点
            perp1 = (point[0] + (perp_dx / math.sqrt(perp_dx**2 + perp_dy**2)) * (perpendicular_length ),
                        point[1] + (perp_dy / math.sqrt(perp_dx**2 + perp_dy**2)) * (perpendicular_length))

            perp2 = (point[0] - (perp_dx / math.sqrt(perp_dx**2 + perp_dy**2)) * (perpendicular_length ),
                        point[1] - (perp_dy / math.sqrt(perp_dx**2 + perp_dy**2)) * (perpendicular_length ))

            # 平行线的长度
            parallel_length = 50

            # 平行线的两个端点
            parallel1_start = (perp1[0] + (path_vector[0] / math.sqrt(path_vector[0]**2 + path_vector[1]**2)) * (parallel_length / 2),
                            perp1[1] + (path_vector[1] / math.sqrt(path_vector[0]**2 + path_vector[1]**2)) * (parallel_length / 2))

            parallel1_end = (perp1[0] - (path_vector[0] / math.sqrt(path_vector[0]**2 + path_vector[1]**2)) * (parallel_length / 2),
                            perp1[1] - (path_vector[1] / math.sqrt(path_vector[0]**2 + path_vector[1]**2)) * (parallel_length / 2))
            
            parallel2_start = (perp2[0] + (path_vector[0] / math.sqrt(path_vector[0]**2 + path_vector[1]**2)) * (parallel_length / 2),
                            perp2[1] + (path_vector[1] / math.sqrt(path_vector[0]**2 + path_vector[1]**2)) * (parallel_length / 2))

            parallel2_end = (perp2[0] - (path_vector[0] / math.sqrt(path_vector[0]**2 + path_vector[1]**2)) * (parallel_length / 2),
                            perp2[1] - (path_vector[1] / math.sqrt(path_vector[0]**2 + path_vector[1]**2)) * (parallel_length / 2))

            line.append((parallel1_start,parallel1_end))
            line.append((parallel2_start,parallel2_end))
            return line
        
        #print('point:' , point)
        #print('last_ponit:' , last_point)
        
        ok = 1
        
        line1 = get_line(point , path_vector )
        line2 = get_line(last_point , last_path_vector)

        #print('line1:' , line1)
        #print('line2:' , line2)


        for i in range(0,2,1) :
            for j in range(0,2,1):
                if(do_lines_intersect(line1[i][0] , line1[i][1] , line2[j][0] , line2[j][1]) == True):
                    ok = 0

        if ok == 0:
            return True
        else :
            return False
        

    def is_point_intersect_for_bend(point , path_vector , last_point , last_path_vector ):
        
        def get_line_for_bend_2(point , path_vector ):
            line = []
            # 垂线的长度
            perpendicular_length = 15

            # 计算垂线方向
            perp_dx = -path_vector[1]  # 垂线方向 x 分量
            perp_dy = path_vector[0]   # 垂线方向 y 分量

            # 垂线的两个端点
            perp1 = (point[0] + (perp_dx / math.sqrt(perp_dx**2 + perp_dy**2)) * (perpendicular_length ),
                        point[1] + (perp_dy / math.sqrt(perp_dx**2 + perp_dy**2)) * (perpendicular_length))

            perp2 = (point[0] - (perp_dx / math.sqrt(perp_dx**2 + perp_dy**2)) * (perpendicular_length ),
                        point[1] - (perp_dy / math.sqrt(perp_dx**2 + perp_dy**2)) * (perpendicular_length ))

            # 垂线的长度
            parallel_length = 50

            # 垂线的两个端点
            parallel1 = (perp1[0] + (path_vector[0] / math.sqrt(path_vector[0]**2 + path_vector[1]**2)) * (parallel_length / 2),
                            perp1[1] + (path_vector[1] / math.sqrt(path_vector[0]**2 + path_vector[1]**2)) * (parallel_length / 2))

            parallel2 = (perp1[0] - (path_vector[0] / math.sqrt(path_vector[0]**2 + path_vector[1]**2)) * (parallel_length / 2),
                            perp1[1] - (path_vector[1] / math.sqrt(path_vector[0]**2 + path_vector[1]**2)) * (parallel_length / 2))
            
            parallel3 = (perp2[0] + (path_vector[0] / math.sqrt(path_vector[0]**2 + path_vector[1]**2)) * (parallel_length / 2),
                            perp2[1] + (path_vector[1] / math.sqrt(path_vector[0]**2 + path_vector[1]**2)) * (parallel_length / 2))

            parallel4 = (perp2[0] - (path_vector[0] / math.sqrt(path_vector[0]**2 + path_vector[1]**2)) * (parallel_length / 2),
                            perp2[1] - (path_vector[1] / math.sqrt(path_vector[0]**2 + path_vector[1]**2)) * (parallel_length / 2))
            
            parallel1_1 = (parallel1[0] + (perp_dx / math.sqrt(perp_dx**2 + perp_dy**2)) * (parallel_length ),
                        parallel1[1] + (perp_dy / math.sqrt(perp_dx**2 + perp_dy**2)) * (parallel_length))
            
            parallel2_1 = (parallel2[0] + (perp_dx / math.sqrt(perp_dx**2 + perp_dy**2)) * (parallel_length ),
                        parallel2[1] + (perp_dy / math.sqrt(perp_dx**2 + perp_dy**2)) * (parallel_length))

            parallel3_1 = (parallel3[0] - (perp_dx / math.sqrt(perp_dx**2 + perp_dy**2)) * (parallel_length ),
                        parallel3[1] - (perp_dy / math.sqrt(perp_dx**2 + perp_dy**2)) * (parallel_length))
            parallel4_1 = (parallel4[0] - (perp_dx / math.sqrt(perp_dx**2 + perp_dy**2)) * (parallel_length ),
                        parallel4[1] - (perp_dy / math.sqrt(perp_dx**2 + perp_dy**2)) * (parallel_length))

            line.append((parallel1,parallel1_1))
            line.append((parallel2,parallel2_1))
            line.append((parallel3,parallel3_1))
            line.append((parallel4,parallel4_1))

            return line
        
        def get_line_for_bend_1(point , path_vector ):
            line = []
            # 垂线的长度
            perpendicular_length = 65

            # 计算垂线方向
            perp_dx = -path_vector[1]  # 垂线方向 x 分量
            perp_dy = path_vector[0]   # 垂线方向 y 分量

            # 垂线的两个端点
            perp1 = (point[0] + (perp_dx / math.sqrt(perp_dx**2 + perp_dy**2)) * (perpendicular_length ),
                        point[1] + (perp_dy / math.sqrt(perp_dx**2 + perp_dy**2)) * (perpendicular_length))

            perp2 = (point[0] - (perp_dx / math.sqrt(perp_dx**2 + perp_dy**2)) * (perpendicular_length ),
                        point[1] - (perp_dy / math.sqrt(perp_dx**2 + perp_dy**2)) * (perpendicular_length ))

            # 平行线的长度
            parallel_length = 50

            # 平行线的两个端点
            parallel1_start = (perp1[0] + (path_vector[0] / math.sqrt(path_vector[0]**2 + path_vector[1]**2)) * (parallel_length / 2),
                            perp1[1] + (path_vector[1] / math.sqrt(path_vector[0]**2 + path_vector[1]**2)) * (parallel_length / 2))

            parallel1_end = (perp1[0] - (path_vector[0] / math.sqrt(path_vector[0]**2 + path_vector[1]**2)) * (parallel_length / 2),
                            perp1[1] - (path_vector[1] / math.sqrt(path_vector[0]**2 + path_vector[1]**2)) * (parallel_length / 2))
            
            parallel2_start = (perp2[0] + (path_vector[0] / math.sqrt(path_vector[0]**2 + path_vector[1]**2)) * (parallel_length / 2),
                            perp2[1] + (path_vector[1] / math.sqrt(path_vector[0]**2 + path_vector[1]**2)) * (parallel_length / 2))

            parallel2_end = (perp2[0] - (path_vector[0] / math.sqrt(path_vector[0]**2 + path_vector[1]**2)) * (parallel_length / 2),
                            perp2[1] - (path_vector[1] / math.sqrt(path_vector[0]**2 + path_vector[1]**2)) * (parallel_length / 2))

            line.append((parallel1_start,parallel1_end))
            line.append((parallel2_start,parallel2_end))
            return line
        
        #print('point:' , point)
        #print('last_ponit:' , last_point)
        
        ok = 1
        
        line1 = get_line_for_bend_1(point , path_vector )
        line2 = get_line_for_bend_2(last_point , last_path_vector)

        print('line1:' , line1)
        print('line2:' , line2)


        for i in range(0,2,1) :
            for j in range(0,4,1):
                if(do_lines_intersect(line1[i][0] , line1[i][1] , line2[j][0] , line2[j][1]) == True):
                    ok = 0

        if ok == 0:
            return True
        else :
            return False



    options = Dict()

    # 创建 FlexPath 并提取多边形
    path = gdspy.FlexPath(pos, width=width, corners="circular bend", bend_radius=bend_radius)
    polygons = path.to_polygonset().polygons



    bridge_num_map = dict()
    first_bridge_num_map = dict()
    last_num_bridges = 0 
    last_path_vector = 0
    path_vector = 0
    # 路径中段空气桥添加
    num_bridges = 0
    # 路径中段空气桥添加
    for i in range(len(pos) - 1):
        start, end = pos[i], pos[i + 1]
        last_path_vector = path_vector
        # 计算段长度（考虑线宽调整）
        path_vector = np.array([end[0] - start[0], end[1] - start[1]])

        path_length = np.linalg.norm(path_vector) - bend_radius * 2  # 减去两端圆角部分
        flag = False
        # print('times : {} , path_verctor : {} , path_length : {} '.format(i , path_vector , path_length))
        # 计算有效路径长度内空气桥的数量
        if path_length > 0:
            last_num_bridges = num_bridges
            num_bridges = max(1, math.ceil(path_length / spacing))
            bridge_num_map[i] = num_bridges
            for j in range(1, num_bridges + 1):
                # 插值计算空气桥中心位置
                t = j / (num_bridges + 1)
                center_x = (1 - t) * start[0] + t * end[0]
                center_y = (1 - t) * start[1] + t * end[1]

                gds_pos = (center_x, center_y)

                if i > 0  and j == 1:

                    last_point = options['air_bridge_line_{}_{}'.format(i-1 , last_num_bridges)]
                    if is_point_in_flexpath(gds_pos, polygons, width / 2 + 5):  # 增加5个单位容差
                        if is_point_intersect(gds_pos ,path_vector ,  last_point.gds_pos , last_path_vector) :
                            print('line {} , num {} intersect'.format(i, j))
                            del options[last_point.name]
                            last_point = options['air_bridge_line_{}_{}'.format(i-1 , last_num_bridges-1)]
                            bridge_num_map[i-1] = last_num_bridges-1
                        else :
                            angle = math.atan2(path_vector[1], path_vector[0])
                            if flag == False :
                                first_bridge_num_map[i] = j
                                flag = True
                            option = Dict(
                                name=f"air_bridge_line_{i}_{j}",
                                type="AirbridgeNb",
                                chip=chip_type,
                                gds_pos=gds_pos,
                                rotation=angle
                            )
                            options[option.name] = option

                else :
                    # 检查中心点是否满足范围条件
                    if is_point_in_flexpath(gds_pos, polygons, width / 2 + 5):  # 增加5个单位容差
                        
                        angle = math.atan2(path_vector[1], path_vector[0])
                        if flag == False :
                            first_bridge_num_map[i] = j
                            flag = True                       
                        option = Dict(
                            name=f"air_bridge_line_{i}_{j}",
                            type="AirbridgeNb",
                            chip=chip_type,
                            gds_pos=gds_pos,
                            rotation=angle
                        )
                        options[option.name] = option
    # 路径拐角处空气桥添加
    for i in range(1, len(pos) - 1):
        prev_point, curr_point, next_point = pos[i - 1], pos[i], pos[i + 1]

        # 调整拐角位置和旋转角度
        adjusted_pos, rotation_angle = adjust_air_bridge_position_for_bend(
            prev_point, curr_point, next_point, bend_radius, width
        )

        last_point = options['air_bridge_line_{}_{}'.format(i-1 , bridge_num_map[i-1])]
        next_point1 = options['air_bridge_line_{}_{}'.format(i , first_bridge_num_map[i])]
        # 检查中心点是否满足范围条件  这部分逻辑要继续完善
        if is_point_in_flexpath(adjusted_pos, polygons, width / 2 + 5):  # 增加5个单位容差
            path_vector_now = angle_to_path_vector(rotation_angle, 1)
            print('rotation_angle :' ,rotation_angle)
            print('last_point.angle:' , last_point.rotation)
            print('adjusted_pos' , adjusted_pos)
            last_path_vector = angle_to_path_vector(last_point.rotation , 1)
            next_path_vector = angle_to_path_vector(next_point1.rotation , 1)
            if  not (is_point_intersect_for_bend(adjusted_pos , path_vector_now , last_point.gds_pos , last_path_vector)) and not (is_point_intersect_for_bend(adjusted_pos , path_vector_now , next_point1.gds_pos , next_path_vector)) :
                option = Dict(
                    name=f"air_bridge_pos_{i}",
                    type="AirbridgeNb",
                    chip=chip_type,
                    gds_pos=adjusted_pos,
                    rotation=rotation_angle
                )
                options[option.name] = option
    return options