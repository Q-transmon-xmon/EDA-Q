
##########################################################################################
# Methods related to generating air bridges
##########################################################################################

def add_air_bridges(pos, bend_radius, spacing=120, chip_name="chip3"):
    from addict import Dict
    import math
    def adjust_air_bridge_position_for_bend(prev_point, curr_point, next_point, bend_radius):
        """
        Optimize the position of the air bridge to make it precisely contact with the rounded path and dynamically adjust the offset correction factor.

        Input:
            prev_point: tuple, the coordinates of the previous point (x, y).
            curr_point: tuple, the coordinates of the current point (x, y).
            next_point: tuple, the coordinates of the next point (x, y).
            bend_radius: float, the radius of the rounded corner.

        Output:
            adjusted_pos: tuple, the adjusted position coordinates of the air bridge (x, y).
            rotation_angle: float, the rotation angle of the air bridge's tangent direction (in radians, rotated 90 degrees clockwise).
        """
        # 1. **Vector Calculation**
        v1x, v1y = prev_point[0] - curr_point[0], prev_point[1] - curr_point[1]
        v2x, v2y = next_point[0] - curr_point[0], next_point[1] - curr_point[1]

        # 2. **Normalize Vectors**
        v1_length = math.sqrt(v1x**2 + v1y**2)
        v2_length = math.sqrt(v2x**2 + v2y**2)
        v1x, v1y = v1x / v1_length, v1y / v1_length
        v2x, v2y = v2x / v2_length, v2y / v2_length

        # 3. **Calculate the Cosine and Sine of the Angle Between Vectors**
        dot_product = v1x * v2x + v1y * v2y  # Dot product of the two vectors
        angle_cos = dot_product  # Cosine of the angle between the vectors cos(θ)
        angle = math.acos(angle_cos)  # The angle in radians θ

        # 4. **Dynamic Adjustment of Correction Factor**
        deviation_from_right = abs(angle - math.pi / 2)  # Absolute deviation from the right angle
        if angle > math.pi / 2:  # When the angle is obtuse
            offset_factor = 0.4 - 0.5 * (deviation_from_right / (math.pi / 2))
        else:  # When the angle is acute
            offset_factor = 0.4 + 0.8 * (deviation_from_right / (math.pi / 2))

        # 5. **Calculate the Angle Bisector Vector**
        bisector_x = v1x + v2x
        bisector_y = v1y + v2y
        bisector_length = math.sqrt(bisector_x**2 + bisector_y**2)
        bisector_x /= bisector_length  # Normalize the angle bisector vector
        bisector_y /= bisector_length

        # 6. **Calculate the Offset**
        offset_x = bisector_x * (bend_radius / math.sqrt(1 - angle_cos**2)) * offset_factor
        offset_y = bisector_y * (bend_radius / math.sqrt(1 - angle_cos**2)) * offset_factor

        # 7. **Adjusted Position**
        adjusted_x = curr_point[0] + offset_x
        adjusted_y = curr_point[1] + offset_y

        # 8. **Calculate the Rotation Angle of the Tangent Direction**
        rotation_angle = math.atan2(bisector_y, bisector_x)

        return (adjusted_x, adjusted_y), rotation_angle + math.pi / 2  # Rotated 90 degrees clockwise

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
    print("The number of generated air bridges is:{}".format(len(options)))
    return options
    

