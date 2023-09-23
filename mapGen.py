from config import MAP_CONSTANTS
from entities.room import Room
from helpers.model_helpers import load_model
import random

class MapLoader:
    
    
    def __init__(self):
        self.mapLength = MAP_CONSTANTS.MAP_LENGTH
        
       
        
    def mapGen(self):
        map = []
        mapLength = 0.5
        prevRoomLength = 0
        for i in range(self.mapLength):
            if i == 0:
                id = 7
            elif i == self.mapLength-1:
                id = 100
            elif i%5 == 0:
                id = 101
                
            else:
                id = random.randint(1,MAP_CONSTANTS.ROOM_TYPES)
            
            room = Room(1,3,id,mapLength,prevRoomLength)
            mapLength = mapLength - (prevRoomLength/2 + room.size/2)
            prevRoomLength = room.size
            
            map.append(room)
            
        
        return map
    
    def loadMap(self,map):
        for room in map:
            self.loadRoom(room)
    
    def loadRoom(self,room):
        room.build()
        return room
        
    def convert_entry(self,number):
        return 3 if number == 1 else 4 if number == 2 else 1 if number == 3 else 2 if number == 4 else number
    
    
    
    def unloadRoom(self,oldRoom):
        oldRoom.destroy()
    
    