from panda3d.core import Point3, Vec3

def get_vector_intersection_with_y_coordinate_plane(direction_vector: Vec3 , start_point: Point3, y_coordinate=0):
    factor = ((y_coordinate - start_point.y)/direction_vector.y)
    return Point3(start_point.x + (direction_vector.x * factor), 0, start_point.z + (direction_vector.z * factor))