def add_air_bridges2(pos, bend_radius, spacing=120, chip_type="chip3", width=10, air_bridge_type="AirBridge"):
    """
    Add air bridges to ensure that the center points meet the distance or area conditions relative to the FlexPath polygons.
    """
    import numpy as np
    import math
    
    def find_nearest_segment_center(polygons, curr_point, line_width):
        """
        Find the center of the path segment closest to the given point curr_point, and adjust the center position according to the line width.

        Input:
            polygons: list, a list of polygons that make up the path, where each polygon is a 2D array of points.
            curr_point: tuple, the coordinates (x, y) of the current point used to calculate the nearest segment.
            line_width: float, the width of the path segment, used to adjust the offset of the center position.

        Output:
            nearest_center: tuple, the coordinates (x, y) of the center of the segment closest to curr_point after adjustment.
        """
        # Concatenate multiple polygon point sets into a continuous path point array
        path_points = np.concatenate(polygons)
        curr_x, curr_y = curr_point  # The x and y coordinates of the current point

        # Initialize the minimum distance and the nearest center point
        min_distance = float('inf')  # Initial minimum distance is positive infinity
        nearest_center = None        # Initial nearest center point is None

        # Iterate over each segment of the path
        for i in range(len(path_points) - 1):
            # Get the two endpoints of the current segment
            x1, y1 = path_points[i]
            x2, y2 = path_points[i + 1]

            # Calculate the direction vector and length of the segment
            dx, dy = x2 - x1, y2 - y1  # Direction vector of the segment
            length = math.sqrt(dx**2 + dy**2)  # Length of the segment

            # Calculate the unit direction vector
            direction_x = dx / length
            direction_y = dy / length

            # Calculate the orthogonal direction vector (normal vector, used to calculate the line width offset)
            normal_x = -direction_y
            normal_y = direction_x

            # Calculate the center of the segment
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2

            # Adjust the position of the segment center according to the line width
            adjusted_center_x = center_x + normal_x * (line_width / 2)
            adjusted_center_y = center_y + normal_y * (line_width / 2)

            # Calculate the distance from the adjusted center to the current point curr_point
            distance = np.sqrt((adjusted_center_x - curr_x)**2 + (adjusted_center_y - curr_y)**2)

            # If the current distance is less than the previous minimum distance, update the nearest center point and minimum distance
            if distance < min_distance:
                min_distance = distance
                nearest_center = (adjusted_center_x, adjusted_center_y)

        # Return the nearest segment center after adjustment
        return nearest_center

    # ... (rest of the function remains the same, including the other helper functions and the main logic for adding air bridges)



    def adjust_air_bridge_position_for_bend(prev_point, curr_point, next_point, bend_radius, width):
        """
        Optimize the offset of the air bridge, accurately calculate the contact point between the rounded path and the air bridge, and dynamically adjust the rotation angle of the air bridge.

        Input:
            prev_point: tuple, the coordinates (x, y) of the previous point on the path.
            curr_point: tuple, the coordinates (x, y) of the current point on the path, which is the point where the air bridge position needs to be adjusted.
            next_point: tuple, the coordinates (x, y) of the next point on the path.
            bend_radius: float, the radius of the rounded corner of the path.
            width: float, the width of the path (used to determine the geometric shape of the path).

        Output:
            center_pos: tuple, the adjusted center position of the air bridge, in the form of (x, y).
            rotation_angle: float, the rotation angle of the air bridge (in radians, rotated 90 degrees clockwise).

        Functions:
            1. Use `gdspy.FlexPath` to create a path based on the rounded corner.
            2. Extract the polygon representation of the path and calculate the center of the path segment closest to the current point.
            3. Calculate the bisector direction and rotation angle of the air bridge based on the path direction.
        """

        # Create a set of points for the path
        path_points = [prev_point, curr_point, next_point]

        # Use gdspy to create a FlexPath based on the rounded corner
        path = gdspy.FlexPath(
            path_points,
            width=width,               # Path width
            corners="circular bend",   # Corner type
            bend_radius=bend_radius    # Corner radius
        )

        # Extract the polygon representation of the path (set of points)
        polygons = path.to_polygonset().polygons  # Extract the set of points for the polygons
        # Calculate the center of the path segment closest to the current point
        center_pos = find_nearest_segment_center(polygons, curr_point, width)

        # 1. **Vector Calculation**
        # Vector from the current point to the previous point
        v1x, v1y = prev_point[0] - curr_point[0], prev_point[1] - curr_point[1]
        # Vector from the current point to the next point
        v2x, v2y = next_point[0] - curr_point[0], next_point[1] - curr_point[1]

        # 2. **Normalize Vectors**
        v1_length = math.sqrt(v1x**2 + v1y**2)  # Calculate the length of vector 1
        v2_length = math.sqrt(v2x**2 + v2y**2)  # Calculate the length of vector 2
        v1x, v1y = v1x / v1_length, v1y / v1_length  # Normalize vector 1
        v2x, v2y = v2x / v2_length, v2y / v2_length  # Normalize vector 2

        # 3. **Calculate the Bisector Vector**
        # The bisector vector is the sum of the two vectors
        bisector_x = v1x + v2x
        bisector_y = v1y + v2y
        bisector_length = math.sqrt(bisector_x**2 + bisector_y**2)  # Length of the bisector
        bisector_x /= bisector_length  # Normalize the bisector vector
        bisector_y /= bisector_length

        # 4. **Calculate the Rotation Angle of the Tangent Direction**
        # The rotation angle of the tangent direction
        rotation_angle = math.atan2(bisector_y, bisector_x)

        # Return the adjusted center position and rotation angle of the air bridge
        return center_pos, rotation_angle + math.pi / 2  # Rotated 90 degrees clockwise


    def is_point_in_flexpath(point, polygons, tolerance):
        """
        Check if a given point is within the polygon range of the path, allowing a certain tolerance distance.

        Input:
            point: tuple, the coordinates (x, y) of the point to check.
            polygons: list, a list of point sets for the polygons, where each polygon is a 2D array.
            tolerance: float, the tolerance distance, the maximum distance allowed between the point and the polygon boundary.

        Output:
            bool: If the point is within the polygon range or within the tolerance range, return True; otherwise, return False.

        Functions:
            1. Check if the point is strictly within the polygon.
            2. If not inside the polygon, further check if the shortest distance from the point to the polygon boundary is less than or equal to the tolerance.
        """
        px, py = point  # Extract the x and y coordinates of the point

        # 1. **Check if the point is strictly inside the polygon**
        for poly in polygons:
            # Use the gdspy.inside function to check if the point is inside the current polygon
            if gdspy.inside([point], [poly], short_circuit=True)[0]:
                return True

            # 2. **Check the shortest distance from the point to the polygon boundary**
            for i in range(len(poly)):
                # Get two adjacent points on the polygon boundary
                x1, y1 = poly[i - 1]  # The previous vertex
                x2, y2 = poly[i]      # The current vertex

                # Calculate the direction vector of the line segment
                dx, dy = x2 - x1, y2 - y1
                length_squared = dx**2 + dy**2  # The square of the line segment length

                # If the line segment length is 0 (degenerate to a point)
                if length_squared == 0:
                    # Directly calculate the distance from the point to the vertex
                    distance = math.sqrt((px - x1)**2 + (py - y1)**2)
                else:
                    # Calculate the projection ratio t of the point onto the line segment, limited to the range [0, 1]
                    t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / length_squared))
                    # Calculate the coordinates of the projection point
                    proj_x = x1 + t * dx
                    proj_y = y1 + t * dy
                    # Calculate the distance from the point to the projection point
                    distance = math.sqrt((px - proj_x)**2 + (py - proj_y)**2)

                # If the shortest distance from the point to the boundary is less than or equal to the tolerance, return True
                if distance <= tolerance:
                    return True

        # If after iterating through all polygons and boundaries no conditions are met, return False
        return False
    
    from addict import Dict
    options = Dict()

    # create FlexPath And extract polygons
    import gdspy
    path = gdspy.FlexPath(pos, width=width, corners="circular bend", bend_radius=bend_radius)
    polygons = path.to_polygonset().polygons

    # Add air bridge at the corner of the path
    for i in range(1, len(pos) - 1):
        prev_point, curr_point, next_point = pos[i - 1], pos[i], pos[i + 1]

        # Adjust the corner position and rotation angle
        adjusted_pos, rotation_angle = adjust_air_bridge_position_for_bend(
            prev_point, curr_point, next_point, bend_radius, width
        )

        # Check if the center point meets the range conditions
        if is_point_in_flexpath(adjusted_pos, polygons, width / 2 + 5):  # increase5Unit tolerance
            option = Dict(
                name=f"air_bridge_pos_{i}",
                type=air_bridge_type,
                chip=chip_type,
                center_pos=adjusted_pos,
                rotation=rotation_angle
            )
            options[option.name] = option

    # Add air bridge in the middle of the path
    for i in range(len(pos) - 1):
        start, end = pos[i], pos[i + 1]

        # Calculate segment length(Consider adjusting the line width)
        path_vector = np.array([end[0] - start[0], end[1] - start[1]])
        path_length = np.linalg.norm(path_vector) - bend_radius * 2  # Subtract the rounded corners at both ends

        # Calculate the number of air bridges within the effective path length
        if path_length > 0:
            num_bridges = max(1, math.ceil(path_length / spacing))

            for j in range(1, num_bridges + 1):
                # Interpolation calculation of the center position of the air bridge
                t = j / (num_bridges + 1)
                center_x = (1 - t) * start[0] + t * end[0]
                center_y = (1 - t) * start[1] + t * end[1]

                center_pos = (center_x, center_y)

                # Check if the center point meets the range conditions
                if is_point_in_flexpath(center_pos, polygons, width / 2 + 5):  # increase5Unit tolerance
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

