from entities.entity_base import enity_base

from panda3d.core import Vec3, Point2, CollisionNode, CollisionSphere, CollisionHandlerEvent, CollisionEntry

import math
import uuid

from helpers.model_helpers import load_model

from config import GAME_CONSTANTS, ENTITY_TEAMS

class base_enemy(enity_base):
    
    def __init__(self, spawn_x, spawn_z):
        super().__init__()
        
        self.team = ENTITY_TEAMS.ENEMIES 
        
        self.speed = 5

        self.model = load_model("player")
        
        self.model.reparentTo(render)
        
        self.model.setPos(spawn_x,0,spawn_z)
        
        self.current_hp = GAME_CONSTANTS.SAMPLE_ENEMY_MAX_HP
        
        self.id = str(uuid.uuid4())
        
        self.collision = self.model.attachNewNode(CollisionNode("enemy"))
        
        self.collision.node().addSolid(CollisionSphere(0,0,0,0.9))
        
        self.collision.show()
        
        self.collision.setTag("team", self.team)
        self.collision.setTag("id", self.id)
        
        self.notifier = CollisionHandlerEvent()

        self.notifier.addInPattern("%fn-into-%in")
        
        self.accept("enemy-into-bullet", self.bullet_hit)
        
        base.cTrav.addCollider(self.collision, self.notifier)
        
        self.is_dead = False
        
        
    def update(self, dt, player_pos):
        
        entity_pos = self.model.getPos()
        
        delta_to_player = Vec3(entity_pos.x - player_pos.x, 0 , entity_pos.z - player_pos.z) 

        diff_to_player_normalized = Point2(delta_to_player.x, delta_to_player.z)

        x = math.degrees(math.atan2(diff_to_player_normalized.x, diff_to_player_normalized.y))
        
        x_direction = diff_to_player_normalized[0] * self.speed * dt
        z_direction = diff_to_player_normalized[1] * self.speed * dt
        
        
        self.model.setX(self.model.getX() - x_direction)
        self.model.setZ(self.model.getZ() - z_direction)

        self.model.setR(x)
        
    def destroy(self):
        self.model.removeNode()
        self.collision.removeNode()
        self.ignore_all()
       
    # collisionentry is not needed -> we ignore it 
    def bullet_hit(self, entry: CollisionEntry):
        # Ignore collisions triggered by other enemies
        if entry.from_node.getTag("id") != self.id:
            return
        # No damage take by allied or own bullets
        if entry.into_node.getTag("team") == self.team:
            return
        
        self.takeDamage(1)
        
    def takeDamage(self,dmg):
        self.current_hp -=dmg
        print("Taking damage")
        if self.current_hp <= 0:
            self.is_dead = True