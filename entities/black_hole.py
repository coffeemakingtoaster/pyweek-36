from entities.entity_base import enity_base

from config import GAME_CONSTANTS, ENTITY_TEAMS

from panda3d.core import CollisionNode, CollisionSphere

from helpers.model_helpers import load_model

class black_hole_entity(enity_base):
    
    def __init__(self, spawn_pos):
        
        self.model = load_model("barrel")
        
        self.model.setPos(spawn_pos)
        
        self.model.reparentTo(render)
        
        self.collision = self.model.attachNewNode(CollisionNode("black_hole"))
        
        self.collision.setTag("team", ENTITY_TEAMS.ABILITY)
        
        self.collision.node().addSolid(CollisionSphere(0,0,0,GAME_CONSTANTS.BLACK_HOLE_RANGE))
        
        self.collision.show()
       
        # Player is not affected 
        self.collision.node().setCollideMask(ENTITY_TEAMS.ABILITY_BITMASK)
        
        base.taskMgr.doMethodLater(GAME_CONSTANTS.BLACK_HOLE_DURATION, self.destroy, "black_hole_destroy")
        
    # basic wrapper for destroy
    def destroy(self, task):
        self.model.removeNode()