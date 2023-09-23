from direct.showbase import DirectObject
from config import MAP_CONSTANTS, ENTITY_TEAMS
import json
from helpers.model_helpers import load_model
from panda3d.core import BoundingBox, NodePath, PandaNode, ShowBoundsEffect, CollisionBox, CollisionNode, LVector3f, CollisionHandlerEvent, CollisionSphere,CollisionEntry
from panda3d.core import LPoint3
from panda3d.core import *
from entities.spawner import Spawner
from entities.Altar import Altar
from entities.Boss import boss
import math
from direct.actor.Actor import Actor
from os.path import join

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
        self.lights = []
        self.models = []
        self.walls = []
        self.door = None
        self.doorCollider = None
        self.Altar = None
        self.boss = None
        self.collision = None
        self.entered = False
        self.boss = None
        
        self.notifier = CollisionHandlerEvent()
        self.notifier.addInPattern("%fn-into-%in")
        
        self.open_sfx = base.loader.loadSfx(join("assets", "sfx", "door_opening.wav")) 
        
        self.close_sfx = base.loader.loadSfx(join("assets", "sfx", "door_closing.wav"))
        
    def loadRoomAssets(self, id):
        file_path = f'assets/rooms/{id}.json'
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data['assets'] , data['size']
    
    def build(self):
        for asset in self.roomAssets:
            self.buildModel(asset["asset"],(asset["x"],asset["y"],asset["z"]),(asset["rotx"],asset["roty"],asset["rotz"]),asset["collider"],asset["type"],asset["wave"],asset["enemy_type"],asset["scale"])
        
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
    
    def buildModel(self,asset,position,rotation,collision = False,assetType="deko",wave = 0,enemyType = "",scale = 1):
        if assetType != "spawner" and assetType != "altar"  and assetType != "boss":
            #print(assetType)
            #print(self.gridPos)
            #print(self.gridPos-(self.prevRoomLength/2+self.size/2))
            model: NodePath = load_model(asset)
            model.reparentTo(render)
            if assetType == "lightsource":
                plight = PointLight('plight')
                plight.setColor((2, 1.2, 0.6, 1))
                plight.attenuation = (1, 0, 0.05)
                plnp = model.attachNewNode(plight)
                plnp.setPos(-1.5,4,0)
                render.setLight(plnp)
                self.lights.append(plnp)
                #print("no")
        
            model.setPos(position[0],position[1],position[2]+((self.gridPos-(self.prevRoomLength/2+self.size/2))*MAP_CONSTANTS.ROOM_SIZE))
            model.setScale(scale)
            if assetType == "colliding" or assetType == "halfColliding" or assetType == "ground" or assetType == "altar":
                min_point, max_point = model.getTightBounds()
                if assetType == "colliding" or assetType == "ground" or assetType == "altar" :
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
            self.spawners.append(Spawner((position[0],position[1],position[2]+((self.gridPos-(self.prevRoomLength/2+self.size/2))*MAP_CONSTANTS.ROOM_SIZE)),wave,enemyType,self.size,(0,0,((self.gridPos-(self.prevRoomLength/2+self.size/2))*MAP_CONSTANTS.ROOM_SIZE))))
        elif assetType == "altar":
            self.Altar = Altar((position[0],position[1],position[2]+((self.gridPos-(self.prevRoomLength/2+self.size/2))*MAP_CONSTANTS.ROOM_SIZE)))
        elif assetType == "boss":
            self.boss = boss((position[0],position[1],position[2]+((self.gridPos-(self.prevRoomLength/2+self.size/2))*MAP_CONSTANTS.ROOM_SIZE)))
            print("Loaded boss \n\n\n\n\n")
        
           
    def destroy(self):
        for model in self.models:
            if model:
                model.removeNode()
        for spawner in self.spawners:
            spawner.model.removeNode()
        if self.Altar:
            self.Altar.destroy()
            if self.Altar.plnp:
                render.clearLight(self.Altar.plnp)
            self.Altar.model.cleanup()
        if self.boss:
            print("removedBoss")
            if self.boss.plnp:
                self.boss.plnp.removeNode()
            self.boss.model.cleanup()
        
        for light in self.lights:
            render.clearLight(light)
            
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
        max_point.z = wall.getPos().z -2
        
        cp = CollisionBox(min_point - wall.getPos(),max_point - wall.getPos())
        
        min_point, max_point = wall.getTightBounds()
        min_point.y = -10
        max_point.y = 10
        min_point.z = wall.getPos().z +2
        
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
        self.open_sfx.play()
    
    def enter(self):
        print(self.boss)
        self.closeDoor()
        self.collision.removeNode()
        self.entered = True
        
        
    def closeDoor(self):
        self.door.play('Close')
        self.doorHitBox()
        self.close_sfx.play()
        
    def doorHitBox(self):
        min_point, max_point = self.door.getTightBounds()
        min_point.y = -10
        max_point.y = 10
        min_point.x = self.door.getPos().x -3
        max_point.x = self.door.getPos().x +1
        min_point.z = self.door.getPos().z -1
        max_point.z = self.door.getPos().z +1
        cpDoor = CollisionBox(min_point - self.door.getPos(),max_point - self.door.getPos())
        self.doorCollider = self.door.attach_new_node(CollisionNode("wall"))
        #self.doorCollider.show()
        self.doorCollider.node().addSolid(cpDoor)
        self.doorCollider.setTag("team", ENTITY_TEAMS.MAP)
        base.cTrav.addCollider(self.doorCollider, CollisionHandlerEvent())