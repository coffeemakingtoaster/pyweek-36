from entities.base_enemy import base_enemy
from entities.entity_base import enity_base

from panda3d.core import Vec3, Point2, CollisionNode, CollisionSphere, CollisionHandlerEvent, CollisionEntry, CollisionBox, Point3
from direct.task.Task import Task

import math
import uuid

from helpers.model_helpers import load_model

from config import GAME_CONSTANTS, ENTITY_TEAMS
import time
from direct.actor.Actor import Actor
from config import MAP_CONSTANTS

from os.path import join


class melee_enemy(base_enemy):
    
    def __init__(self, spawn_x, spawn_z,roomSize,roomZero):
        super().__init__(spawn_x,spawn_z,roomSize,roomZero)
        self.speed = 8
        self.attackcooldown = 3
        self.attack_sound = base.loader.loadSfx(join("assets", "sfx", "boss_attack_2.wav")) 
        
        
    def loadModel(self):
        return Actor("assets/anims/Enemy.egg",{"Attack":"assets/anims/Enemy-AttackMelee.egg"})
    
    def update(self, dt, player_pos):
        
        entity_pos = self.model.getPos()
        
        delta_to_player = Vec3(entity_pos.x - player_pos.x, 0 , entity_pos.z - player_pos.z) 

        diff_to_player_normalized = Point2(delta_to_player.x, delta_to_player.z).normalized()

        
        x = math.degrees(math.atan2(diff_to_player_normalized.x, diff_to_player_normalized.y))
        
        x_direction = diff_to_player_normalized[0] * self.speed * dt
        z_direction = diff_to_player_normalized[1] * self.speed * dt
        
        black_hole_pull_vector = self.get_black_hole_pull_vector()
        
        if delta_to_player.length() <= 1:
            x_direction = 0
            z_direction = 0
                    
        if self.in_black_hole:
            
            x_direction += black_hole_pull_vector.x * dt
            z_direction += black_hole_pull_vector.z * dt
            
        self.model.setX(self.model.getX() - x_direction)
        self.model.setZ(self.model.getZ() - z_direction)
       
        # Safeguard 
        if self.model.getY() > 2: 
            self.model.setY(2)
        
        self.model.setR(x)
        
        current_time = time.time()
        if current_time - self.last_attack_time >= self.attackcooldown and delta_to_player.length()<6:
            self.attack()
            self.last_attack_time = current_time
        
    def _spawn_attack_hitbox(self, _):
        self.attack_sound.play()
        if self.model:
            self.attack_hitbox = self.model.attachNewNode(CollisionNode("attack"))
            #self.attack_hitbox.show()
            self.attack_hitbox.node().addSolid(CollisionBox(Point3(0,0,0),2,3,1.5))
            self.attack_hitbox.setTag("team", ENTITY_TEAMS.PLAYER)
            self.attack_hitbox.setPos(0,0,-1)
            # Set player team as player is the target
            self.attack_hitbox.node().setCollideMask(ENTITY_TEAMS.MELEE_ATTACK_BITMASK)
            base.cTrav.addCollider(self.attack_hitbox, self.notifier)
            base.taskMgr.doMethodLater(0.3, self._destroy_attack_hitbox, "destroy_melee_attack_hitbox")
            
        
        return Task.done
        
    def _destroy_attack_hitbox(self, _):
        if self.model:
            self.attack_hitbox.removeNode()
        self.speed = 8
        
    
        return Task.done
    
    
      
    def attack(self):
        self.speed = 12
        self.model.play('Attack')
        base.taskMgr.doMethodLater(0.3, self._spawn_attack_hitbox, "spawn_melee_attack_hitbox")
        
