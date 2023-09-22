from entities.entity_base import enity_base
from config import GAME_CONSTANTS
from helpers.model_helpers import load_model
from panda3d.core import *
from config import MAP_CONSTANTS, ENTITY_TEAMS


from direct.actor.Actor import Actor
from entities.ranged_enemy import ranged_enemy
from entities.melee_enemy import melee_enemy
from entities.tank_enemy import tank_enemy

class Altar(enity_base):
    def __init__(self,pos):
        super().__init__()
        self.pos = pos
        self.model = Actor("assets/anims/Boss.egg",{"Turn":"assets/anims/Boss-Attack1.egg"})
        self.model.setPosHprScale(pos[0],pos[1],pos[2], 0, 90, 180, 2, 2, 2)
        self.plnp = None
        
        self.notifier = CollisionHandlerEvent()
        self.notifier.addInPattern("%fn-into-%in")
        
        self.model.reparentTo(render)
        #self.model.setPos(pos[0],pos[1],pos[2])
        #self.model.setP(90)
        #self.model.setR(180)
        self.activationsphere = self.model.attach_new_node(CollisionNode("altar-sphere"))
        #self.activationsphere.show()
        self.activationsphere.setTag("team", ENTITY_TEAMS.PLAYER)
        self.activationsphere.node().setCollideMask(ENTITY_TEAMS.MELEE_ATTACK_BITMASK)
        base.cTrav.addCollider(self.activationsphere, self.notifier)
        min_point, max_point = self.model.getTightBounds()
        cp = CollisionSphere(0,0,0, 5)
        self.activationsphere.node().addSolid(cp)
        base.cTrav.addCollider(self.activationsphere, CollisionHandlerEvent())
        print("InitAltar")
                
    def activate(self):
        plight = PointLight('plight')
        plight.setColor((-5, -5, -5, 5))
        self.plnp = self.model.attachNewNode(plight)
        self.plnp.setPos(0, 0, 5)
        plight.attenuation = (1, 0, 0.05)
        render.setLight(self.plnp)
        self.model.loop("Turn")
        self.activationsphere.removeNode()