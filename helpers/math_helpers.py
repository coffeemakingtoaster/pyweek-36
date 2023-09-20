from panda3d.core import Point3, Vec3, CollisionNode, CollisionRay, CollisionHandlerQueue, CollisionEntry

from config import ENTITY_TEAMS

def get_vector_intersection_with_y_coordinate_plane(direction_vector: Vec3 , start_point: Point3, y_coordinate=0):
    factor = ((y_coordinate - start_point.y)/direction_vector.y)
    return Point3(start_point.x + (direction_vector.x * factor), 0, start_point.z + (direction_vector.z * factor))


def get_first_intersection(starting_pos, direction) -> CollisionEntry:
    pq = CollisionHandlerQueue()
    picker_node = CollisionNode('dashray')
    picker_np = render.attach_new_node(picker_node)
    picker_ray = CollisionRay(starting_pos, direction)
    picker_node.add_solid(picker_ray)
    base.cTrav.add_collider(picker_np, pq)
    #picker_np.show()
    base.cTrav.traverse(render)
    base.cTrav.remove_collider(picker_np)
    if len(pq.getEntries()) == 0:
        return None
    pq.sort_entries()
    for entry in pq.getEntries():
        # Dont let player colilision stop player dash
        if entry.into_node.getTag("team") != ENTITY_TEAMS.PLAYER:
            return entry
    picker_np.removeNode()
    return None 