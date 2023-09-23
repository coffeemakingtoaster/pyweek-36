from entities.entity_base import enity_base

from config import GAME_CONSTANTS, ENTITY_TEAMS

from helpers.model_helpers import load_model

from panda3d.core import *
    
import uuid
import math

class lightSpear_entity(enity_base):
    def __init__(self, spawn_x, spawn_z, direction, team: ENTITY_TEAMS):
        super().__init__()
        
        self.team = team 
        
        self.plnp = None
        
        self.direction =  direction
        
       
        self.model = load_model("lightSpear")
        if(direction.x < 0): 
            self.model.setR((Vec3(0,0,-1).angle_deg(direction)))
        else:
            self.model.setR(-(Vec3(0,0,-1).angle_deg(direction)))
        self.model.setScale(1.5)
        
        self.model.reparentTo(render)
        
        self.model.setPos(spawn_x, 2 ,spawn_z) 
        
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
        
        plight = PointLight('plight')
        plight.setColor((0.5,0.5,0.5, 1))
        self.plnp = self.model.attachNewNode(plight)
        plight.attenuation = (1, 0, 0.2)
        self.plnp.setPos(0, 0, 0)
        render.setLight(self.plnp)
        
        self.notifier = CollisionHandlerEvent()
        
        self.notifier.addInPattern("%fn-into")
        
        self.accept("bullet-into", self.on_collision)
        
        base.cTrav.addCollider(self.collision, self.notifier)
        
    def update(self, dt):
        
        self.travelled_distance += Vec3(self.direction * 40 * dt).length()
       
        # If max distance has been reached -> Kill object 
        if self.travelled_distance > GAME_CONSTANTS.BULLET_MAX_DISTANCE:
            self.is_dead = True
            return 
        
        # Why does this value have to be flipped?
        self.model.setX(self.model.getX() + self.direction.x * 40 * dt)
        self.model.setZ(self.model.getZ() + self.direction.z * 40 * dt)
        
    def on_collision(self, collision: CollisionEntry):
        # Is the bullet in the event the bullet from this entity class
        if collision.from_node.getTag("id") != self.id: 
            return
        # Ignore object that are on the same team or is an ability
        if collision.into_node.getTag("team") == self.team or collision.into_node.getTag("team") == ENTITY_TEAMS.ABILITY:
            return
        self.is_dead =  True
        
    def destroy(self):
        render.clearLight(self.plnp)
        self.model.removeNode()
        self.collision.removeNode()
        self.ignore_all()