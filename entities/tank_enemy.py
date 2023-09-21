from entities.base_enemy import base_enemy
from entities.entity_base import enity_base

from panda3d.core import Vec3, Point2, CollisionNode, CollisionSphere, CollisionHandlerEvent, CollisionEntry

import math
import uuid

from helpers.model_helpers import load_model

from config import GAME_CONSTANTS, ENTITY_TEAMS
import time
from direct.actor.Actor import Actor


class tank_enemy(base_enemy):
    
    def __init__(self, spawn_x, spawn_z):
        super().__init__(spawn_x,spawn_z)
        
    def loadModel(self):
        return Actor("assets/anims/TankEnemy.egg",{"Attack":"assets/anims/TankEnemy-Attack.egg","Idle":"assets/anims/TankEnemy-Bite.egg"})
    
    def update(self, dt, player_pos):
        
        entity_pos = self.model.getPos()
        
        delta_to_player = Vec3(entity_pos.x - player_pos.x, 0 , entity_pos.z - player_pos.z) 

        diff_to_player_normalized = Point2(delta_to_player.x, delta_to_player.z).normalized()

        
        x = math.degrees(math.atan2(diff_to_player_normalized.x, diff_to_player_normalized.y))
        
        x_direction = diff_to_player_normalized[0] * self.speed * dt
        z_direction = diff_to_player_normalized[1] * self.speed * dt
       
        # Reduce Pull for tank
        black_hole_pull_vector = self.get_black_hole_pull_vector() * GAME_CONSTANTS.BLACK_HOLE_TANK_PULL_FACTOR 
        
        if delta_to_player.length() <= 2:
            x_direction = 0
            z_direction = 0
                    
        if self.in_black_hole:
            
            x_direction += black_hole_pull_vector.x * dt
            z_direction += black_hole_pull_vector.z * dt
            
        self.model.setX(self.model.getX() - x_direction)
        self.model.setZ(self.model.getZ() - z_direction)
       
        self.model.setR(x) 
        
        # Safeguard 
        if self.model.getY() > 1: 
            self.model.setY(1)
        
        current_time = time.time()
        if current_time - self.last_attack_time >= self.attackcooldown and delta_to_player.length()<4:
            self.attack()
            self.last_attack_time = current_time
    
      
    def attack(self):
        self.model.play('Attack')
