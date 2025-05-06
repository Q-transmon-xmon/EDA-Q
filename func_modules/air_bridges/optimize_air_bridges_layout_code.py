import pyclipper

def optimize_air_bridges_layout(gds_ops):
    """
    
    """

    # uncoupling
    import copy
    gds_ops = copy.deepcopy(gds_ops)
    new_gds_ops = copy.deepcopy(gds_ops)

    # your code
    print("to be continued...")

    print("to be continued...")
    #print(new_gds_ops)

    airbridge_dict = new_gds_ops['air_bridges']
    #print(airbridge_dict)

    def get_rectangle_corners_x(polygon):
        """
        get four points for a rectangle
        
        :param p1: first points (x1, y1)
        :param p2: second points (x2, y2)
        :return: four points
        """

        #rotation += np.pi / 2
        p1 = polygon[6]
        p2 = polygon[7]

        

        p3 = polygon[8]
        p4 = polygon[9]
        x1, y1 = p1
        x2, y2 = p2

        # 计算其他两个点
        corners1 = [
            [x1, y1],  # 左下角
            [x2, y1],  # 右下角
            [x2, y2],  # 右上角
            [x1, y2]   # 左上角
        ]

        corners1.append([x1,y1])
        x3, y3 = p3
        x4, y4 = p4

        # 计算其他两个点
        corners2 = [
            [x3, y3],  # 左下角
            [x4, y3],  # 右下角
            [x4, y4],  # 右上角
            [x3, y4]   # 左上角
        ]
        corners2.append([x3,y3])
        return corners1 + corners2

    i = 1
    
    del_flag = False
    while True:
        target = 'air_bridge_pos_{}'.format(i)
        if target in airbridge_dict:
            print(i)
            if del_flag == True:
                j = 2
            else :
                j = 1
            last = ''
            tmp1 = 'air_bridge_line_{}_{}'.format(i-1 , j)
            while tmp1 in airbridge_dict :
                last = tmp1
                j += 1
                tmp1 = 'air_bridge_line_{}_{}'.format(i-1 , j)
            next = 'air_bridge_line_{}_{}'.format(i , 1)
            polygon_A = airbridge_dict[last]['outline']
            polygon_B = airbridge_dict[target]['outline']
            polygon_C = airbridge_dict[next]['outline']

            # first judge outside
            polygon_A1 = get_rectangle_corners_x(polygon_A)
            polygon_B1 = get_rectangle_corners_x(polygon_B)
            polygon_C1 = get_rectangle_corners_x(polygon_C)
            #print('polygon_a:' , polygon_A1)
            #print('polygon_c:' , polygon_C1)
            #print('polygon_b:' , polygon_B1)
            pc = pyclipper.Pyclipper()
            pc.AddPath(polygon_A1, pyclipper.PT_SUBJECT, True)
            pc.AddPath(polygon_C1, pyclipper.PT_CLIP, True)
            solution = pc.Execute(pyclipper.CT_INTERSECTION, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)
            if len(solution) > 0:
                print('del two ends')
                del airbridge_dict[last]
                del airbridge_dict[next]
                del_flag = True
            else :
                # outside intersect is none :
                print('prepare del for bend')
                del_flag = False
                pc1 = pyclipper.Pyclipper()
                pc1.AddPath(polygon_A1, pyclipper.PT_SUBJECT, True)
                pc1.AddPath(polygon_B1, pyclipper.PT_CLIP, True)
                solution1 = pc1.Execute(pyclipper.CT_INTERSECTION, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)
                pc2 = pyclipper.Pyclipper()
                pc2.AddPath(polygon_B1, pyclipper.PT_SUBJECT, True)
                pc2.AddPath(polygon_C1, pyclipper.PT_CLIP, True)
                solution2 = pc2.Execute(pyclipper.CT_INTERSECTION, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)
                if (len(solution1) > 0) or (len(solution2) > 0):
                    print('del bend')
                    del airbridge_dict[target]
            i += 1
        else :
            break

    new_gds_ops['air_bridges'] = airbridge_dict
    print(new_gds_ops)
    return new_gds_ops
    return new_gds_ops