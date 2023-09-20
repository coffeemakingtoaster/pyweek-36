from entities.base_enemy import base_enemy
from panda3d.core import Vec3, Point2, CollisionNode, CollisionSphere, CollisionHandlerEvent, CollisionEntry
import math
import time
from entities.bullet import bullet_entity

class ranged_enemy(base_enemy):
    
    def __init__(self, spawn_x, spawn_z):
        super().__init__(spawn_x,spawn_z)
        self.bullets = []
    
    def update(self, dt, player_pos):
        entity_pos = self.model.getPos()
        
        delta_to_player = Vec3(entity_pos.x - player_pos.x, 0 , entity_pos.z - player_pos.z) 
        delta_x_reversed = Vec3(entity_pos.x - player_pos.x, 0 , entity_pos.z - player_pos.z) 
        diff_to_player_normalized = Point2(delta_to_player.x, delta_to_player.z).normalized()
        x = math.degrees(math.atan2(diff_to_player_normalized.x, diff_to_player_normalized.y))
        
        x_direction = diff_to_player_normalized[0] * self.speed * dt
        z_direction = diff_to_player_normalized[1] * self.speed * dt
        
        if delta_to_player.length() > 12:
            self.model.setX(self.model.getX() - x_direction)
            self.model.setZ(self.model.getZ() - z_direction)
        elif delta_to_player.length() < 10:
            self.model.setX(self.model.getX() + x_direction)
            self.model.setZ(self.model.getZ() + z_direction)

        self.model.setR(x)
        
        current_time = time.time()
        if current_time - self.last_attack_time >= self.attackcooldown:
            self.attack(delta_x_reversed.normalized())
            self.last_attack_time = current_time
            
        bullets_to_delete = []
        for i, bullet in enumerate(self.bullets):
            bullet.update(dt)
            if bullet.is_dead:
                bullet.destroy()
                del self.bullets[i]
            
    def attack(self,delta_x_reversed):
        self.bullets.append(bullet_entity(self.model.getX(), self.model.getZ(), delta_x_reversed, self.team))