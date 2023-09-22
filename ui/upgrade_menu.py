from ui.ui_base import ui_base 
from config import GAME_STATUS

from direct.gui.DirectGui import DirectButton, OnscreenImage

import sys

from os.path import join

class upgrade_menu(ui_base):
    def __init__(self):
        ui_base.__init__(self)
        self.ui_elements = []
        
        img = OnscreenImage(image=join("assets","icons","hud","backplane.png"), pos=(0,0,0), scale=10)
        img.setTransparency(1, 0)
        img.setAlphaScale(0.5) 
        self.ui_elements.append(img)

        continue_button = DirectButton(text=("Speed"),pos=(0,0,0), scale=0.2, command=self.speed, text_font=self.font)
        self.ui_elements.append(continue_button)
        
        main_menu_button = DirectButton(text=("Health"), pos=(0,0,-0.6), scale=0.2, command=self.health, text_font=self.font)
        self.ui_elements.append(main_menu_button)

    def speed(self):
        messenger.send('upgradeSpeed')
        messenger.send('pause_game')
    
    def health(self):
        messenger.send('upgradeHealth')
        messenger.send('pause_game')
        
    def damage(self):
        messenger.send('upgradeDamage')
        messenger.send('pause_game')