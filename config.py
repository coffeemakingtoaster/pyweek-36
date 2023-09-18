class GAME_CONSTANTS:
   PLAYER_MOVEMENT_SPEED = 15 
   PLAYER_MAX_HP = 5
   SAMPLE_ENEMY_MAX_HP = 1
   BULLET_SPEED = 40 
   BULLET_MAX_DISTANCE = 30
   
class GAME_CONFIG:
   DEFAULT_WINDOW_HEIGHT = 720 
   DEFAULT_WINDOW_WIDTH = 1280

class GAME_STATUS:
   MAIN_MENU = "main_menu"
   LOADING_LEVEL = "loading_level"
   PAUSED = "paused"
   RUNNING = "running"
   STARTING = "starting"
   SETTINGS = "settings"
   
class MAP_CONSTANTS:
   ROOM_SIZE = 24
   ROOM_HEIGHT = 5
   MAP_LENGTH = 15
   ROOM_TYPES = 3
   
class ENTITY_TEAMS:
   PLAYER = "player"
   ENEMIES = "enemies"
   MAP = "map"