def add_air_bridges3(pos, bend_radius, spacing=120, chip_type="chip3", width=10, air_bridge_type="AirbriageNb"):
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
        Search for distance curr_point The center point of the nearest line segment，And adjust the center position according to the line width。
        """
        path_points = np.concatenate(polygons)  # Expand the polygon point set into continuous path points
        curr_x, curr_y = curr_point

        # Initialize minimum distance and nearest center point
        min_distance = float('inf')
        nearest_center = None

        # Traverse each segment of the path
        for i in range(len(path_points) - 1):
            # Calculate the endpoints of the line segment
            x1, y1 = path_points[i]
            x2, y2 = path_points[i + 1]

            # Calculate the direction vector and length of the line segment
            dx, dy = x2 - x1, y2 - y1
            length = math.sqrt(dx**2 + dy**2)

            # Unit directional vector
            direction_x = dx / length
            direction_y = dy / length

            # Orthogonal directional vector（Normal vector）
            normal_x = -direction_y
            normal_y = direction_x

            # Calculate the center point of the line segment
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2

            # Adjust the center point according to the line width
            adjusted_center_x = center_x + normal_x * (line_width / 2)
            adjusted_center_y = center_y + normal_y * (line_width / 2)

            # Calculate the adjusted center point to curr_point The distance
            distance = np.sqrt((adjusted_center_x - curr_x)**2 + (adjusted_center_y - curr_y)**2)

            # Update the nearest center point
            if distance < min_distance:
                min_distance = distance
                nearest_center = (adjusted_center_x, adjusted_center_y)

        return nearest_center



    def adjust_air_bridge_position_for_bend(prev_point, curr_point, next_point, bend_radius,width):
        """
        Optimize the offset of the air bridge，Accurately calculate the contact points between rounded corners and paths，Dynamic adjustment correction factor。
        """

        path_points = [prev_point, curr_point, next_point]
        path = gdspy.FlexPath(
            path_points,
            width=width,
            corners="circular bend",
            bend_radius=bend_radius
        )
        polygons = path.to_polygonset().polygons  # Extract polygon point set
        gds_pos = find_nearest_segment_center(polygons,curr_point,width)

        # Vector computation
        v1x, v1y = prev_point[0] - curr_point[0], prev_point[1] - curr_point[1]
        v2x, v2y = next_point[0] - curr_point[0], next_point[1] - curr_point[1]

        # normalized vector
        v1_length = math.sqrt(v1x**2 + v1y**2)
        v2_length = math.sqrt(v2x**2 + v2y**2)
        v1x, v1y = v1x / v1_length, v1y / v1_length
        v2x, v2y = v2x / v2_length, v2y / v2_length


        # Calculate the vector of the angle bisector
        bisector_x = v1x + v2x
        bisector_y = v1y + v2y
        bisector_length = math.sqrt(bisector_x**2 + bisector_y**2)
        bisector_x /= bisector_length
        bisector_y /= bisector_length

        # Calculate the rotation angle in the tangent direction
        rotation_angle = math.atan2(bisector_y, bisector_x)

        return gds_pos, rotation_angle + math.pi / 2  # clockwise rotation90linear measure


    def is_point_in_flexpath(point, polygons, tolerance):
        """
        Check if the checkpoint is within the polygon range of the path，And allow for a certain tolerance。
        """
        px, py = point

        # Determine whether the point is within the polygon（stringent condition）
        for poly in polygons:
            if gdspy.inside([point], [poly], short_circuit=True)[0]:
                return True

            # Determine the shortest distance from a point to the polygon boundary
            for i in range(len(poly)):
                x1, y1 = poly[i - 1]
                x2, y2 = poly[i]

                # Calculate the shortest distance from a point to a line segment
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
    
    options = Dict()

    # create FlexPath And extract polygons
    path = gdspy.FlexPath(pos, width=width, corners="circular bend", bend_radius=bend_radius)
    polygons = path.to_polygonset().polygons


    # Add air bridge in the middle of the path
    for i in range(len(pos) - 1):
        start, end = pos[i], pos[i + 1]

        # Calculate segment length（Consider adjusting the line width）
        path_vector = np.array([end[0] - start[0], end[1] - start[1]])
        path_length = np.linalg.norm(path_vector) - bend_radius * 2  # Subtract the rounded corners at both ends

        # Calculate the number of air bridges within the effective path length
        if path_length > 0:
            num_bridges = max(1, math.ceil(path_length / spacing))

            for j in range(1, num_bridges + 1):
                # Interpolation calculation of the center position of the air bridge
                t = j / (num_bridges + 1)
                center_x = (1 - t) * start[0] + t * end[0]
                center_y = (1 - t) * start[1] + t * end[1]

                gds_pos = (center_x, center_y)

                # Check if the center point meets the range conditions
                if is_point_in_flexpath(gds_pos, polygons, width / 2 + 5):  # increase5Unit tolerance
                    angle = math.atan2(path_vector[1], path_vector[0])

                    option = Dict(
                        name=f"air_bridge_line_{i}_{j}",
                        type=air_bridge_type,
                        chip=chip_type,
                        gds_pos=gds_pos,
                        rotation=angle
                    )
                    options[option.name] = option
    # Add air bridge at the corner of the path
    for i in range(1, len(pos) - 1):
        prev_point, curr_point, next_point = pos[i - 1], pos[i], pos[i + 1]

        # Adjust the corner position and rotation angle
        adjusted_pos, rotation_angle = adjust_air_bridge_position_for_bend(
            prev_point, curr_point, next_point, bend_radius, width
        )

        # Check if the center point meets the range conditions
        if is_point_in_flexpath(adjusted_pos, polygons, width / 2 + 5):  # increase5Unit tolerance
            option = Dict(
                name=f"air_bridge_pos_{i}",
                type=air_bridge_type,
                chip=chip_type,
                gds_pos=adjusted_pos,
                rotation=rotation_angle
            )
            options[option.name] = option
    return options