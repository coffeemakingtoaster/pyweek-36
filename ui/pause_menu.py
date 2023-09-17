from ui.ui_base import ui_base 
from constants import GAME_STATUS

from direct.gui.DirectGui import DirectButton 

import sys

class pause_menu(ui_base):
    def __init__(self):
        ui_base.__init__(self)

        self.ui_elements = []
        continue_button = DirectButton(text=("Continue"),pos=(0,0,0), scale=0.2, command=self.unpause_game)
        self.ui_elements.append(continue_button)
        main_menu_button = DirectButton(text=("Return to main menu"), pos=(0,0,-0.6), scale=0.2, command=self.goto_main_menu)
        self.ui_elements.append(main_menu_button)


    def unpause_game(self):
        messenger.send('pause_game') 
    
    def goto_main_menu(self):
        print("goto")
        messenger.send('goto_main_menu') 