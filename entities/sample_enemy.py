from entities.entity_base import enity_base
from entities.base_enemy import base_enemy

from panda3d.core import Vec3, Point2, CollisionNode, CollisionSphere, CollisionHandlerEvent, CollisionEntry

import math
import uuid

from helpers.model_helpers import load_model

from config import GAME_CONSTANTS, ENTITY_TEAMS

class sample_enemy_entity(base_enemy):
    
    def __init__(self, spawn_x, spawn_z):
        super().__init__(spawn_x,spawn_z)
        
        

        
    
       
   
    
        
 