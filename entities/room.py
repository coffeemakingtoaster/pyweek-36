from direct.showbase import DirectObject
from config import MAP_CONSTANTS
import json
from helpers.model_helpers import load_model

class Room(DirectObject.DirectObject):
      
    def __init__(self, entry, exit,id,gridPos):
        self.size = MAP_CONSTANTS.ROOM_SIZE
        self.entry =entry
        self.exit = exit
        self.id = id
        self.gridPos = gridPos
        self.roomAssets = self.loadRoomAssets(id)
        
        self.models = []
        
    def loadRoomAssets(self, id):
        file_path = f'assets/rooms/{id}.json'
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data['assets']
    
    def build(self):
        for asset in self.roomAssets:
            model=load_model(asset["asset"])
            model.reparentTo(render)
            model.setPos(asset["x"]+self.gridPos[0]*MAP_CONSTANTS.ROOM_SIZE,asset["y"],asset["z"]+self.gridPos[1]*MAP_CONSTANTS.ROOM_SIZE)
    
            self.models.append(model)
        return self
            
    def destroy(self):
        for model in self.models:
            model.removeNode()
