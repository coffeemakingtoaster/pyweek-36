from ui.ui_base import ui_base 
from config import GAME_STATUS, GAME_CONFIG

from panda3d.core import WindowProperties

from direct.gui.DirectGui import DirectButton, DirectCheckButton, DirectSlider
from panda3d.core import DisplayInformation


import sys

class settings_menu(ui_base):
    def __init__(self):
        ui_base.__init__(self)
        
        fullscreen_checkbox = DirectCheckButton(text="Fullscreen", pos=(0,0,0),scale=0.2, command=self.toggle_fullscreen)
        self.ui_elements.append(fullscreen_checkbox)
       
        current_music_volume = base.musicManager.getVolume() 
        self.music_volume_slider = DirectSlider(pageSize=1, range=(0,100), pos=(-0.5,0,-0.3), scale=0.4, value=int(current_music_volume * 100), command=self.update_music_volume)
        self.ui_elements.append(self.music_volume_slider)
        
        current_sfx_volume = base.sfxManagerList[0].getVolume() 
        self.sfx_volume_slider = DirectSlider(pageSize=1, range=(0,100), pos=(0.5,0,-0.3),  scale=0.4, value=int(current_sfx_volume * 100), command=self.update_sfx_volume)
        self.ui_elements.append(self.sfx_volume_slider)
        
        main_menu_button = DirectButton(text=("return to main menu"), pos=(0,0,-0.6), scale=0.2, command=self.return_to_main_menu)
        self.ui_elements.append(main_menu_button)


    def return_to_main_menu(self):
        messenger.send('goto_main_menu') 
        
    def toggle_fullscreen(self, status):
        wp = WindowProperties(base.win.getProperties())  
        is_currently_in_fullscreen = wp.get_fullscreen()
        if status == 1 and not is_currently_in_fullscreen:
            wp.set_fullscreen(True)
            wp.set_size(1920, 1080)
            base.win.requestProperties(wp)
        elif status == 0 and is_currently_in_fullscreen:
            wp.set_fullscreen(False)
            wp.set_size(GAME_CONFIG.DEFAULT_WINDOW_WIDTH, GAME_CONFIG.DEFAULT_WINDOW_HEIGHT)
            # Center window
            wp.set_origin(-2, -2)
            base.win.requestProperties(wp)
            
            
    def update_sfx_volume(self):
        value = self.sfx_volume_slider["value"]
        for manager in base.sfxManagerList:
            manager.setVolume(value/100)
            
    def update_music_volume(self):
        value = self.music_volume_slider["value"]
        base.musicManager.setVolume(value/100)