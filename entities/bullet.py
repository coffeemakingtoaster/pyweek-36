from entities.entity_base import enity_base

from config import GAME_CONSTANTS, ENTITY_TEAMS

from helpers.model_helpers import load_model

from panda3d.core import Vec3, Point2, CollisionNode, CollisionSphere, CollisionEntry, CollisionHandlerEvent, Point3, BitMask32, NodePath, CollideMask
    
import uuid
import math

class bullet_entity(enity_base):
    def __init__(self, spawn_x, spawn_z, direction, team: ENTITY_TEAMS):
        super().__init__()
        
        self.team = team 
        
        self.direction =  direction
       
        # I am not sure why this is needed 
        self.direction.x = self.direction.x * -1
        
        self.model = load_model("bullet")
        
        self.model.setScale(0.3)
        
        self.model.reparentTo(render)
        
        self.model.setPos(spawn_x,0,spawn_z) 
        
        # This is slightly bugged -> Will be removed anyway for final model 
        bullet_rotation = math.degrees(math.atan2(direction.z, direction.x))
        
        self.model.lookAt(direction)
        
        self.id = str(uuid.uuid4())
        
        self.collision: NodePath = self.model.attachNewNode(CollisionNode("bullet"))
        
        self.collision.setTag("team", self.team)
        
        self.collision.setTag("id", self.id)
        
        self.collision.node().addSolid(CollisionSphere(0,1,0,0.5))
        
        if self.team == ENTITY_TEAMS.PLAYER: 
            print("setting enemy")
            self.collision.node().setCollideMask(ENTITY_TEAMS.ENEMIES_BITMASK)
        else:
            print("Setting player")
            self.collision.node().setCollideMask(ENTITY_TEAMS.PLAYER_BITMASK)
        
        self.is_dead = False
        
        self.travelled_distance = 0
        
        self.collision.show()
        
        self.notifier = CollisionHandlerEvent()
        
        self.notifier.addInPattern("%fn-into")
        
        self.accept("bullet-into", self.on_collision)
        
        base.cTrav.addCollider(self.collision, self.notifier)
        
    def update(self, dt):
        
        self.travelled_distance += Vec3(self.direction * GAME_CONSTANTS.BULLET_SPEED * dt).length()
       
        # If max distance has been reached -> Kill object 
        if self.travelled_distance > GAME_CONSTANTS.BULLET_MAX_DISTANCE:
            self.is_dead = True
            return 
        
        # Why does this value have to be flipped?
        self.model.setX(self.model.getX() + self.direction.x * GAME_CONSTANTS.BULLET_SPEED * dt)
        self.model.setZ(self.model.getZ() + self.direction.z * GAME_CONSTANTS.BULLET_SPEED * dt)
        
    def on_collision(self, collision: CollisionEntry):
        print("into ", end="") 
        print(collision.into_node.into_collide_mask)
        print(collision.into_node.from_collide_mask)
        print("from ", end="")
        print(collision.from_node.from_collide_mask)
        print(collision.from_node.into_collide_mask)
        # Is the bullet in the event the bullet from this entity class
        if collision.from_node.getTag("id") != self.id: 
            return
       
        # Ignore object that are on the same team 
        if collision.into_node.getTag("team") == self.team:
            return
        
        self.is_dead =  True
        
    def destroy(self):
        self.model.removeNode()
        self.collision.removeNode()
        self.ignore_all()
        
        