from entities.base_enemy import base_enemy
from panda3d.core import Vec3, Point2, CollisionNode, CollisionSphere, CollisionHandlerEvent, CollisionEntry
import math
import time
from entities.big_light_bullet import bigLightBullet_entity
from entities.light_bullet import lightBullet_entity
from direct.actor.Actor import Actor
import random
from config import MAP_CONSTANTS
from os.path import join

class priest_enemy(base_enemy):
    
    def __init__(self, spawn_x, spawn_z,roomSize,roomZero,enemies):
        super().__init__(spawn_x,spawn_z,roomSize,roomZero)
        self.attackcooldown = 1
        self.enemies = enemies
        self.healAmount = 1
        self.bullets =[]
        self.attack_sfx = base.loader.loadSfx(join("assets", "sfx","boss_shoot.wav"))
        self.heal_sfx = base.loader.loadSfx(join("assets","sfx", "enemy_heal.wav"))
    
    def loadModel(self):
        return Actor("assets/anims/Priest.egg",{"Attack":"assets/anims/Priest-Attack.egg","Heal":"assets/anims/Priest-Heal.egg"})
    
    def update(self, dt, player_pos):
        entity_pos = self.model.getPos()
        
        delta_to_player = Vec3(entity_pos.x - player_pos.x, 0 , entity_pos.z - player_pos.z) 
        delta_x_reversed = Vec3(entity_pos.x - player_pos.x, 0 , entity_pos.z - player_pos.z) * -1
        diff_to_player_normalized = Point2(delta_to_player.x, delta_to_player.z).normalized()
        x = math.degrees(math.atan2(diff_to_player_normalized.x, diff_to_player_normalized.y))
        
        x_direction = diff_to_player_normalized[0] * self.speed * dt
        z_direction = diff_to_player_normalized[1] * self.speed * dt
        
        leash = Vec3(entity_pos.x - self.roomZero[0], 0 , entity_pos.z - self.roomZero[2]).length()
        
       
        if delta_to_player.length() < 12 and leash < (self.roomSize*MAP_CONSTANTS.ROOM_SIZE/2)-2:
            x_direction = -x_direction  
            z_direction = -z_direction
    
        black_hole_pull_vector = self.get_black_hole_pull_vector()    
                    
        if self.in_black_hole:
            
            x_direction += black_hole_pull_vector.x * dt
            z_direction += black_hole_pull_vector.z * dt
            
        self.model.setX(self.model.getX() - x_direction)
        self.model.setZ(self.model.getZ() - z_direction)

        self.model.setR(x)
        
        # Safeguard 
        if self.model.getY() > 2: 
            self.model.setY(2)
        
        current_time = time.time()
        if current_time - self.last_attack_time >= self.attackcooldown:
            action = random.randint(1,2)
            if action == 1:
                self.attack(delta_x_reversed.normalized())
            else:
                self.heal_enemies()
            
            self.last_attack_time = current_time
        
        bullets_to_delete = []
        for i, bullet in enumerate(self.bullets):
            bullet.update(dt)
            if bullet.is_dead:
                bullet.destroy()
                del self.bullets[i]
            
    def attack(self,delta_x_reversed):
        self.bullets.append(bigLightBullet_entity(self.model.getX(), self.model.getZ(), delta_x_reversed, self.team))
        
        self.model.play('Attack')
          
            
    def heal_enemies(self):
        for enemy in self.enemies:
            enemy.heal(self.healAmount)
        self.heal_sfx.play()
        self.model.play('Heal')
        
        
    def destroy(self):
        for bullet in self.bullets:
            bullet.destroy()
        super().destroy()