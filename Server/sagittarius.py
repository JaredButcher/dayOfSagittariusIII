import dataManagement
import threading
import math
import time
import sockServer

class sagGame:
    UPDATE_RATE = 30 #Game updates per second, goal 30 min 10

    def __init__(self, owner, size, ships):
        self.players = []
        self.transforms = []
        self.addPlayer(owner)
        self.live = True
        self.idCounter = 0
        self.gameLoop = threading.Thread(target=self.loop)
        self.gameLoop.start()

    def addPlayer(self, player):
        player.setGame(self, self.getNewId())
        self.players.append(player)

    def addTransform(self, transform):
        transform.setGame(self, getNewId)
        self.transforms.append(transform)

    def rmTransform(self, transform):
        self.transforms.remove(transform)

    def getNewId(self):
        self.idCounter += 1
        return self.idCounter

    def getInfo(self):


    #def recCommand(self, )

    def loop(self):
        timeP = time.perf_counter() 
        while self.live:
            timeC = time.perf_counter()
            delta = timeC - timeP
            if(delta < 1/self.UPDATE_RATE): #Binds it to max updates per second
                continue
            timeP = timeC
            for transform in self.transforms:
                transform.update(delta)

class player:
    def __init__(self, user, team, ships, attack, defense, speed, scout, wepPri, wepSec):
        self.user = user
        self.wepPri = wepPri
        self.wepSec = wepSec
        self.attack = attack
        self.defense = defense
        self.speed = speed
        self.scout = scout
        self.fleets = []
        self.scouts = []
        self.ships = ships
        self.team = team

    def setGame(self, game, id):
        self.game = game
        self.id = id

class transform:
    def __init__(self, game = None, position = 0,0, rotaion = 0, maxSpeed = 0, Traverse = 0):
        self.rot, self.targetRot = rotaion
        self.pos, self.targtPos = position
        self.vel = 0, 0
        self.changeRot, self.changePos = False
        self.maxSpeed = maxSpeed
        self.trav = Traverse
        self.game = game
        self.game.addTransform(self)

    def goTo(self, x,y):
        self.targtPos = x, y
        tempPos = self.targtPos[0] - self.pos[0], self.targtPos[1] - self.pos[1]
        self.vel = ((tempPos[0]^2)/(tempPos[0]^2 + tempPos[1]^2))^.5, ((tempPos[1]^2)/(tempPos[0]^2 + tempPos[1]^2))^.5

    def turnTo(self, rotation):
        self.targetRot = rotation
        self.rotDirection = self.rot - self.targetRot - math.pi

    def update(self, time):
        if(self.rot != self.targetRot):
            self.changeRot = True
            if(self.rotDirection > 0):
                self.rot = self.rot + self.trav * time
            else:
                self.rot = self.rot - self.trav * time
            if((self.rot - self.targetRot + math.pi) * self.trd < 0):
                self.rot = self.targetRot
        if(self.pos != self.targtPos):
            self.changePos = True
            if(self.pos[0] < self.targtPos[0]):
                self.pos[0] = max(self.targtPos[0], self.pos[0] + self.vel[0] * time) 
            else:
                self.pos[0] = min(self.targtPos[0], self.pos[0] + self.vel[0] * time)
            if(self.pos[1] < self.targtPos[1]):
                self.pos[1] = max(self.targtPos[1], self.pos[1] + self.vel[1] * time) 
            else:
                self.pos[1] = min(self.targtPos[1], self.pos[1] + self.vel[1] * time) 

    def getChanges(self):
        out = {}
        out[sockServer.transform.id] = self.id
        out[sockServer.transform.target] = {}
        if(self.changeRot):
            out[sockServer.transform.rotation] = self.rot
            out[sockServer.transform.target][sockServer.transform.rotation] = self.targetRot
        if(self.changePos):
            out[sockServer.transform.position] = {'x': self.pos[0], 'y': self.pos[1]}
            out[sockServer.transform.velocity] = {'x': self.vel[0], 'y': self.vel[1]}
            out[sockServer.transform.target][sockServer.transform.position] = {'x': self.targtPos[0], 'y': self.targtPos[1]}
        self.changePos, self.changeRot = False
        return out

    def destory(self):
        self.game.rmTransform(self)

    def setGame(self, game, id):
        self.game = game
        self.id = id




