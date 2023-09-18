from entities.entity_base import enity_base
from config import GAME_CONSTANTS 
from helpers.model_helpers import load_model
from helpers.utilities import lock_mouse_in_window
from helpers.math_helpers import get_vector_intersection_with_y_coordinate_plane 

from panda3d.core import lookAt, Quat, Point3, Vec3, Lens, Plane, Point2
import math

class player_entity(enity_base):
    
    def __init__(self):
        super().__init__()
        
        self.movement_status = {"up":0, "down":0, "left": 0, "right": 0}
        
        # Keybinds for movement
        self.accept("a",self.set_movement_status, ["left"])
        self.accept("a-up", self.unset_movement_status, ["left"])
        self.accept("d",self.set_movement_status, ["right"])
        self.accept("d-up", self.unset_movement_status, ["right"])
        self.accept("w",self.set_movement_status, ["up"])
        self.accept("w-up", self.unset_movement_status, ["up"])
        self.accept("s",self.set_movement_status, ["down"])
        self.accept("s-up", self.unset_movement_status, ["down"])
        
        
        # For testing
        self.accept("space", self.take_damage) 
        
        self.model = load_model("player")
        
        self.model.reparentTo(render)
        
        self.model.setPos(0,0,0)
        
        self.current_hp = GAME_CONSTANTS.PLAYER_MAX_HP
        
    def set_movement_status(self, direction):
        self.movement_status[direction] = 1
        
    def unset_movement_status(self, direction):
        self.movement_status[direction] = 0
       
    def update(self, dt):
        x_direction = ((self.movement_status["left"] * -1 ) + self.movement_status["right"]) * GAME_CONSTANTS.PLAYER_MOVEMENT_SPEED * dt
        z_direction = ((self.movement_status["down"] ) + self.movement_status["up"]* -1 ) * GAME_CONSTANTS.PLAYER_MOVEMENT_SPEED * dt
        
        self.model.setX(self.model.getX() + x_direction)
        self.model.setZ(self.model.getZ() + z_direction)
        
        base.cam.setX(self.model.getX())
        base.cam.setZ(self.model.getZ())
        
        # Rotate mouse to camera
        mouse_pos = base.mouseWatcherNode.getMouse()
        nearPoint = Point3()
        base.camLens.extrude(mouse_pos, nearPoint, Point3())
        
        point = get_vector_intersection_with_y_coordinate_plane(nearPoint, base.cam.getPos())
        
        player_pos = self.model.getPos()
        delta_to_player = Vec3(player_pos.x - point.x, 0 ,player_pos.z - point.z) 

        mouse_pos_norm = Point2(delta_to_player.x, delta_to_player.z).normalized()

        x = math.degrees(math.atan2(mouse_pos_norm.x, mouse_pos_norm.y))
        
        self.model.setHpr(0,0,-x)
        
        if self.current_hp <= 0:
            print("Man im dead")
            messenger.send("goto_main_menu")
        
    def take_damage(self):
        self.current_hp -= 1
        messenger.send("display_hp", [self.current_hp])
        
    def destroy(self):
        self.model.removeNode()
        
        
        

         