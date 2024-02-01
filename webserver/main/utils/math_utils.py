import math


def create_simple_circle_polygon(latitude, longitude, radius_in_km, num_points=24):
    polygon = []
    radius_in_meters = radius_in_km*1000

    for i in range(num_points):
        angle = 2 * math.pi * i / num_points
        dx = radius_in_meters * math.cos(angle)
        dy = radius_in_meters * math.sin(angle)

        # Convert meters to degrees (approximately, considering latitude)
        dx_deg = dx / (111320 * math.cos(latitude))
        dy_deg = dy / 110540

        # Add point to the polygon
        polygon.append([latitude + dx_deg, longitude + dy_deg])

    polygon.append(polygon[0])
    return polygon
