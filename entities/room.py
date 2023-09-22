from direct.showbase import DirectObject
from config import MAP_CONSTANTS, ENTITY_TEAMS
import json
from helpers.model_helpers import load_model
from panda3d.core import BoundingBox, NodePath, PandaNode, ShowBoundsEffect, CollisionBox, CollisionNode, LVector3f, CollisionHandlerEvent, CollisionSphere,CollisionEntry
from panda3d.core import LPoint3
from panda3d.core import *
from entities.spawner import Spawner
from entities.Altar import Altar
import math
from direct.actor.Actor import Actor

class Room(DirectObject.DirectObject):
      
    def __init__(self, entry, exit,id,gridPos,prevRoomLength):
        self.size = MAP_CONSTANTS.ROOM_SIZE
        self.entry =entry
        self.exit = exit
        self.id = id
        self.gridPos = gridPos
        self.roomAssets , self.size = self.loadRoomAssets(id)
        self.prevRoomLength = prevRoomLength
        self.spawners = []
        self.models = []
        self.walls = []
        self.door = None
        self.doorCollider = None
        self.Altar = None
        self.collision = None
        self.entered = False
        self.boss = None
        
        self.notifier = CollisionHandlerEvent()
        self.notifier.addInPattern("%fn-into-%in")
        
        
        
        
    def loadRoomAssets(self, id):
        file_path = f'assets/rooms/{id}.json'
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data['assets'] , data['size']
    
    def build(self):
        for asset in self.roomAssets:
            self.buildModel(asset["asset"],(asset["x"],asset["y"],asset["z"]),(asset["rotx"],asset["roty"],asset["rotz"]),asset["collider"],asset["type"],asset["wave"],asset["enemy_type"])
        
        if self.size == 1:
            
            self.buildModel("vertWall",(-12,0,0),(0,0,0),True,"colliding")
            self.buildModel("vertWall",(12,0,0),(0,0,0),True,"colliding")
            
        elif self.size ==1.5:
            
            self.buildModel("midWall",(-18,0,0),(0,0,0),True,"colliding")
            self.buildModel("midWall",(18,0,0),(0,0,0),True,"colliding")
            
        elif self.size == 2:
            
            self.buildModel("bigWall",(-24,0,0),(0,0,0),True,"colliding")
            self.buildModel("bigWall",(24,0,0),(0,0,0),True,"colliding")
            
        
        self.addEntryWall()
        
        
        
        return self
    
    def buildModel(self,asset,position,rotation,collision = False,assetType="deko",wave = 0,enemyType = ""):
        if assetType != "spawner" and assetType != "altar" :
            #print(assetType)
            #print(self.gridPos)
            #print(self.gridPos-(self.prevRoomLength/2+self.size/2))
            model: NodePath = load_model(asset)
            model.reparentTo(render)
            if assetType == "lightsource":
                plight = PointLight('plight')
                plight.setColor((2, 1.2, 0.6, 1))
                plight.attenuation = (1, 0, 0.1)
                plnp = model.attachNewNode(plight)
                plnp.setPos(position[0],position[1],position[2]+((self.gridPos-(self.prevRoomLength/2+self.size/2))*MAP_CONSTANTS.ROOM_SIZE))
                render.setLight(plnp)
                print("no")
        
            model.setPos(position[0],position[1],position[2]+((self.gridPos-(self.prevRoomLength/2+self.size/2))*MAP_CONSTANTS.ROOM_SIZE))
            if assetType == "colliding" or assetType == "halfColliding" or assetType == "ground":
                min_point, max_point = model.getTightBounds()
                if assetType == "colliding" or assetType == "ground" :
                    if min_point.y < max_point.y:
                        min_point.y = -10
                        max_point.y = 20
                    elif max_point.y > min_point.y:
                        max_point.y = -10
                        min_point.y = 20
                    if assetType == "ground":
                        max_point.z = max_point.z-3
                else:
                    if min_point.y < max_point.y:
                        min_point.y = -10
                        max_point.y = 0.2
                    elif max_point.y > min_point.y:
                        max_point.y = -10
                        min_point.y = 0.2
                #model.show_tight_bounds()
                cp = CollisionBox(min_point - model.getPos(),max_point - model.getPos())
                
                
                if assetType == "ground":
                    csn = model.attach_new_node(CollisionNode("room"))
                    csn.setTag("team", ENTITY_TEAMS.PLAYER)
                    csn.node().setCollideMask(ENTITY_TEAMS.MELEE_ATTACK_BITMASK)
                    self.collision = csn
                    base.cTrav.addCollider(self.collision, self.notifier)
                    #csn.show()
                else:
                    csn = model.attach_new_node(CollisionNode("wall"))
                    csn.setTag("team", ENTITY_TEAMS.MAP)
                    csn.node().setCollideMask(ENTITY_TEAMS.MAP_BITMASK)
                csn.node().addSolid(cp)
                base.cTrav.addCollider(csn, CollisionHandlerEvent())
                self.models.append(csn)
            
            model.setHpr(rotation[0],rotation[1],rotation[2])
            
            self.models.append(model)
            return model
        elif assetType == "spawner":
            self.spawners.append(Spawner((position[0],position[1],position[2]+((self.gridPos-(self.prevRoomLength/2+self.size/2))*MAP_CONSTANTS.ROOM_SIZE)),wave,enemyType))
        elif assetType == "altar":
            self.Altar = Altar((position[0],position[1],position[2]+((self.gridPos-(self.prevRoomLength/2+self.size/2))*MAP_CONSTANTS.ROOM_SIZE)))
           
    def destroy(self):
        for model in self.models:
            model.removeNode()
        for spawner in self.spawners:
            spawner.model.removeNode()
        if self.Altar:
            self.Altar.destroy()
            if self.Altar.plnp:
                render.clearLight(self.Altar.plnp)
        
    def addEntryWall(self):
        wall = None
        if max(self.size,self.prevRoomLength) == 1:
           wall= self.buildModel("doorWall",(0,0,12*self.size),(0,0,90),True)
        elif max(self.size,self.prevRoomLength) ==1.5:
           wall= self.buildModel("midDoorWall",(0,0,12*self.size),(0,0,90),True)
        elif max(self.size,self.prevRoomLength) == 2:
           wall= self.buildModel("bigDoorWall",(0,0,12*self.size),(0,0,90),True)
        
        wall.setHpr(0,0,0)
        min_point, max_point = wall.getTightBounds()
        #wall.show_tight_bounds()
        min_point.y = -10
        max_point.y = 10
        max_point.z = wall.getPos().z -1
        
        cp = CollisionBox(min_point - wall.getPos(),max_point - wall.getPos())
        
        min_point, max_point = wall.getTightBounds()
        min_point.y = -10
        max_point.y = 10
        min_point.z = wall.getPos().z +1
        
        cp2 = CollisionBox(min_point - wall.getPos(),max_point - wall.getPos())
        
        csn = wall.attach_new_node(CollisionNode("wall"))
        #csn.show()
        csn.setTag("team", ENTITY_TEAMS.MAP)
        csn.node().addSolid(cp)
        csn.node().addSolid(cp2)
        base.cTrav.addCollider(csn, CollisionHandlerEvent())
        wall.setHpr(0,0,90)
        
        self.door = Actor("assets/anims/Door.egg",{"Open":"assets/anims/Door-DoorOpen.egg","Close":"assets/anims/Door-DoorClose.egg"})
        
        
        self.door.play('Close')
        self.door.getChild(0).setR(90)
        self.door.getChild(0).setH(90)
        self.door.getChild(0).setP(0)
        
        self.door.reparentTo(render)
        
        self.door.setPos(0.9,-1,12*self.size+((self.gridPos-(self.prevRoomLength/2+self.size/2))*MAP_CONSTANTS.ROOM_SIZE))
        self.models.append(self.door)
        
        self.doorHitBox()
        
        
        
            
    def openDoor(self):
        self.door.play('Open')
        self.doorCollider.removeNode()
    
    def enter(self):
        self.closeDoor()
        self.collision.removeNode()
        self.entered = True
        
        
    def closeDoor(self):
        self.door.play('Close')
        self.doorHitBox()
        
    def doorHitBox(self):
        min_point, max_point = self.door.getTightBounds()
        min_point.y = -10
        max_point.y = 10
        min_point.x = self.door.getPos().x -2
        min_point.z = self.door.getPos().z -1
        max_point.z = self.door.getPos().z +1
        cpDoor = CollisionBox(min_point - self.door.getPos(),max_point - self.door.getPos())
        self.doorCollider = self.door.attach_new_node(CollisionNode("wall"))
        #self.doorCollider.show()
        self.doorCollider.node().addSolid(cpDoor)
        self.doorCollider.setTag("team", ENTITY_TEAMS.MAP)
        base.cTrav.addCollider(self.doorCollider, CollisionHandlerEvent())