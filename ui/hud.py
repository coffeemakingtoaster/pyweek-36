from ui.ui_base import ui_base
from config import GAME_CONSTANTS, PLAYER_ABILITIES
from helpers.utilities import format_float

from panda3d.core import TransparencyAttrib 
from direct.task.Task import Task

from direct.gui.DirectGui import DirectLabel, OnscreenImage

import sys
from os.path import join

class game_hud(ui_base):
    def __init__(self):
        ui_base.__init__(self)
        
        print("Hud init")

        self.ui_elements = []
        
        self.accept("display_hp", self.display_hp_count)
        self.accept("display_boss_hp", self.display_boss_hp_count)
        
        self.accept("set_ability_on_cooldown", self.set_ability_cooldown)

        self.hp_display_background = OnscreenImage(scale=0.1, pos=(0, 0, -0.7), image=join("assets", "icons", "hud", "hp_backplane.png"))
        self.hp_display_background.setTransparency(TransparencyAttrib.MAlpha)
        self.ui_elements.append(self.hp_display_background)
        self.hp_display = DirectLabel(text="{}".format(GAME_CONSTANTS.PLAYER_MAX_HP), scale=0.1, pos=(-0.008, 0, -0.74), text_font=self.font, relief=None, text_fg=(255,255,255,1))
        self.ui_elements.append(self.hp_display)
        
        self.dash_ability_icon = self._create_ability_icon(PLAYER_ABILITIES.DASH, (0.4,0,-0.8))
        self.ui_elements.append(self.dash_ability_icon)
        
        self.black_hole_ability_icon = self._create_ability_icon(PLAYER_ABILITIES.BLACK_HOLE, (-0.4, 0, -0.8))
        self.ui_elements.append(self.black_hole_ability_icon)
        
        self.current_cooldowns = {
            PLAYER_ABILITIES.DASH: 0,
            PLAYER_ABILITIES.BLACK_HOLE: 0
        }
        
        self.is_paused = False
        
    def _create_ability_icon(self, name,pos, scale=0.1):
        backplane = OnscreenImage(image=join("assets","icons","hud","backplane.png"), pos=pos, scale=scale)
        backplane.setTransparency(TransparencyAttrib.MAlpha)
        self.ui_elements.append(backplane)
        img = OnscreenImage(image=join("assets","icons","hud","{}.png".format(name)), pos=pos, scale=scale)
        img.setTransparency(TransparencyAttrib.MAlpha)
        border = OnscreenImage(image=join("assets", "icons", "hud", "border.png"), pos=pos, scale=scale)
        border.setTransparency(TransparencyAttrib.MAlpha)
        self.ui_elements.append(border)
        return img
        
    def display_hp_count(self, hp_value):
        hp_value = max(0, hp_value)
        self.hp_display["text"] =  "{}".format(hp_value)
        
    def set_ability_cooldown(self, ability_name, ready_time):
        print(ability_name)
        ability_icon = None
        if ability_name == PLAYER_ABILITIES.DASH:
            ability_icon = self.dash_ability_icon
        elif ability_name == PLAYER_ABILITIES.BLACK_HOLE:
            ability_icon = self.black_hole_ability_icon
       
        # Protect from invalid input 
        if ability_icon is None:
            return
    
        ability_icon.setTransparency(1, 0)
        ability_icon.setAlphaScale(0.5)
        self.current_cooldowns[ability_name] = ready_time - self._get_current_time()
        cooldownText = DirectLabel(text=format_float(self.current_cooldowns[ability_name]), pos=(ability_icon.getX(), ability_icon.getY(), ability_icon.getZ() - 0.02), scale=ability_icon.getScale() - 0.05, text_font=self.font, text_fg=(255,255,255,1), relief=False)
        self.ui_elements.append(cooldownText)
        base.taskMgr.add(self._update_abilities_cooldown_display, "hud_update_{}".format(ability_name), extraArgs=[ability_name, cooldownText, ability_icon])
            
    def _get_current_time(self):
        return base.clock.getLongTime() 
    
    def destroy(self):
        self.ignoreAll()
        base.taskMgr.removeTasksMatching("hud_update*")
        try:
            self.boss_hp_display.setScale(0,0,0)
            self.boss_name_display.setScale(0,0,0)
            self.boss_hp_backpaint.setScale(0,0,0)
            self.boss_hp_base.setScale(0,0,0) 
            super().destroy()
        except:
            print("Nodes were already cleaned up")
            
    def _update_abilities_cooldown_display(self, spell_name, cd_text: DirectLabel, image: OnscreenImage):
        if self.is_paused:
            return Task.cont
        
        self.current_cooldowns[spell_name] -= base.clock.dt
        
        if self.current_cooldowns[spell_name] <= 0:
            # Remove cd text and transparency
            cd_text.remove_node()
            image.setAlphaScale(1)
            # Ability is ready
            return Task.done 
        cd_text.setText(format_float(self.current_cooldowns[spell_name]))
        return Task.cont
    
    def pause(self):
        self.is_paused = True
        
    def resume(self):
        self.is_paused = False
        
    def display_boss_hp_count(self, hp_value):
        hp_value = max(hp_value, 0)
        step = (hp_value/GAME_CONSTANTS.BOSS_HP) * 0.995
        self.boss_hp_display.setScale(step, 1, 0.045)
        # Pos of -0.995 is final
        self.boss_hp_display.setX(-0.995 + step)
        
    def enter_boss_mode(self, name):
        # Create Boss HP Bar
        self.boss_name_display = DirectLabel(text=name, text_fg=(255,255,255,1), pos=(0,0,0.9), relief=None, scale=0.1, text_font=self.font)
        self.ui_elements.append(self.boss_name_display)
        self.boss_hp_base = OnscreenImage(image=join("assets","ui","hp_bar","background.png"), pos=(0,0,0.82), scale=(1,1, 0.05))
        # CHANGING THESE X SCALES NEEDS TO BE UPDATED IN DISPLAY FUNCTION AS WELL
        self.boss_hp_backpaint = OnscreenImage(image=join("assets","ui","hp_bar","hp_back.png"), pos=(0,0,0.82), scale=(0.995,1, 0.045))
        self.boss_hp_display = OnscreenImage(image=join("assets","ui","hp_bar","hp_display.png"), pos=(0,0,0.82), scale=(0.995,1, 0.045))
        self.ui_elements.append(self.boss_hp_base)
        self.ui_elements.append(self.boss_hp_backpaint)
        self.ui_elements.append(self.boss_hp_display)
        