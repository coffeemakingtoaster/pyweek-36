from entities.entity_base import enity_base
from config import GAME_CONSTANTS
from helpers.model_helpers import load_model


from direct.actor.Actor import Actor
from entities.ranged_enemy import ranged_enemy
from entities.melee_enemy import melee_enemy
from entities.tank_enemy import tank_enemy
from entities.healer_enemy import healer_enemy
from entities.sniper_enemy import sniper_enemy
from entities.priest_enemy import priest_enemy

class Spawner(enity_base):
    def __init__(self,pos,wave,type,roomSize,roomZero):
        super().__init__()
        self.pos = pos
        self.model = load_model("vase")
        #self.model.reparentTo(render)
        self.model.setPos(pos[0],pos[1],pos[2])
        self.wave = wave
        self.type = type
        self.roomSize = roomSize
        self.roomZero = roomZero
        
        
    def spawn(self,entities):
        if self.type == "ranged_enemy":
            entities.append(ranged_enemy(self.pos[0], self.pos[2],self.roomSize,self.roomZero))
        elif self.type == "melee_enemy":
            entities.append(melee_enemy(self.pos[0], self.pos[2],self.roomSize,self.roomZero))
        elif self.type == "tank_enemy":
            entities.append(tank_enemy(self.pos[0], self.pos[2],self.roomSize,self.roomZero))
        elif self.type == "healer_enemy":
            entities.append(healer_enemy(self.pos[0], self.pos[2],self.roomSize,self.roomZero,entities))
        elif self.type == "sniper_enemy":
            entities.append(sniper_enemy(self.pos[0], self.pos[2],self.roomSize,self.roomZero))
        elif self.type == "priest_enemy":
            entities.append(priest_enemy(self.pos[0], self.pos[2],self.roomSize,self.roomZero,entities))
        else:
            pass
        
    

