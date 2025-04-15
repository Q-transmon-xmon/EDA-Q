#######################################################################
# Add air bridges for a specified path, supporting the arrangement of air bridges at path corners and middle sections, ensuring geometric conditions are met
#######################################################################

def add_air_bridges(pos, bend_radius, spacing=120, chip_name="chip3"):
    """
    Add air bridges, supporting the arrangement at path corners and middle sections.

    Input:
        pos: list, a list of coordinates for the path.
        bend_radius: float, the radius of the rounded corners in the path.
        spacing: float, the spacing between air bridges, default is 120.
        chip_name: str, the name of the chip to which the air bridges belong, default is "chip3".

    Output:
        options: Dict, a collection of parameters for all air bridges.
    """
    from addict import Dict
    import math
    
    def adjust_air_bridge_position_for_bend(prev_point, curr_point, next_point, bend_radius):
        """
        Optimize the offset of the air bridge, accurately calculate the contact point between the rounded corner and the path, and dynamically adjust the correction factor.

        Input:
            prev_point: tuple, the coordinates of the previous point on the path.
            curr_point: tuple, the coordinates of the current point.
            next_point: tuple, the coordinates of the next point on the path.
            bend_radius: float, the radius of the rounded corner.

        Output:
            adjusted_pos: tuple, the adjusted coordinates of the air bridge center.
            rotation_angle: float, the rotation angle of the air bridge.
        """
        # Vector calculation
        v1x, v1y = prev_point[0] - curr_point[0], prev_point[1] - curr_point[1]
        v2x, v2y = next_point[0] - curr_point[0], next_point[1] - curr_point[1]

        # Normalize vectors
        v1_length = math.sqrt(v1x**2 + v1y**2)
        v2_length = math.sqrt(v2x**2 + v2y**2)
        v1x, v1y = v1x / v1_length, v1y / v1_length
        v2x, v2y = v2x / v2_length, v2y / v2_length

        # Calculate the cosine and sine of the angle between vectors
        dot_product = v1x * v2x + v1y * v2y  # Dot product
        angle_cos = dot_product  # Cosine of the angle
        angle = math.acos(angle_cos)  # Angle in radians

        # Dynamically adjust the correction factor
        deviation_from_right = abs(angle - math.pi / 2)  # Absolute deviation from the right angle
        if angle > math.pi / 2:  # Obtuse angle
            offset_factor = 0.4 - 0.5 * (deviation_from_right / (math.pi / 2))
        else:  # Acute angle
            offset_factor = 0.4 + 0.8 * (deviation_from_right / (math.pi / 2))

        # Calculate the angle bisector vector
        bisector_x = v1x + v2x
        bisector_y = v1y + v2y
        bisector_length = math.sqrt(bisector_x**2 + bisector_y**2)
        bisector_x /= bisector_length
        bisector_y /= bisector_length

        # Calculate the offset
        offset_x = bisector_x * (bend_radius / math.sqrt(1 - angle_cos**2)) * offset_factor
        offset_y = bisector_y * (bend_radius / math.sqrt(1 - angle_cos**2)) * offset_factor

        # Adjusted position
        adjusted_x = curr_point[0] + offset_x
        adjusted_y = curr_point[1] + offset_y

        # Calculate the rotation angle of the tangent direction
        rotation_angle = math.atan2(bisector_y, bisector_x)

        return (adjusted_x, adjusted_y), rotation_angle + math.pi / 2  # Rotate 90 degrees clockwise
    
    options = Dict()
    for i in range(1, len(pos) - 1):
        prev_point, curr_point, next_point = pos[i - 1], pos[i], pos[i + 1]

        adjusted_pos, rotation_angle = adjust_air_bridge_position_for_bend(prev_point, curr_point, next_point, bend_radius)

        option = Dict(
            name=f"air_bridge_pos_{i}",
            type="AirBridge",
            chip=chip_name,
            center_pos=adjusted_pos,
            rotation=rotation_angle
        )
        options[option.name] = option
    for i in range(len(pos) - 1):
        start, end = pos[i], pos[i + 1]
        length = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
        num_bridges = math.ceil(length / spacing)

        for j in range(1, num_bridges):
            t = j / num_bridges
            center_x = (1 - t) * start[0] + t * end[0]
            center_y = (1 - t) * start[1] + t * end[1]

            angle = math.atan2(end[1] - start[1], end[0] - start[0])

            option = Dict(
                name=f"air_bridge_line_{i}_{j}",
                type="AirBridge",
                chip=chip_name,
                center_pos=(center_x, center_y),
                rotation=angle
            )
            options[option.name] = option
    print("生成空气桥的数量为： {}".format(len(options)))
    return options

