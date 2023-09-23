from entities.entity_base import enity_base

from config import GAME_CONSTANTS, ENTITY_TEAMS

from helpers.model_helpers import load_model
from direct.actor.Actor import Actor

from panda3d.core import Vec3, Point2, CollisionNode, CollisionSphere, CollisionEntry, CollisionHandlerEvent, Point3, BitMask32, NodePath, CollideMask
    
import uuid
import math

class bullet_entity(enity_base):
    def __init__(self, spawn_x, spawn_z, direction, team: ENTITY_TEAMS):
        super().__init__()
        
        self.team = team 
        
        self.direction =  direction
       
        self.model = Actor("assets/anims/Bullet.egg",{"Explode":"assets/anims/Bullet-Explode.egg"})
        
        self.model.setScale(1)
        
        self.model.reparentTo(render)
        
        self.model.setPos(spawn_x, 2 ,spawn_z) 
        
        # This is slightly bugged -> Will be removed anyway for final model 
        bullet_rotation = math.degrees(math.atan2(direction.z, direction.x))
        
        self.model.lookAt(direction)
        
        self.id = str(uuid.uuid4())
        
        self.collision: NodePath = self.model.attachNewNode(CollisionNode("bullet"))
        
        self.collision.setTag("team", self.team)
        
        self.collision.setTag("id", self.id)
        
        self.collision.node().addSolid(CollisionSphere(0,1,0,0.5))
        
        if self.team == ENTITY_TEAMS.PLAYER: 
            #print("setting enemy")
            self.collision.node().setCollideMask(ENTITY_TEAMS.ENEMIES_BITMASK)
        else:
            #print("Setting player")
            self.collision.node().setCollideMask(ENTITY_TEAMS.PLAYER_BITMASK)
        
        self.is_dead = False
        
        self.travelled_distance = 0
        
        #self.collision.show()
        
        self.notifier = CollisionHandlerEvent()
        
        self.notifier.addInPattern("%fn-into")
        
        self.accept("bullet-into", self.on_collision)
        
        self.stopped = False
        
        base.cTrav.addCollider(self.collision, self.notifier)
        
    def update(self, dt):
        
        self.travelled_distance += Vec3(self.direction * GAME_CONSTANTS.BULLET_SPEED * dt).length()
       
        # If max distance has been reached -> Kill object 
        if self.travelled_distance > GAME_CONSTANTS.BULLET_MAX_DISTANCE:
            self.is_dead = True
            return 
        if not self.stopped:
        # Why does this value have to be flipped?
            self.model.setX(self.model.getX() + self.direction.x * GAME_CONSTANTS.BULLET_SPEED * dt)
            self.model.setZ(self.model.getZ() + self.direction.z * GAME_CONSTANTS.BULLET_SPEED * dt)
        
    def on_collision(self, collision: CollisionEntry):
        # Is the bullet in the event the bullet from this entity class
        if collision.from_node.getTag("id") != self.id: 
            return
        # Ignore object that are on the same team or is an ability
        if collision.into_node.getTag("team") == self.team or collision.into_node.getTag("team") == ENTITY_TEAMS.ABILITY:
            return
        self.model.play("Explode")
        self.stopped = True
        base.taskMgr.doMethodLater(0.2, self.die, "die") 
        
    
    def die(self,_):
        self.is_dead =  True
        
    def destroy(self):
        self.model.removeNode()
        self.collision.removeNode()
        self.ignore_all()