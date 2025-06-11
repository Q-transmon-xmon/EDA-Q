def add_tunnel_bridges_czy(pos, bend_radius, width1 , gap, spacing=120, chip_type="chip3", width=10 , tunnel_bridge_type = 'Bridgecover'):
    options = dict()
    from addict import Dict
    import math
    import numpy as np
    import gdspy

    point_part = dict()
    default_length = 80
    def adjust_tunnel_bridge_position_for_bend(prev_point, curr_point, next_point, bend_radius,width):
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
            #gds_pos = find_nearest_segment_center(polygons,curr_point,width)

            # 向量计算
            v1x, v1y = prev_point[0] - curr_point[0], prev_point[1] - curr_point[1]
            v2x, v2y = next_point[0] - curr_point[0], next_point[1] - curr_point[1]

            # 归一化向量
            v1_length = math.sqrt(v1x**2 + v1y**2)
            v2_length = math.sqrt(v2x**2 + v2y**2)
            v1x, v1y = v1x / v1_length, v1y / v1_length
            v2x, v2y = v2x / v2_length, v2y / v2_length

            def angle_between_vectors(vec1, vec2):
                # 计算每个向量的角度（相对于 x 轴）
                angle1 = math.atan2(vec1[1], vec1[0])
                angle2 = math.atan2(vec2[1], vec2[0])
                
                # 计算角度差（从向量1旋转到向量2）
                delta_angle = angle2 - angle1
                
                # 规范化到 -π 到 π 的范围（可选）
                if delta_angle > math.pi:
                    delta_angle -= 2*math.pi
                elif delta_angle < -math.pi:
                    delta_angle += 2*math.pi
                
                return angle1 , angle2 , delta_angle

            angle1 , angle2 ,rotation_angle = angle_between_vectors((v1x , v1y) , (v2x , v2y))

            return angle1 , angle2 ,rotation_angle   # 顺时针旋转90度
    def find_points_on_segment(A, B, length=80):
        # 计算线段长度
        L = math.dist(A, B)
        if L <= length:
            return (0,0) , (0,0)
        
        dx = B[0] - A[0]
        dy = B[1] - A[1]
        
        ux = dx / L
        uy = dy / L
        
        t = (L - length) / 2
    
        P1 = (A[0] + t * ux, A[1] + t * uy)
        P2 = (B[0] - t * ux, B[1] - t * uy)
        
        return P1, P2
    for i in range(len(pos) - 2):
        start, end , next = pos[i], pos[i + 1] , pos[i + 2]
        path_vector = np.array([end[0] - start[0], end[1] - start[1]])
        path_length = np.linalg.norm(path_vector) - bend_radius * 2  # Subtract the rounded corners at both ends
        if path_length > 0:
            num_bridges = max(1, math.ceil(path_length / spacing))
            j = 1
            t = j / (num_bridges + 1)
            center_x = (1 - t) * end[0] + t * start[0]
            center_y = (1 - t) * end[1] + t * start[1]

            gds_pos1 = (center_x, center_y)
        
        path_vector1 = np.array([next[0] - end[0], next[1] - end[1]])
        path_length = np.linalg.norm(path_vector1) - bend_radius * 2  # Subtract the rounded corners at both ends
        if path_length > 0:
            num_bridges = max(1, math.ceil(path_length / spacing))
            j = 1
            t = j / (num_bridges + 1)
            center_x = (1 - t) * end[0] + t * next[0]
            center_y = (1 - t) * end[1] + t * next[1]

            gds_pos2 = (center_x, center_y)
        # 调整拐角位置和旋转角度

        angle1 , angle2 ,rotation_angle = adjust_tunnel_bridge_position_for_bend(
            start, end, next, bend_radius, width
        )

        print(angle1 , angle2 ,rotation_angle)
        direction = 0
        if(pos[i+1][1] >= pos[i][1]):
            direction = 1
        else :
            direction = 0


        angle1_1 = angle1 + np.pi/2
        angle2_1 = angle2 + np.pi/2 

        bg_width = width1 * 2 + gap

        x1_1 = gds_pos1[0] + bg_width * math.cos(angle1_1) / 2
        x1_2 = gds_pos1[0] - bg_width * math.cos(angle1_1) / 2
        y1_1 = gds_pos1[1] + bg_width * math.sin(angle1_1) / 2
        y1_2 = gds_pos1[1] - bg_width * math.sin(angle1_1) / 2

        x2_1 = gds_pos2[0] + bg_width * math.cos(angle2_1) / 2
        x2_2 = gds_pos2[0] - bg_width * math.cos(angle2_1) / 2
        y2_1 = gds_pos2[1] + bg_width * math.sin(angle2_1) / 2
        y2_2 = gds_pos2[1] - bg_width * math.sin(angle2_1) / 2

        if rotation_angle < 0 :
            line1_in = (x1_2 , y1_2)
            line1_out = (x1_1 , y1_1)
            line2_in = (x2_1 , y2_1)
            line2_out = (x2_2 , y2_2)
            print(line1_in , line1_out , line2_in , line2_out)

        else :
            line1_out = (x1_2 , y1_2)
            line1_in = (x1_1 , y1_1)
            line2_out = (x2_1 , y2_1)
            line2_in = (x2_2 , y2_2)
            print(line1_in , line1_out , line2_in , line2_out)

        pos1 = list()
        pos1.append(gds_pos1)
        pos1.append(end)
        pos1.append(gds_pos2)

        point_part['{}'.format(i)] = pos1

        option =  Dict( name="Bridgecover_bend{}".format(i),
            type= tunnel_bridge_type,
            chip = "chip3",
            outline = [], 
            path = pos1,  
            corner_radius = bend_radius,
            width = width1,
            gap = gap,
            direction = direction,
            line1_in = line1_in,
            line1_out = line1_out,
            line2_in = line2_in,
            line2_out = line2_out,
            angle = rotation_angle)
        

        options[option.name] = option
    
    start = (0,0)
    for i in range(len(point_part) + 1):
        if( i >= len(point_part)):
            end = pos[len(pos)-1]
        else :
            end = point_part[str(i)][0]
        print('start :' + str(start) + ' end : ' +str(end))
        target1 , target2 = find_points_on_segment(start , end , 200)
        if target1 == (0,0) and target2 == (0,0):
            start = point_part[str(i)][2]
            continue
        vx , vy = target2[0] - target1[0] , target2[1] - target1[1]
        angle = math.atan2(vy , vx)
        if(vx == 0):
            angle = np.pi / 2
        print('angle :' , angle)
        angle += np.pi / 2

        x1_1 = target1[0] + bg_width * math.cos(angle) / 2
        x1_2 = target1[0] - bg_width * math.cos(angle) / 2
        y1_1 = target1[1] + bg_width * math.sin(angle) / 2
        y1_2 = target1[1] - bg_width * math.sin(angle) / 2

        x2_1 = target2[0] + bg_width * math.cos(angle) / 2
        x2_2 = target2[0] - bg_width * math.cos(angle) / 2
        y2_1 = target2[1] + bg_width * math.sin(angle) / 2
        y2_2 = target2[1] - bg_width * math.sin(angle) / 2

        if(angle - np.pi / 2)  >= 0:

            line1_in = (x1_1 , y1_1)
            line1_out = (x1_2 , y1_2)
            line2_in = (x2_1 , y2_1)
            line2_out = (x2_2 , y2_2)
        else :
            line1_in = (x1_2 , y1_2)
            line1_out = (x1_1 , y1_1)
            line2_in = (x2_2 , y2_2)
            line2_out = (x2_1 , y2_1)


        tmp_pos = list()
        tmp_pos.append(target1)
        tmp_pos.append(target2)

        option =  Dict( name="Bridgecover_line{}".format(i),
            type= tunnel_bridge_type,
            chip = "chip3",
            outline = [], 
            path = tmp_pos,  
            corner_radius = bend_radius,
            width = width1,
            gap = gap,
            line1_in = line1_in,
            line1_out = line1_out,
            line2_in = line2_in,
            line2_out = line2_out,
            angle = angle - np.pi/2,
            line = 1)
        options[option.name] = option
        
        if i >= len(point_part):
            break
        start = point_part[str(i)][2]

    print('point_part'  , point_part)
    return options