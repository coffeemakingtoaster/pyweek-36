from ui.ui_base import ui_base
from config import GAME_CONSTANTS, PLAYER_ABILITIES
from helpers.utilities import format_float

from panda3d.core import TransparencyAttrib 
from direct.task.Task import Task

from direct.gui.DirectGui import DirectLabel, OnscreenImage

import sys
from os.path import join

class game_hud(ui_base):
    def __init__(self, hp_count):
        ui_base.__init__(self)

        self.ui_elements = []
        
        self.accept("display_hp", self.display_hp_count)
        
        self.accept("set_ability_on_cooldown", self.set_ability_cooldown)
        
        self.hp_display = DirectLabel(text="{}/{}".format(hp_count, GAME_CONSTANTS.PLAYER_MAX_HP), scale=0.2, pos=(-0.6, 0, -0.8), color=(255,0,0,1))
        self.ui_elements.append(self.hp_display)
        
        self.dash_ability_icon = self._create_ability_icon(PLAYER_ABILITIES.DASH, (0.6,0,-0.8))
        self.ui_elements.append(self.dash_ability_icon)
        
        self.is_destroyed = False
        
    def _create_ability_icon(self, name,pos, scale=0.2):
        self.ui_elements.append(OnscreenImage(image=join("assets","icons","hud","backplane.png"), pos=pos, scale=scale))
        img = OnscreenImage(image=join("assets","icons","hud","{}.png".format(name)), pos=pos, scale=scale)
        return img
        
    def display_hp_count(self, hp_value):
        self.hp_display["text"] =  "{}/{}".format(hp_value, GAME_CONSTANTS.PLAYER_MAX_HP)
        
    def set_ability_cooldown(self, ability_name, ready_time):
        print(ability_name)
        if ability_name == PLAYER_ABILITIES.DASH:
            self.dash_ability_icon.setTransparency(1, 0)
            self.dash_ability_icon.setAlphaScale(0.5)
            cooldownText = DirectLabel(text=format_float(ready_time - self._get_current_time()), pos=self.dash_ability_icon.getPos(), scale=self.dash_ability_icon.getScale())
            base.taskMgr.add(self._update_abilities_cooldown_display, "hud_update_dash", extraArgs=[ready_time, cooldownText, self.dash_ability_icon])
            
    def _get_current_time(self):
        return base.clock.getLongTime() 
    
    
    def destroy(self):
        self.ignoreAll()
        base.taskMgr.removeTasksMatching("hud_update*")
        super().destroy()
            
    def _update_abilities_cooldown_display(self, ready_time, cd_text: DirectLabel, image: OnscreenImage):
        time_diff = ready_time - self._get_current_time()
        if time_diff <= 0:
            # Remove cd text and transparency
            cd_text.remove_node()
            image.setAlphaScale(1)
            # Ability is ready
            return 
        cd_text.setText(format_float(time_diff))
        return Task.cont