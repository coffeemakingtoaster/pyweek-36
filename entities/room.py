from direct.showbase import DirectObject
from config import MAP_CONSTANTS

class Room(DirectObject.DirectObject):
      
     def __init__(self, entry, exit,id,gridPos):
        self.size = MAP_CONSTANTS.ROOM_SIZE
        self.entry =entry
        self.exit = exit
        self.id = id
        self.gridPos = gridPos
      