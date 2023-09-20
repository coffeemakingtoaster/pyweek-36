from direct.showbase import DirectObject
from config import MAP_CONSTANTS, ENTITY_TEAMS
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
        self.walls = []
        
    def loadRoomAssets(self, id):
        file_path = f'assets/rooms/{id}.json'
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data['assets']
    
    def build(self):
        for asset in self.roomAssets:
            self.buildModel(asset["asset"],(asset["x"],asset["y"],asset["z"]),(asset["rotx"],asset["roty"],asset["rotz"]),asset["collider"])
        
        for x in range(1,5):
            if x != self.entry:
                if x != self.exit:
                    if x == 1:
                        self.buildModel("vertWall",(0,0,12),(0,0,90),True)
                    elif x == 2:
                        self.buildModel("vertWall",(-12,0,0),(0,0,0),True)
                    elif x == 3:
                        self.buildModel("vertWall",(0,0,-12),(0,0,90),True)
                    elif x == 4:
                        self.buildModel("vertWall",(12,0,0),(0,0,0),True)
                else:
                    if x == 1:
                        self.buildModel("doorWall",(0,0,12),(0,0,90),True)
                    elif x == 2:
                        self.buildModel("doorWall",(-12,0,0),(0,0,0),True)
                    elif x == 3:
                        self.buildModel("doorWall",(0,0,-12),(0,0,90),True)
                    elif x == 4:
                        self.buildModel("doorWall",(12,0,0),(0,0,0),True)
        
        #self.boundingBox = BoundingBox(LPoint3(-MAP_CONSTANTS.ROOM_SIZE/2+self.gridPos[0]*MAP_CONSTANTS.ROOM_SIZE,-MAP_CONSTANTS.ROOM_SIZE/2+self.gridPos[0]*MAP_CONSTANTS.ROOM_SIZE,-MAP_CONSTANTS.ROOM_SIZE/2+self.gridPos[0]*MAP_CONSTANTS.ROOM_SIZE),LPoint3(MAP_CONSTANTS.ROOM_SIZE/2+self.gridPos[0]*MAP_CONSTANTS.ROOM_SIZE,MAP_CONSTANTS.ROOM_SIZE/2+self.gridPos[0]*MAP_CONSTANTS.ROOM_SIZE,MAP_CONSTANTS.ROOM_SIZE/2+self.gridPos[0]*MAP_CONSTANTS.ROOM_SIZE))
        return self
    
    def buildModel(self,asset,position,rotation,collision):
        model: NodePath = load_model(asset)
        model.reparentTo(render)
        model.setPos(position[0]+self.gridPos[0]*MAP_CONSTANTS.ROOM_SIZE,position[1],position[2]+self.gridPos[1]*MAP_CONSTANTS.ROOM_SIZE)
        if collision:
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
            csn.setTag("team", ENTITY_TEAMS.MAP)
            base.cTrav.addCollider(csn, CollisionHandlerEvent())
            self.models.append(csn)
        model.setHpr(rotation[0],rotation[1],rotation[2])
        self.models.append(model)
        
    def destroy(self):
        for model in self.models:
            model.removeNode()
    def addEntryWall(self):
        for x in range(1,5):
            if x == self.entry:
                if x == 1:
                    self.buildModel("doorWall",(0,0,12),(0,0,90),True)
                elif x == 2:
                    self.buildModel("doorWall",(-12,0,0),(0,0,0),True)
                elif x == 3:
                    self.buildModel("doorWall",(0,0,-12),(0,0,90),True)
                elif x == 4:
                    self.buildModel("doorWall",(12,0,0),(0,0,0),True)
