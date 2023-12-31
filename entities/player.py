from entities.entity_base import enity_base
from entities.bullet import bullet_entity
from entities.black_hole import black_hole_entity
from config import GAME_CONSTANTS, ENTITY_TEAMS, PLAYER_ABILITIES
from helpers.model_helpers import load_particles 
from helpers.utilities import lock_mouse_in_window
from helpers.math_helpers import get_vector_intersection_with_y_coordinate_plane, get_first_intersection

from panda3d.core import *
import math
from direct.actor.Actor import Actor
from os.path import join

class player_entity(enity_base):
    
    def __init__(self):
        
        # TODO: remove the model as the parent of the hitbox. Instead make them siblings. This allows for the visual illusion of a rotating player without actually having to rotate the hitbox
        super().__init__()
        
        self.team = ENTITY_TEAMS.PLAYER
        self.moveSpeed = GAME_CONSTANTS.PLAYER_MOVEMENT_SPEED
        
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
        self.accept("q", self.cast_black_hole) 
        self.plnp = None
        
        self.id =  "player"
        self.model = Actor("assets/anims/Player.egg",{"Idle":"assets/anims/Player-Idle.egg"})
        
        self.model.reparentTo(render)
        
        plight = PointLight('plight')
        plight.setColor((-1, -1, -1, 1))
        self.plnp = self.model.attachNewNode(plight)
        plight.attenuation = (1, 0, 0.1)
        self.plnp.setPos(0, 0, 0)
        render.setLight(self.plnp)
        
        self.model.setPos(0,2,0)
        #self.model.setHpr(0, 90, 180)
        self.model.loop('Idle')
        self.model.getChild(0).setP(90)
        self.model.getChild(0).setR(180)
        
        self.current_hp = GAME_CONSTANTS.PLAYER_MAX_HP
        
        self.is_dashing = False 
        
        self.dash_vector = None
        
        self.bullets = []
        
        self.collision = self.model.attachNewNode(CollisionNode("player"))
        
        self.collision.node().addSolid(CollisionCapsule(Point3(0,-2,0),(0,2,0),0.9))
        
        #self.collision.show()
        
        self.collision.node().setCollideMask(ENTITY_TEAMS.PLAYER_BITMASK)
        
        self.collision.setTag("team", self.team)
        self.collision.setTag("id", self.id)
              
        self.ability_collision = self.model.attachNewNode(CollisionNode("player_melee_attack_hitbox"))
        
        self.ability_collision.node().addSolid(CollisionSphere(0,0,0,0.9))
        
        self.ability_collision.node().setCollideMask(ENTITY_TEAMS.MELEE_ATTACK_BITMASK)
        
        self.ability_collision.setTag("team", self.team)
        
        self.notifier = CollisionHandlerEvent()

        self.notifier.addInPattern("%fn-into-%in")
        
        self.accept("bullet-into", self.bullet_hit, [True])
        
        self.accept("attack-into-player_melee_attack_hitbox", self.bullet_hit, [False])
        
        base.cTrav.addCollider(self.ability_collision, self.notifier) 
        base.cTrav.addCollider(self.collision, self.notifier)
        
        self.is_dead = False
        
        self.last_position = Point3(0,2,0)
        
        self.time_since_last_dash = GAME_CONSTANTS.PLAYER_DASH_COOLDOWN
        self.time_since_last_black_hole = GAME_CONSTANTS.BLACK_HOLE_COOLDOWN
        
        self.ignore_push = False
        
        self.dash_particles = load_particles("smoke")
        
        self.dash_sfx = base.loader.loadSfx(join("assets", "sfx", "player_dash.wav"))
        
        self.shoot_sfx = base.loader.loadSfx(join("assets", "sfx", "player_shoot.wav"))
        
        self.damage_sfx = base.loader.loadSfx(join("assets", "sfx", "player_damage.wav"))
        
        self.attack_cooldown = GAME_CONSTANTS.PLAYER_SHOOT_SPEED
        
        self.last_shoot_time = base.clock.getLongTime() 
        
    def set_movement_status(self, direction):
        self.movement_status[direction] = 1
        
    def unset_movement_status(self, direction):
        self.movement_status[direction] = 0
    
    def update(self, dt):
        
        self.model.node().resetAllPrevTransform()
        
        push_direction = self.last_position - self.model.getPos()
        
        if self.time_since_last_dash < GAME_CONSTANTS.PLAYER_DASH_COOLDOWN:
            self.time_since_last_dash += dt
            
        if self.time_since_last_black_hole < GAME_CONSTANTS.BLACK_HOLE_COOLDOWN:
            self.time_since_last_black_hole += dt
        
        if self.is_dashing:
            if self.time_since_last_dash > GAME_CONSTANTS.PLAYER_DASH_DURATION:
                self.is_dashing = False
                self.dash_particles.cleanup()
                # Ignore remaining push of dash for movement correction of next frame
                self.ignore_push = True
            else:
                self.model.setFluidPos(self.model.getPos() + (self.dash_vector * ( dt / GAME_CONSTANTS.PLAYER_DASH_DURATION)))
        else:
            movement_direction = Vec3(((self.movement_status["left"] * -1 ) + self.movement_status["right"]) * self.moveSpeed * dt , 0, ((self.movement_status["down"] ) + self.movement_status["up"]* -1 ) * self.moveSpeed * dt)
        
            # Last push did not only push back on movement but also did funky stuff
            if not self.ignore_push:
                if push_direction.normalized() != movement_direction.normalized() * -1 and push_direction.length() != 0:
                    movement_direction = movement_direction + (movement_direction.normalized() * push_direction.length()) * -1
        
            self.model.setFluidPos(self.model.getX() + movement_direction.x, 2, self.model.getZ() + movement_direction.z)
        
            self.last_position = self.model.getPos()
           
            # Reset ignore push after one normal movement frame
            if self.ignore_push:
                self.ignore_push = False
            
        base.cam.setX(self.model.getX())
        base.cam.setZ(self.model.getZ()+40)
        
        # Rotate mouse to camera
        if base.mouseWatcherNode.hasMouse():
            point = self._get_mouse_position() 
        
            player_pos = self.model.getPos()
            
            delta_to_player = Vec3(player_pos.x - point.x, 0 ,player_pos.z - point.z) 

            mouse_pos_norm = Point2(delta_to_player.x, delta_to_player.z).normalized()

            x = math.degrees(math.atan2(mouse_pos_norm.x, mouse_pos_norm.y))
        
            self.model.setR(x)
        
        if self.current_hp <= 0:
            self.is_dead = True
        
        for i, bullet in enumerate(self.bullets):
            bullet.update(dt)
            if bullet.is_dead:
                bullet.destroy()
                del self.bullets[i]
        
    def shoot_bullet(self):
        current_time = base.clock.getLongTime()
        if current_time - self.last_shoot_time < self.attack_cooldown: 
            return
        self.shoot_sfx.play()
        target_point = self._get_mouse_position() 
        player_pos = self.model.getPos()
        delta_to_player = Vec3(target_point.x - player_pos.x, 0 , target_point.z - player_pos.z).normalized()
        self.bullets.append(bullet_entity(self.model.getX(), self.model.getZ(), delta_to_player, self.team)) 
        self.last_shoot_time = current_time
    
    def _get_mouse_position(self):
        mouse_pos = base.mouseWatcherNode.getMouse()
        nearPoint = Point3()
        farPoint = Point3()
        base.camLens.extrude(mouse_pos, nearPoint, farPoint)
       
        # Rotate the extruded vector based on the rotation of the camera 
        quat = Quat()
        
        quat.setHpr(base.cam.getHpr())
        
        nearPoint = quat.xform(nearPoint)
        
        point = get_vector_intersection_with_y_coordinate_plane(nearPoint, base.cam.getPos())
        return point 
        
    def destroy(self):
        self.model.removeNode()
        for bullet in self.bullets:
            bullet.destroy()
        self.is_dead = True
        self.ignore_all()
        render.clearLight(self.plnp)
        
    def bullet_hit(self, attack_was_ranged: bool,  entry: CollisionEntry):
        # Dashing player does not receive damage 
        if self.is_dashing:
            return
       
        # print(entry.into_node.getTag("team")) 
        # Only take damage from bullets meant for my own team
        if entry.into_node.getTag("team") != self.team:
            return
        
        if entry.into_node.getTag("id") != self.id and attack_was_ranged:
            return
        
        self.damage_sfx.play()
        
        self.current_hp -= 1
        messenger.send("display_hp", [self.current_hp])
        messenger.send("player-got-hit")
        
    def dash(self):
       current_time = base.clock.getLongTime()
       # Respect the cooldown
       if self.time_since_last_dash >= GAME_CONSTANTS.PLAYER_DASH_COOLDOWN:
           target_point = self._get_mouse_position() 
           
           player_pos = self.model.getPos()
           
           dash_direction = Vec3(target_point.x - player_pos.x, 0 , target_point.z - player_pos.z)
           
           dash_range = GAME_CONSTANTS.PLAYER_DASH_DURATION * GAME_CONSTANTS.PLAYER_DASH_SPEED
           
           if (collision := get_first_intersection(self.model.getPos(), dash_direction)) is not None:
               #print(collision.getSurfacePoint(render))
               #print((collision.getSurfacePoint(render)- self.model.getPos()))
               #print((collision.getSurfacePoint(render)- self.model.getPos()).length())
               # If collision is within dash range -> Stop dash at collision
               # Shorten slightly to stop BEFORE hitting the object
               dash_range = min((collision.getSurfacePoint(render) - self.model.getPos()).length() - 0.5, dash_range)
               
           self.dash_vector = dash_direction.normalized() * dash_range 
            
           # Display cd in HUD 
           messenger.send("set_ability_on_cooldown", [PLAYER_ABILITIES.DASH, current_time + GAME_CONSTANTS.PLAYER_DASH_COOLDOWN])
            
           self.dash_particles = load_particles("smoke") 
           self.dash_particles.start(self.model, renderParent=render)
          
           self.is_dashing = True
           self.time_since_last_dash = 0
           self.dash_sfx.play()
           
    def on_wall_collision(self, entry: CollisionEntry):
        # Stop dash when colliding with an object
        if entry.into_node.getTag("team") == ENTITY_TEAMS.MAP:
            self.is_dashing = False
            
    def cast_black_hole(self):
        current_time = base.clock.getLongTime()
        
        if self.time_since_last_black_hole >= GAME_CONSTANTS.BLACK_HOLE_COOLDOWN:
            mouse_pos = self._get_mouse_position()
            #print("Spawning black hole")
            
            messenger.send("spawn_black_hole", [mouse_pos])
            
            messenger.send("set_ability_on_cooldown", [PLAYER_ABILITIES.BLACK_HOLE, current_time + GAME_CONSTANTS.BLACK_HOLE_COOLDOWN]) 
            
            black_hole_entity(mouse_pos)
           
            self.time_since_last_black_hole = 0
            
    def heal(self):
        self.current_hp +=1
        messenger.send("display_hp", [self.current_hp]) 
            
    def upGradeSpeed(self):
        self.moveSpeed += 5
            