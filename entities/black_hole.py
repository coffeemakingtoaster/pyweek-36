from entities.entity_base import enity_base

from config import GAME_CONSTANTS, ENTITY_TEAMS

from panda3d.core import CollisionNode, CollisionSphere, PointLight

from helpers.model_helpers import load_model
from direct.actor.Actor import Actor

class black_hole_entity(enity_base):
    
    def __init__(self, spawn_pos):
        
        self.model = Actor("assets/anims/blackHole.egg",{"Expand":"assets/anims/blackHole-Expand.egg"})
        self.model.play("Expand")
        self.model.setPos(spawn_pos)
        self.model.setP(90)
        
        plight = PointLight('plight')
        plight.setColor((-2, -2, -2, 2))
        self.plnp = self.model.attachNewNode(plight)
        self.plnp.setPos(0, 0, 0)
        plight.attenuation = (1, 0, 0.01)
        render.setLight(self.plnp)
        
        self.model.reparentTo(render)
        
        self.collision = self.model.attachNewNode(CollisionNode("black_hole"))
        
        self.collision.setTag("team", ENTITY_TEAMS.ABILITY)
        
        self.collision.node().addSolid(CollisionSphere(0,0,0,GAME_CONSTANTS.BLACK_HOLE_RANGE))
        
        #self.collision.show()
       
        # Player is not affected 
        self.collision.node().setCollideMask(ENTITY_TEAMS.ABILITY_BITMASK)
        
        base.taskMgr.doMethodLater(GAME_CONSTANTS.BLACK_HOLE_DURATION, self.destroy, "black_hole_destroy")
        
    # basic wrapper for destroy
    def destroy(self, task):
        self.model.removeNode()
        render.clearLight(self.plnp)