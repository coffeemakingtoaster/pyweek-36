from ui.ui_base import ui_base 
from config import GAME_STATUS
from helpers.utilities import save_config

from direct.gui.DirectGui import DirectButton, OnscreenImage, DirectLabel

import sys
from os.path import join

class main_menu(ui_base):
    def __init__(self):
        ui_base.__init__(self)

        self.ui_elements = []
        
        self.load_background_image()
        
        self.ui_elements.append(DirectLabel(text="Dark", scale=0.25, pos=(-0.5,0,0.7), text_font=self.font, relief=None, text_fg=(255,255,255,1)))
        
        self.ui_elements.append(DirectLabel(text="Matter", scale=0.25, pos=(0,0,0.5), text_font=self.font, relief=None, text_fg=(255,255,255,1)))
        
        self.ui_elements.append(DirectLabel(text="Mage", scale=0.25, pos=(0.3,0,0.3), text_font=self.font, relief=None, text_fg=(255,255,255,1)))
        
        start_button = DirectButton(text=("start"),pos=(0,0,0), scale=0.2, command=self.start_game, text_font=self.font, relief=None)
        self.ui_elements.append(start_button)
        
        settings_button = DirectButton(text=("settings"), pos=(0,0,-0.3),scale=0.2, command=self.open_settings, text_font=self.font, relief=None)
        self.ui_elements.append(settings_button)
        
        quit_button = DirectButton(text=("quit"), pos=(0,0,-0.6), scale=0.2, command=self.quit_game, text_font=self.font, relief=None)
        self.ui_elements.append(quit_button)

    def start_game(self):
        print("Start button pressed")
        # Use global event messenger to start the game
        messenger.send('start_game') 
        
    def open_settings(self):
       messenger.send('toggle_settings') 
       
    def quit_game(self):
        save_config(join("user_config.json"))
        sys.exit()