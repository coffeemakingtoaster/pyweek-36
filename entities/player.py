from entities.entity_base import enity_base
from entities.bullet import bullet_entity
from config import GAME_CONSTANTS, ENTITY_TEAMS, PLAYER_ABILITIES
from helpers.model_helpers import load_model
from helpers.utilities import lock_mouse_in_window
from helpers.math_helpers import get_vector_intersection_with_y_coordinate_plane, get_first_intersection

from panda3d.core import lookAt, Quat, Point3, Vec3, Lens, Plane, Point2, CollisionHandlerEvent, CollisionNode, CollisionCapsule, CollisionEntry, BitMask32, CollideMask, LVector3f
import math
from direct.actor.Actor import Actor

class player_entity(enity_base):
    
    def __init__(self):
        
        # TODO: remove the model as the parent of the hitbox. Instead make them siblings. This allows for the visual illusion of a rotating player without actually having to rotate the hitbox
        super().__init__()
        
        self.team = ENTITY_TEAMS.PLAYER
        
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
        
        self.accept("mouse1", self.shoot_bullet)
        self.accept("mouse3", self.dash)
        
        #self.model = load_model("player")
        self.model = Actor("assets/anims/Playertest.egg",{"Dance":"assets/anims/Playertest-Dance.egg"})
        
        self.model.reparentTo(render) 
        
        self.model.setPos(0,0.5,0)
        self.model.loop('Dance')
        self.model.getChild(0).setP(90)
        
        self.current_hp = GAME_CONSTANTS.PLAYER_MAX_HP
        
        self.is_dashing = False 
        
        self.dash_vector = None
        
        self.bullets = []
        
        self.collision = self.model.attachNewNode(CollisionNode("player"))
        
        self.collision.node().addSolid(CollisionCapsule(Point3(0,0,0),(0,5,0),0.9))
        
        self.collision.show()
        
        self.collision.node().setCollideMask(ENTITY_TEAMS.PLAYER_BITMASK)
        
        self.collision.setTag("team", self.team)
        
        self.notifier = CollisionHandlerEvent()

        self.notifier.addInPattern("%fn-into-%in")
        
        self.accept("player-into-bullet", self.bullet_hit)
        
        base.cTrav.addCollider(self.collision, self.notifier)
        
        self.is_dead = False
        
        self.last_position = Point3(0,0.5,0)
        
        self.time_since_last_dash = GAME_CONSTANTS.PLAYER_DASH_COOLDOWN
        
        self.ignore_push = False
        
    def set_movement_status(self, direction):
        self.movement_status[direction] = 1
        
    def unset_movement_status(self, direction):
        self.movement_status[direction] = 0
        
    def on_collision(self, entry=None):
        print(entry)
       
    def update(self, dt):
        
        self.model.node().resetAllPrevTransform()
        
        push_direction = self.last_position - self.model.getPos()
        
        if self.time_since_last_dash < GAME_CONSTANTS.PLAYER_DASH_COOLDOWN:
            self.time_since_last_dash += dt
        
        if self.is_dashing:
            print(self.time_since_last_dash)
            if self.time_since_last_dash > GAME_CONSTANTS.PLAYER_DASH_DURATION:
                self.is_dashing = False
                # Ignore remaining push of dash for movement correction of next frame
                self.ignore_push = True
            else:
                self.model.setFluidPos(self.model.getPos() + (self.dash_vector * ( dt / GAME_CONSTANTS.PLAYER_DASH_DURATION)))
        else:
            movement_direction = Vec3(((self.movement_status["left"] * -1 ) + self.movement_status["right"]) * GAME_CONSTANTS.PLAYER_MOVEMENT_SPEED * dt , 0, ((self.movement_status["down"] ) + self.movement_status["up"]* -1 ) * GAME_CONSTANTS.PLAYER_MOVEMENT_SPEED * dt)
        
            # Last push did not only push back on movement but also did funky stuff
            if not self.ignore_push:
                if push_direction.normalized() != movement_direction.normalized() * -1 and push_direction.length() != 0:
                    movement_direction = movement_direction + (movement_direction.normalized() * push_direction.length()) * -1
        
            self.model.setFluidPos(self.model.getX() + movement_direction.x, 0.5, self.model.getZ() + movement_direction.z)
        
            self.last_position = self.model.getPos()
           
            # Reset ignore push after one normal movement frame
            if self.ignore_push:
                self.ignore_push = False
            
        base.cam.setX(self.model.getX())
        base.cam.setZ(self.model.getZ())
        
        # Rotate mouse to camera
        if base.mouseWatcherNode.hasMouse():
            point = self._get_mouse_position() 
        
            player_pos = self.model.getPos()
            
            delta_to_player = Vec3(player_pos.x - point.x, 0 ,player_pos.z - point.z) 

            mouse_pos_norm = Point2(delta_to_player.x, delta_to_player.z).normalized()

            x = math.degrees(math.atan2(mouse_pos_norm.x, mouse_pos_norm.y))
        
            self.model.setHpr(0,0,-x)
        
        if self.current_hp <= 0:
            messenger.send("goto_main_menu")
        
        for i, bullet in enumerate(self.bullets):
            bullet.update(dt)
            if bullet.is_dead:
                bullet.destroy()
                del self.bullets[i]
        
    def shoot_bullet(self):
        mouse_pos = base.mouseWatcherNode.getMouse()
        nearPoint = Point3()
        base.camLens.extrude(mouse_pos, nearPoint, Point3())
        
        target_point = get_vector_intersection_with_y_coordinate_plane(nearPoint, base.cam.getPos())
        
        player_pos = self.model.getPos()
        delta_to_player = Vec3(target_point.x - player_pos.x, 0 , target_point.z - player_pos.z).normalized()
        
        self.bullets.append(bullet_entity(self.model.getX(), self.model.getZ(), delta_to_player, self.team)) 
    
    def _get_mouse_position(self):
        mouse_pos = base.mouseWatcherNode.getMouse()
        nearPoint = Point3()
        base.camLens.extrude(mouse_pos, nearPoint, Point3())
        
        point = get_vector_intersection_with_y_coordinate_plane(nearPoint, base.cam.getPos())
        return point 
        
    def destroy(self):
        self.model.removeNode()
        for bullet in self.bullets:
            bullet.destroy()
        self.is_dead = True
        self.ignore_all()
        
    def bullet_hit(self, entry: CollisionEntry):
        # No damage taken by own bullets
        if entry.into_node.getTag("team") == self.team:
            return
        # Dashing player does not receive damage 
        if self.is_dashing:
            return
        self.current_hp -= 1
        messenger.send("display_hp", [self.current_hp])
        
    def dash(self):
       current_time = base.clock.getLongTime()
       # Respect the cooldown
       if self.time_since_last_dash >= GAME_CONSTANTS.PLAYER_DASH_COOLDOWN:
           mouse_pos = base.mouseWatcherNode.getMouse()
           nearPoint = Point3()
           base.camLens.extrude(mouse_pos, nearPoint, Point3())
           
           player_pos = self.model.getPos()
        
           target_point = get_vector_intersection_with_y_coordinate_plane(nearPoint, base.cam.getPos())
           
           dash_direction = Vec3(target_point.x - player_pos.x, 0 , target_point.z - player_pos.z)
           
           dash_direction.x = dash_direction.x * -1
           
           dash_range = GAME_CONSTANTS.PLAYER_DASH_DURATION * GAME_CONSTANTS.PLAYER_DASH_SPEED
           
           if (collision := get_first_intersection(self.model.getPos(), dash_direction)) is not None:
               print(collision.getSurfacePoint(render))
               print((collision.getSurfacePoint(render)- self.model.getPos()))
               print((collision.getSurfacePoint(render)- self.model.getPos()).length())
               # If collision is within dash range -> Stop dash at collision
               # Shorten slightly to stop BEFORE hitting the object
               dash_range = min((collision.getSurfacePoint(render) - self.model.getPos()).length() - 0.25, dash_range)
               
               print(dash_range)
               
           self.dash_vector = dash_direction.normalized() * dash_range 
            
           # Display cd in HUD 
           messenger.send("set_ability_on_cooldown", [PLAYER_ABILITIES.DASH, current_time + GAME_CONSTANTS.PLAYER_DASH_COOLDOWN])
          
           self.is_dashing = True
           self.time_since_last_dash = 0
           
    def on_wall_collision(self, entry: CollisionEntry):
        print("collide with wall")
        # Stop dash when colliding with an object
        if entry.into_node.getTag("team") == ENTITY_TEAMS.MAP:
            self.is_dashing = False