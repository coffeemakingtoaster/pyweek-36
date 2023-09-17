from panda3d.core import loadPrcFile

from ui.main_menu import main_menu
from ui.pause_menu import pause_menu
from ui.settings_menu import settings_menu
from config import GAME_STATUS, GAME_CONSTANTS, GAME_CONFIG
from helpers.utilities import load_config, save_config

from panda3d.core import WindowProperties

from direct.showbase.ShowBase import ShowBase
from direct.task.Task import Task
from direct.gui.OnscreenText import OnscreenText

from os.path import join

# Load panda3d configfile that disables model caching
loadPrcFile("./settings.prc")

class main_game(ShowBase):
    def __init__(self):
        
        ShowBase.__init__(self)
        
        load_config(join("user_config.json"))

        self.game_status = GAME_STATUS.MAIN_MENU 

        self.status_display = OnscreenText(text=GAME_STATUS.MAIN_MENU, pos=(0.9,0.9 ), scale=0.07,fg=(255,0,0, 1))
        
        # Set value high to instantly trigger update 
        self.ticks_since_last_fps_update = 1000

        self.active_ui = None 
        self.goto_to_main_menu()

        # Create event handlers for events fired by UI
        self.accept("start_game", self.set_game_status, [GAME_STATUS.STARTING])

        # Create event handlers for events fired by keyboard
        self.accept("escape", self.toggle_pause)
        self.accept("pause_game", self.toggle_pause)

        self.accept("goto_main_menu", self.goto_to_main_menu)
        self.accept("toggle_settings", self.toggle_settings)

        self.gameTask = base.taskMgr.add(self.game_loop, "gameLoop")
        
        # Load music
        background_music = base.loader.loadMusic(join("assets", "music", "music.mp3")) 
        background_music.setLoop(True)
        background_music.play()
        
    def game_loop(self, task):

        dt = self.clock.dt 

        if self.game_status == GAME_STATUS.STARTING:
            print("Starting")
            self.set_game_status(GAME_STATUS.LOADING_LEVEL)
            # Move this to task?
            self.load_game()

        # Do not progress game logic if game is not active
        if self.game_status == GAME_STATUS.RUNNING:
           return Task.cont 

        return Task.cont
    
    def load_game(self):
        print("Loading game")
        self.active_ui.destroy()
        self.setBackgroundColor((0, 0, 0, 0))
        self.set_game_status(GAME_STATUS.RUNNING)

    def set_game_status(self, status):
        self.status_display["text"] = status
        self.game_status = status

    def toggle_pause(self):
        if self.game_status == GAME_STATUS.RUNNING:
            self.set_game_status(GAME_STATUS.PAUSED)
            # Not needed as of now as gui does not exist 
            #self.active_ui.destroy()
            self.active_ui = pause_menu()
        elif self.game_status == GAME_STATUS.PAUSED:
            self.active_ui.destroy()
            #self.active_ui = hud
            self.set_game_status(GAME_STATUS.RUNNING)

    def goto_to_main_menu(self):
        print("Return to main menu")
        # no hud yet
        if self.active_ui is not None:
            self.active_ui.destroy()
        self.active_ui = main_menu()
        self.setBackgroundColor((1, 1, 1, 1))
        self.set_game_status(GAME_STATUS.MAIN_MENU)
        
        
    def toggle_settings(self):
        if self.game_status == GAME_STATUS.MAIN_MENU:
            self.active_ui.destroy()
            self.active_ui = settings_menu()
            self.set_game_status(GAME_STATUS.SETTINGS)
        elif self.game_status == GAME_STATUS.SETTINGS:
            self.active_ui.destroy()
            self.active_ui = main_menu() 
            self.set_game_status(GAME_STATUS.MAIN_MENU)
            
        
def start_game():
    print("Starting game..")
    game = main_game()
    game.run()

if __name__ == "__main__":
    start_game()