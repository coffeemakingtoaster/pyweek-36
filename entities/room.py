from direct.showbase import DirectObject
from config import MAP_CONSTANTS, ENTITY_TEAMS
import json
from helpers.model_helpers import load_model
from panda3d.core import BoundingBox, NodePath, PandaNode, ShowBoundsEffect, CollisionBox, CollisionNode, LVector3f, CollisionHandlerEvent, CollisionSphere
from panda3d.core import LPoint3
from panda3d.core import PointLight
from entities.spawner import Spawner

class Room(DirectObject.DirectObject):
      
    def __init__(self, entry, exit,id,gridPos,prevRoomLength):
        self.size = MAP_CONSTANTS.ROOM_SIZE
        self.entry =entry
        self.exit = exit
        self.id = id
        self.gridPos = gridPos
        self.roomAssets , self.size = self.loadRoomAssets(id)
        self.boundingBox = None
        self.prevRoomLength = prevRoomLength
        self.spawners = []
        self.models = []
        self.walls = []
        
        
    def loadRoomAssets(self, id):
        file_path = f'assets/rooms/{id}.json'
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data['assets'] , data['size']
    
    def build(self):
        for asset in self.roomAssets:
            self.buildModel(asset["asset"],(asset["x"],asset["y"],asset["z"]),(asset["rotx"],asset["roty"],asset["rotz"]),asset["collider"],asset["type"],asset["wave"],asset["enemy_type"])
        
        if self.size == 1:
            self.buildModel("doorWall",(0,0,-12),(0,0,90),True)
            self.buildModel("vertWall",(-12,0,0),(0,0,0),True,"colliding")
            self.buildModel("vertWall",(12,0,0),(0,0,0),True,"colliding")
        elif self.size ==1.5:
            self.buildModel("midDoorWall",(0,0,-18),(0,0,90),True)
            self.buildModel("midWall",(-18,0,0),(0,0,0),True,"colliding")
            self.buildModel("midWall",(18,0,0),(0,0,0),True,"colliding")
        elif self.size == 2:
            self.buildModel("bigDoorWall",(0,0,-24),(0,0,90),True)
            self.buildModel("bigWall",(-24,0,0),(0,0,0),True,"colliding")
            self.buildModel("bigWall",(24,0,0),(0,0,0),True,"colliding")
        
        return self
    
    def buildModel(self,asset,position,rotation,collision = False,assetType="deko",wave = 0,enemyType = ""):
        if assetType != "spawner":
            print(assetType)
            print(self.gridPos)
            print(self.gridPos-(self.prevRoomLength/2+self.size/2))
            model: NodePath = load_model(asset)
            model.reparentTo(render)
            if assetType == "lightsource":
                plight = PointLight('plight')
                plight.setColor((2, 1.2, 0.6, 1))
                plight.attenuation = (1, 0, 0.1)
                plnp = render.attachNewNode(plight)
                plnp.setPos(position[0],position[1],position[2]+((self.gridPos-(self.prevRoomLength/2+self.size/2))*MAP_CONSTANTS.ROOM_SIZE))
                render.setLight(plnp)
        
            model.setPos(position[0],position[1],position[2]+((self.gridPos-(self.prevRoomLength/2+self.size/2))*MAP_CONSTANTS.ROOM_SIZE))
            if assetType == "colliding" or assetType == "halfColliding":
                min_point, max_point = model.getTightBounds()
                if assetType == "colliding":
                    if min_point.y < max_point.y:
                        min_point.y = -10
                        max_point.y = 20
                    elif max_point.y > min_point.y:
                        max_point.y = -10
                        min_point.y = 20
                else:
                    if min_point.y < max_point.y:
                        min_point.y = -10
                        max_point.y = 0.2
                    elif max_point.y > min_point.y:
                        max_point.y = -10
                        min_point.y = 0.2
                #model.show_tight_bounds()
                cp = CollisionBox(min_point - model.getPos(),max_point - model.getPos())
                csn = model.attach_new_node(CollisionNode("wall"))
                #csn.show()
                csn.setTag("team", ENTITY_TEAMS.MAP)
                csn.node().addSolid(cp)
                base.cTrav.addCollider(csn, CollisionHandlerEvent())
                self.models.append(csn)
            
            model.setHpr(rotation[0],rotation[1],rotation[2])
            self.models.append(model)
        elif assetType == "spawner":
            self.spawners.append(Spawner((position[0],position[1],position[2]+((self.gridPos-(self.prevRoomLength/2+self.size/2))*MAP_CONSTANTS.ROOM_SIZE)),wave,enemyType))
        
            
    def destroy(self):
        for model in self.models:
            model.removeNode()
        for spawner in self.spawners:
            spawner.model.removeNode()
            
    def addEntryWall(self):
        if self.size == 1:
            self.buildModel("doorWall",(0,0,12),(0,0,90),True)
        elif self.size ==1.5:
            self.buildModel("midDoorWall",(0,0,18),(0,0,90),True)
        elif self.size == 2:
            self.buildModel("bigDoorWall",(0,0,24),(0,0,90),True)
