from entities.entity_base import enity_base
from config import GAME_CONSTANTS
from helpers.model_helpers import load_model
from panda3d.core import *
from config import MAP_CONSTANTS, ENTITY_TEAMS

from helpers.important_helpers import get_boss_name

from direct.actor.Actor import Actor
from entities.ranged_enemy import ranged_enemy
from entities.melee_enemy import melee_enemy
from entities.tank_enemy import tank_enemy

class boss(enity_base):
    def __init__(self,pos):
        super().__init__()
        
        self.name = get_boss_name()
        self.pos = pos
        self.model = Actor("assets/anims/Boss.egg",{"Turn":"assets/anims/Boss-Attack1.egg"})
        self.model.setPosHprScale(pos[0],pos[1],pos[2], 0, 90, 180, 2, 2, 2)
        self.plnp = None
        
        self.id = "boss"
        
        self.team = ENTITY_TEAMS.ENEMIES
        
        self.notifier = CollisionHandlerEvent()
        self.notifier.addInPattern("%fn-into-%in")
        
        self.model.reparentTo(render)
        #self.model.setPos(pos[0],pos[1],pos[2])
        #self.model.setP(90)
        #self.model.setR(180)
        self.activationsphere = self.model.attach_new_node(CollisionNode("boss-sphere"))
        self.collision = self.model.attach_new_node(CollisionNode("boss"))
        #self.activationsphere.show()
        self.activationsphere.setTag("team", ENTITY_TEAMS.ENEMIES)
        self.collision.setTag("team", ENTITY_TEAMS.ENEMIES)
        # Needed for preloading
        self.collision.setTag("id", self.id)
        self.activationsphere.node().setCollideMask(ENTITY_TEAMS.MELEE_ATTACK_BITMASK)
        self.collision.node().setCollideMask(ENTITY_TEAMS.ENEMIES_BITMASK)
        base.cTrav.addCollider(self.activationsphere, self.notifier)
        base.cTrav.addCollider(self.collision, self.notifier)
        min_point, max_point = self.model.getTightBounds()
        cp = CollisionSphere(0,0,0,5)
        
        self.accept("bullet-into", self.bullet_hit)
        
        self.activationsphere.node().addSolid(cp)
        
        self.collision.node().addSolid(CollisionSphere(0,0,0,1))
        self.collision.show()
        base.cTrav.addCollider(self.activationsphere, CollisionHandlerEvent())
        
        self.current_hp = GAME_CONSTANTS.BOSS_HP
        
        self.active = False
        
        self.is_dead = False
        print("InitBoss")
        
        
    def update(self, dt):
        pass
                
    def activate(self):
        plight = PointLight('plight')
        plight.setColor((5, 5, 5, 5))
        self.plnp = self.model.attachNewNode(plight)
        self.plnp.setPos(0, 0, 5)
        plight.attenuation = (1, 0, 0.05)
        render.setLight(self.plnp)
        self.model.loop("Turn")
        self.activationsphere.removeNode()
        self.active = True
        
    def take_damage(self, damage):
        if self.active:
            self.current_hp -= damage 
            messenger.send("display_boss_hp", [self.current_hp])
            if self.current_hp <= 0:
                self.is_dead = True
        
    # collisionentry is not needed -> we ignore it 
    def bullet_hit(self, entry: CollisionEntry):
        print("boss damage")
        # Ignore collisions triggered by other enemies
        if entry.into_node.getTag("id") != self.id:
            return
        
        # Only take damage from bullets targeted at own team 
        if entry.into_node.getTag("team") != self.team:
            #print("nope")
            return
        
        self.take_damage(1)