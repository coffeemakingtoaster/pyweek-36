from config import MAP_CONSTANTS
from entities.room import Room
from helpers.model_helpers import load_model
import random

class MapLoader:
    
    def __init__(self):
        self.mapLength = MAP_CONSTANTS.MAP_LENGTH
        
    def mapGen(self):
        map = []
        gridPos = (0,0)
        for i in range(self.mapLength):
            if i == 0:
                entry = 1
                exit = entry + random.randint(1,3)
            else:
                entry = self.convert_entry(map[i-1].exit)
                if entry == 1:
                    gridPos = (gridPos[0],gridPos[1]-1)
                    exit = entry + random.randint(1,3)
                elif entry == 2:
                    gridPos = (gridPos[0]+1,gridPos[1])
                    exit = entry + random.randint(1,2)
                else:
                    gridPos = (gridPos[0]-1,gridPos[1])
                    exit = entry - random.randint(1,2)
                
            
            
            
            id = random.randint(1,MAP_CONSTANTS.ROOM_TYPES)
            map.append(Room(entry,exit,id,gridPos))
            
        return map
    
    def loadMap(self,map):
        for room in map:
            self.loadRoom(room)
    
    def loadRoom(self,room):
        room.build()
        return room
        
    def convert_entry(self,number):
        return 3 if number == 1 else 4 if number == 2 else 1 if number == 3 else 2 if number == 4 else number
    
    
    
    def unloadRoom(self,oldRoom,newRoom):
        oldRoom.destroy()
        newRoom.addEntryWall()