def add_air_bridges2(pos, bend_radius, spacing=120, chip_type="chip3", width=10, air_bridge_type="AirBridge"):
    """
    Add air bridges to ensure that the center points meet the distance or area conditions relative to the FlexPath polygons.

    Input:
        pos: list, a list of coordinates for the path.
        bend_radius: float, the radius of the rounded corners in the path.
        spacing: float, the spacing between air bridges, default is 120.
        chip_type: str, the name of the chip to which the air bridges belong, default is "chip3".
        width: float, the width of the path.
        air_bridge_type: str, the type of air bridge, default is "AirBridge".

    Output:
        options: Dict, a collection of parameters for all air bridges.
    """
    import numpy as np
    import math
    
    def find_nearest_segment_center(polygons, curr_point, line_width):
        """
        Find the center of the segment closest to curr_point and adjust the center position according to the line width.

        Input:
            polygons: list, a list of polygon points for the path.
            curr_point: tuple, the coordinates of the current reference point.
            line_width: float, the width of the path.

        Output:
            nearest_center: tuple, the coordinates of the center of the nearest segment.
        """
        path_points = np.concatenate(polygons)  # Concatenate polygon point sets into a continuous path point array
        curr_x, curr_y = curr_point

        # Initialize minimum distance and nearest center point
        min_distance = float('inf')
        nearest_center = None

        # Iterate over each segment of the path
        for i in range(len(path_points) - 1):
            # Calculate the endpoints of the segment
            x1, y1 = path_points[i]
            x2, y2 = path_points[i + 1]

            # Calculate the direction vector and length of the segment
            dx, dy = x2 - x1, y2 - y1
            length = math.sqrt(dx**2 + dy**2)

            # Unit direction vector
            direction_x = dx / length
            direction_y = dy / length

            # Orthogonal direction vector (normal vector)
            normal_x = -direction_y
            normal_y = direction_x

            # Calculate the center of the segment
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2

            # Adjust the center point according to the line width
            adjusted_center_x = center_x + normal_x * (line_width / 2)
            adjusted_center_y = center_y + normal_y * (line_width / 2)

            # Calculate the distance from the adjusted center point to curr_point
            distance = np.sqrt((adjusted_center_x - curr_x)**2 + (adjusted_center_y - curr_y)**2)

            # Update the nearest center point
            if distance < min_distance:
                min_distance = distance
                nearest_center = (adjusted_center_x, adjusted_center_y)

        return nearest_center



    def adjust_air_bridge_position_for_bend(prev_point, curr_point, next_point, bend_radius, width):
        """
        Optimize the offset of the air bridge, accurately calculate the contact point between the rounded corner and the path, and dynamically adjust the correction factor.

        Input:
            prev_point: tuple, the coordinates of the previous point on the path.
            curr_point: tuple, the coordinates of the current point.
            next_point: tuple, the coordinates of the next point on the path.
            bend_radius: float, the radius of the rounded corner of the path.
            width: float, the width of the path.

        Output:
            center_pos: tuple, the adjusted coordinates of the air bridge center.
            rotation_angle: float, the rotation angle of the air bridge.
        """

        path_points = [prev_point, curr_point, next_point]
        path = gdspy.FlexPath(
            path_points,
            width=width,
            corners="circular bend",
            bend_radius=bend_radius
        )
        polygons = path.to_polygonset().polygons  # Extract the polygon set
        center_pos = find_nearest_segment_center(polygons, curr_point, width)

        # Vector calculation
        v1x, v1y = prev_point[0] - curr_point[0], prev_point[1] - curr_point[1]
        v2x, v2y = next_point[0] - curr_point[0], next_point[1] - curr_point[1]

        # Normalize vectors
        v1_length = math.sqrt(v1x**2 + v1y**2)
        v2_length = math.sqrt(v2x**2 + v2y**2)
        v1x, v1y = v1x / v1_length, v1y / v1_length
        v2x, v2y = v2x / v2_length, v2y / v2_length

        # Calculate the bisector vector
        bisector_x = v1x + v2x
        bisector_y = v1y + v2y
        bisector_length = math.sqrt(bisector_x**2 + bisector_y**2)
        bisector_x /= bisector_length
        bisector_y /= bisector_length

        # Calculate the rotation angle of the tangent direction
        rotation_angle = math.atan2(bisector_y, bisector_x)

        return center_pos, rotation_angle + math.pi / 2  # Rotate 90 degrees clockwise

    def is_point_in_flexpath(point, polygons, tolerance):
        """
        Check if a point is within the polygon range of the path, allowing a certain tolerance.

        Input:
            point: tuple, the coordinates of the point to check.
            polygons: list, the polygon set of the path.
            tolerance: float, the tolerance range.

        Output:
            bool, whether the point meets the range condition.
        """
        px, py = point

        # Check if the point is strictly inside the polygon
        for poly in polygons:
            if gdspy.inside([point], [poly], short_circuit=True)[0]:
                return True

            # Check the shortest distance from the point to the polygon boundary
            for i in range(len(poly)):
                x1, y1 = poly[i - 1]
                x2, y2 = poly[i]

                # Calculate the shortest distance from the point to the segment
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

    from addict import Dict
    options = Dict()

    # Create FlexPath and extract polygons
    import gdspy
    path = gdspy.FlexPath(pos, width=width, corners="circular bend", bend_radius=bend_radius)
    polygons = path.to_polygonset().polygons

    # Add air bridges at path corners
    for i in range(1, len(pos) - 1):
        prev_point, curr_point, next_point = pos[i - 1], pos[i], pos[i + 1]

        # Adjust corner position and rotation angle
        adjusted_pos, rotation_angle = adjust_air_bridge_position_for_bend(
            prev_point, curr_point, next_point, bend_radius, width
        )

        # Check if the center point meets the range condition
        if is_point_in_flexpath(adjusted_pos, polygons, width / 2 + 5):  # Add a 5-unit tolerance
            option = Dict(
                name=f"air_bridge_pos_{i}",
                type=air_bridge_type,
                chip=chip_type,
                center_pos=adjusted_pos,
                rotation=rotation_angle
            )
            options[option.name] = option

    # Add air bridges in the middle of the path
    for i in range(len(pos) - 1):
        start, end = pos[i], pos[i + 1]

        # Calculate the length of the segment (considering line width adjustment)
        path_vector = np.array([end[0] - start[0], end[1] - start[1]])
        path_length = np.linalg.norm(path_vector) - bend_radius * 2  # Subtract the rounded corner parts at both ends

        # Calculate the number of air bridges within the effective path length
        if path_length > 0:
            num_bridges = max(1, math.ceil(path_length / spacing))

            for j in range(1, num_bridges + 1):
                # Interpolate to calculate the center position of the air bridge
                t = j / (num_bridges + 1)
                center_x = (1 - t) * start[0] + t * end[0]
                center_y = (1 - t) * start[1] + t * end[1]

                center_pos = (center_x, center_y)

                # Check if the center point meets the range condition
                if is_point_in_flexpath(center_pos, polygons, width / 2 + 5):  # Add a 5-unit tolerance
                    angle = math.atan2(path_vector[1], path_vector[0])

                    option = Dict(
                        name=f"air_bridge_line_{i}_{j}",
                        type=air_bridge_type,
                        chip=chip_type,
                        center_pos=center_pos,
                        rotation=angle
                    )
                    options[option.name] = option

    return options