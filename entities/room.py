from direct.showbase import DirectObject
from config import MAP_CONSTANTS
import json
from helpers.model_helpers import load_model
from panda3d.core import BoundingBox, NodePath, PandaNode, ShowBoundsEffect, CollisionBox, CollisionNode, LVector3f, CollisionHandlerEvent, CollisionSphere
from panda3d.core import LPoint3

class Room(DirectObject.DirectObject):
      
    def __init__(self, entry, exit,id,gridPos):
        self.size = MAP_CONSTANTS.ROOM_SIZE
        self.entry =entry
        self.exit = exit
        self.id = id
        self.gridPos = gridPos
        self.roomAssets = self.loadRoomAssets(id)
        self.boundingBox = None
        
        self.models = []
        
        #messenger.toggleVerbose()
        
    def loadRoomAssets(self, id):
        file_path = f'assets/rooms/{id}.json'
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data['assets']
    
    def build(self):
        for asset in self.roomAssets:
            model: NodePath =load_model(asset["asset"])
            model.reparentTo(render)
            model.setPos(asset["x"]+self.gridPos[0]*MAP_CONSTANTS.ROOM_SIZE,asset["y"],asset["z"]+self.gridPos[1]*MAP_CONSTANTS.ROOM_SIZE)
            if asset["asset"] != "ground":
                min_point, max_point = model.getTightBounds()
                
                # Extend hitboxes in Y direction
                if min_point.y < max_point.y:
                   min_point.y = -5 
                   max_point.y = 20
                elif max_point.y > min_point.y:
                    max_point.y = -5
                    min_point.y = 20
                
                model.show_tight_bounds()
                cp = CollisionBox(min_point - model.getPos(),max_point - model.getPos())
                csn = model.attach_new_node(CollisionNode("wall"))
                csn.show()
                csn.node().addSolid(cp)
                base.cTrav.addCollider(csn, CollisionHandlerEvent())
                self.models.append(csn)
            self.models.append(model)
        #self.boundingBox = BoundingBox(LPoint3(-MAP_CONSTANTS.ROOM_SIZE/2+self.gridPos[0]*MAP_CONSTANTS.ROOM_SIZE,-MAP_CONSTANTS.ROOM_SIZE/2+self.gridPos[0]*MAP_CONSTANTS.ROOM_SIZE,-MAP_CONSTANTS.ROOM_SIZE/2+self.gridPos[0]*MAP_CONSTANTS.ROOM_SIZE),LPoint3(MAP_CONSTANTS.ROOM_SIZE/2+self.gridPos[0]*MAP_CONSTANTS.ROOM_SIZE,MAP_CONSTANTS.ROOM_SIZE/2+self.gridPos[0]*MAP_CONSTANTS.ROOM_SIZE,MAP_CONSTANTS.ROOM_SIZE/2+self.gridPos[0]*MAP_CONSTANTS.ROOM_SIZE))
        return self
            
    def destroy(self):
        for model in self.models:
            model.removeNode()
