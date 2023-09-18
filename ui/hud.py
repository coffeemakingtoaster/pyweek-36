from ui.ui_base import ui_base
from config import GAME_CONSTANTS
from helpers.utilities import save_config

from direct.gui.DirectGui import DirectLabel 

import sys
from os.path import join

class game_hud(ui_base):
    def __init__(self, hp_count):
        ui_base.__init__(self)

        self.ui_elements = []
        
        self.accept("display_hp", self.display_hp_count)
        
        self.hp_display = DirectLabel(text="{}/{}".format(hp_count, GAME_CONSTANTS.PLAYER_MAX_HP), scale=0.2, pos=(-0.6, 0, -0.8), color=(255,0,0,1))
        self.ui_elements.append(self.hp_display)
        
        
    def display_hp_count(self, hp_value):
        self.hp_display["text"] =  "{}/{}".format(hp_value, GAME_CONSTANTS.PLAYER_MAX_HP)
        
        
