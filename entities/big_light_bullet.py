from entities.entity_base import enity_base

from config import GAME_CONSTANTS, ENTITY_TEAMS

from helpers.model_helpers import load_model

from panda3d.core import *
    
import uuid
import math

from os.path import join

class bigLightBullet_entity(enity_base):
    def __init__(self, spawn_x, spawn_z, direction, team: ENTITY_TEAMS):
        super().__init__()
        
        self.team = team 
        
        self.plnp = None
        
        self.direction =  direction
       
        self.model = load_model("lightBullet")
        
        self.model.reparentTo(render)
        
        self.model.setPos(spawn_x, 2 ,spawn_z) 
        self.model.setScale(2)
        
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
        plight.attenuation = (1, 0, 0.1)
        self.plnp.setPos(0, 0, 0)
        render.setLight(self.plnp)
        
        self.notifier = CollisionHandlerEvent()
        
        self.notifier.addInPattern("%fn-into")
        
        self.accept("bullet-into", self.on_collision)
        
        self.destroy_sound = base.loader.loadSfx(join("assets", "sfx", "light_bullet_destroy.wav"))
        
        base.cTrav.addCollider(self.collision, self.notifier)
        
    def update(self, dt):
        
        self.travelled_distance += Vec3(self.direction * 10 * dt).length()
       
        # If max distance has been reached -> Kill object 
        if self.travelled_distance > GAME_CONSTANTS.BULLET_MAX_DISTANCE:
            self.is_dead = True
            return 
        
        # Why does this value have to be flipped?
        self.model.setX(self.model.getX() + self.direction.x * 10 * dt)
        self.model.setZ(self.model.getZ() + self.direction.z * 10 * dt)
        
    def on_collision(self, collision: CollisionEntry):
        # Is the bullet in the event the bullet from this entity class
        if collision.from_node.getTag("id") != self.id: 
            return
        # Ignore object that are on the same team or is an ability
        if collision.into_node.getTag("team") == self.team or collision.into_node.getTag("team") == ENTITY_TEAMS.ABILITY:
            return
        self.is_dead =  True
        
    def destroy(self):
        self.destroy_sound.play()
        render.clearLight(self.plnp)
        self.model.removeNode()
        self.collision.removeNode()
        self.ignore_all()