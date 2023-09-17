from ui.ui_base import ui_base 
from constants import GAME_STATUS

from direct.gui.DirectGui import DirectButton 

import sys

class main_menu(ui_base):
    def __init__(self):
        ui_base.__init__(self)

        self.ui_elements = []
        start_button = DirectButton(text=("start"),pos=(0,0,0), scale=0.2, command=self.start_game)
        self.ui_elements.append(start_button)
        quit_button = DirectButton(text=("quit"), pos=(0,0,-0.6), scale=0.2, command=sys.exit)
        self.ui_elements.append(quit_button)


    def start_game(self):
        print("Start button pressed")
        # Use global event messenger to start the game
        messenger.send('start_game') 