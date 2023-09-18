from panda3d.core import loadPrcFile

from ui.main_menu import main_menu
from ui.pause_menu import pause_menu
from ui.settings_menu import settings_menu
from ui.hud import game_hud 
from config import GAME_STATUS, GAME_CONSTANTS, GAME_CONFIG
from helpers.utilities import load_config, save_config, lock_mouse_in_window, release_mouse_from_window
from entities.player import player_entity
from entities.sample_enemy import sample_enemy_entity

from panda3d.core import WindowProperties
from panda3d.core import AmbientLight, DirectionalLight, LightAttrib
from panda3d.core import LPoint3, LVector3, BitMask32

from direct.showbase.ShowBase import ShowBase
from direct.task.Task import Task
from direct.gui.OnscreenText import OnscreenText

from os.path import join
from mapGen import MapLoader

# Load panda3d configfile that disables model caching
loadPrcFile("./settings.prc")

class main_game(ShowBase):
    def __init__(self):
        
        ShowBase.__init__(self)
        
        # Set camera position 
        base.cam.setPos(0, -50, 0) 
        self.setupLights()
        
        load_config(join("user_config.json"))

        self.game_status = GAME_STATUS.MAIN_MENU 
        
        self.player = None
        
        self.entities = []

        self.status_display = OnscreenText(text=GAME_STATUS.MAIN_MENU, pos=(0.9,0.9 ), scale=0.07,fg=(255,0,0, 1))

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
        
        base.disableMouse()
        
        
    def game_loop(self, task):
        
        

        dt = self.clock.dt 

        if self.game_status == GAME_STATUS.STARTING:
            print("Starting")
            self.set_game_status(GAME_STATUS.LOADING_LEVEL)
            # Move this to task?
            self.load_game()

        # Do not progress game logic if game is not active
        if self.game_status != GAME_STATUS.RUNNING:
           return Task.cont 
       
        self.player.update(dt)
       
        for entity in self.entities:
           entity.update(dt, self.player.model.getPos())

        return Task.cont
    
    def load_game(self):
        print("Loading game")
        self.active_ui.destroy()
        self.setBackgroundColor((0, 0, 0, 0))
        self.player = player_entity()
        self.active_ui = game_hud(self.player.current_hp)
        self.entities.append(sample_enemy_entity(10,10))
        lock_mouse_in_window()
        mapLoader = MapLoader()
        map = mapLoader.mapGen()
        print(map)
        mapLoader.loadMap(map)
        self.set_game_status(GAME_STATUS.RUNNING)

        
        
        

    def set_game_status(self, status):
        self.status_display["text"] = status
        self.game_status = status

    def toggle_pause(self):
        if self.game_status == GAME_STATUS.RUNNING:
            self.set_game_status(GAME_STATUS.PAUSED)
            # Not needed as of now as gui does not exist 
            self.active_ui.destroy()
            release_mouse_from_window()
            self.active_ui = pause_menu()
        elif self.game_status == GAME_STATUS.PAUSED:
            self.active_ui.destroy()
            self.active_ui = game_hud(self.player.current_hp)
            lock_mouse_in_window() 
            self.set_game_status(GAME_STATUS.RUNNING)

    def goto_to_main_menu(self):
        print("Return to main menu")
        # no hud yet
        if self.active_ui is not None:
            self.active_ui.destroy()
        # delete all entities
        for entity in self.entities:
            entity.destroy()
        if self.player is not None:
            self.player.destroy()
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
     
    def setupLights(self):  
        #ambientLight = AmbientLight("ambientLight")
        #ambientLight.setColor((.8, .8, .8, 1))
        directionalLight = DirectionalLight("directionalLight")
        directionalLight.setDirection(LVector3(0, 45, -45))
        directionalLight.setColor((0.6, 0.6, 0.6, 1))
        render.setLight(render.attachNewNode(directionalLight))
        #render.setLight(render.attachNewNode(ambientLight))
           
def start_game():
    print("Starting game..")
    game = main_game()
    game.run()

if __name__ == "__main__":
    start_game()
    
    