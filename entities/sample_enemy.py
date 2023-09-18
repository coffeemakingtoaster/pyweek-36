from entities.entity_base import enity_base

from panda3d.core import Vec3, Point2

import math

from helpers.model_helpers import load_model

from config import GAME_CONSTANTS

class sample_enemy_entity(enity_base):
    
    def __init__(self, spawn_x, spawn_z):
        super().__init__()

        self.model = load_model("player")
        
        self.model.reparentTo(render)
        
        self.model.setPos(spawn_x,0,spawn_z)
        
        self.current_hp = GAME_CONSTANTS.SAMPLE_ENEMY_MAX_HP
        
    def update(self, dt, player_pos):
        entity_pos = self.model.getPos()
        
        delta_to_player = Vec3(entity_pos.x - player_pos.x, 0 , entity_pos.z - player_pos.z) 

        diff_to_player_normalized = Point2(delta_to_player.x, delta_to_player.z)

        x = math.degrees(math.atan2(diff_to_player_normalized.x, diff_to_player_normalized.y))

        self.model.setR(x)