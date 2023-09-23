from entities.entity_base import enity_base

from panda3d.core import Vec3, Point2, CollisionNode, CollisionSphere, CollisionHandlerEvent, CollisionEntry

import math
import uuid

from helpers.model_helpers import load_model
from helpers.math_helpers import get_black_hole_pull_vector

from config import GAME_CONSTANTS, ENTITY_TEAMS
import time
from direct.actor.Actor import Actor

class base_enemy(enity_base):
    
    def __init__(self, spawn_x, spawn_z):
        super().__init__()
        
        self.team = ENTITY_TEAMS.ENEMIES 
        
        self.speed = GAME_CONSTANTS.ENEMY_MOVEMENT_SPEED 
        
        self.attackcooldown = 2
        self.last_attack_time = time.time()

        self.model = self.loadModel()
        self.model.loop('Idle')
        self.model.getChild(0).setR(90)
        self.model.getChild(0).setH(90)
        self.model.getChild(0).setP(90)
        
        self.model.reparentTo(render)
        
        self.model.setPos(spawn_x,2,spawn_z)
        
        self.max_hp = 5
        self.current_hp = 5
        
        self.id = str(uuid.uuid4())
        
        self.collision = self.model.attachNewNode(CollisionNode("enemy"))
        
        self.collision.node().addSolid(CollisionSphere(0,0,0,0.9))
        
        self.collision.node().setCollideMask(ENTITY_TEAMS.ENEMIES_BITMASK)
        
        self.ability_collision = self.model.attachNewNode(CollisionNode("enemy_ability_hitbox"))
        
        self.ability_collision.node().addSolid(CollisionSphere(0,0,0,0.9))
        
        self.ability_collision.node().setCollideMask(ENTITY_TEAMS.ABILITY_BITMASK)
        
        #self.collision.show()
        
        self.collision.setTag("team", self.team)
        self.ability_collision.setTag("team", self.team)
        self.collision.setTag("id", self.id)
        self.ability_collision.setTag("id", self.id)
        
        self.notifier = CollisionHandlerEvent()

        self.notifier.addInPattern("%fn-into-%in")
        self.notifier.addOutPattern("%fn-out-%in")
        
        self.accept("bullet-into", self.bullet_hit)
        
        self.accept("enemy_ability_hitbox-into-black_hole", self.enter_black_hole)
        
        self.accept("enemy_ability_hitbox-out-black_hole", self.leave_black_hole)
        
        base.cTrav.addCollider(self.collision, self.notifier)
        base.cTrav.addCollider(self.ability_collision, self.notifier)
        
        self.is_dead = False
        self.enemy = True
        self.in_black_hole = False
        self.black_hole_position = None
        
    def loadModel(self):
        return Actor("assets/anims/Enemy.egg",{"Attack":"assets/anims/Enemy-Attack.egg","Bite":"assets/anims/Enemy-Bite.egg"})
        
    def destroy(self):
        self.model.removeNode()
        self.collision.removeNode()
        self.ignore_all()
       
    # collisionentry is not needed -> we ignore it 
    def bullet_hit(self, entry: CollisionEntry):
        # Ignore collisions triggered by other enemies
        if entry.into_node.getTag("id") != self.id:
            return
        
        # Only take damage from bullets targeted at own team 
        if entry.into_node.getTag("team") != self.team:
            #print("nope")
            return
        
        self.takeDamage(1)
        
    def takeDamage(self,dmg):
        self.current_hp -=dmg
        #print("Taking damage")
        print(self.current_hp)
        if self.current_hp <= 0:
            self.is_dead = True
            
    def attack(self):
        print("attack")
    
    def heal(self,amount):
        if self.current_hp < self.max_hp:
            self.current_hp += amount
        
    def enter_black_hole(self, collision: CollisionEntry):
        #print("In black hole")
        self.in_black_hole = True
        self.black_hole_position = collision.into_node_path.getPos(render)
        
        
    def leave_black_hole(self, collision):
        #print("Leaving black hole")
        self.in_black_hole = False
        self.black_hole_position = None
        
    def get_black_hole_pull_vector(self) -> Vec3:
        if not self.in_black_hole or self.black_hole_position is None:
            return Vec3(0,0,0)
        return get_black_hole_pull_vector(self.model.getPos(), self.black_hole_position) 
