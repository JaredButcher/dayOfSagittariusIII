import dataManagement
import threading
import math
import time
import sockServer

class sagGame:
    UPDATE_RATE = 30 #Game updates per second, goal 30 min 10

    def __init__(self, id, owner, name, size, ships, points, teams = 2, mode = 1):
        self.players = []
        self.transforms = []
        self.id = id
        self.owner = owner
        self.name = name;
        self.maxPlayers = size
        self.fleetSize = ships
        self.points = points
        self.teams = teams
        self.mode = mode
        self.live = True
        self.idCounter = 0
        self.gameLoop = threading.Thread(target=self.loop)
        self.gameLoop.start()

    def addPlayer(self, player):
        player.setGame(self, self.getNewId())
        self.players.append(player)

    def rmPlayer(self, player):
        self.players.remove(player)

    def addTransform(self, transform):
        transform.setGame(self, self.getNewId())
        self.transforms.append(transform)

    def rmTransform(self, transform):
        self.transforms.remove(transform)

    def getNewId(self):
        self.idCounter += 1
        return self.idCounter

    def getInfo(self):
        info = {}
        info[sockServer.browser.id.value] = self.id
        info[sockServer.browser.owner.value] = self.owner.getName()
        info[sockServer.browser.name.value] = self.name
        info[sockServer.browser.maxPlayers.value] = self.maxPlayers
        info[sockServer.browser.fleetSize.value] = self.fleetSize
        info[sockServer.browser.fleetPoints.value] = self.points
        info[sockServer.browser.gameMode.value] = self.mode
        info[sockServer.browser.teams.value] = self.teams
        info[sockServer.browser.players.value] = len(self.players)
        return info;

    def getGameInfo(self):
        pass
        '''
        for player in self.players:
            info[sockServer.browser.players.value].append(player.getInfo())
            '''

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

    def getInfo(self):
        info = {}
        info[sockServer.player.id.value] = self.id
        info[sockServer.player.name.value] = self.user.getName()
        info[sockServer.player.team.value] = self.team
        info[sockServer.player.fleets.value] = []
        info[sockServer.player.scouts.value] = []
        info[sockServer.player.primary.value] = self.wepPri
        info[sockServer.player.primaryAmmo.value] = None
        info[sockServer.player.secondary.value] = self.wepSec
        info[sockServer.player.secondaryAmmo.value] = None
        info[sockServer.player.attack.value] = self.attack
        info[sockServer.player.defense.value] = self.defense
        info[sockServer.player.scout.value] = self.scout
        info[sockServer.player.speed.value] = self.speed
        info[sockServer.player.isFlagship.value] = False
        for fleet in self.fleets:
            fInfo = {}
            fInfo[sockServer.fleet.size.value] = fleet.size
            fInfo[sockServer.fleet.transform.value] = fleet.transform.getInfo()
            info[sockServer.player.fleets.value].append(fInfo)
        for scout in self.scouts:
            info[sockServer.player.scouts.value].append(scout.transform.getInfo())
        return info;

class transform: #Base class for all gameobjects
    def __init__(self, game = None, position = 0, rotaion = 0, speed = 0, traverse = 0):
        self.rot, self.targetRot = rotaion
        self.pos, self.targtPos = position
        self.vel = 0, 0
        self.rVel = 0
        self.changeRot = False
        self.changePos = False
        self.speed = speed
        self.trav = traverse
        self.game = game
        self.game.addTransform(self)

    def goTo(self, target):
        self.targtPos = target
        adTarg = target[0] - self.pos[0], target[1] - self.pos[1]
        vel = (adTarg[0]^2 + adTarg[1]^2)^.5 / self.speed
        self.vel = adTarg[0] / vel, adTarg[1] / vel

    def turnTo(self, rotation):
        self.targetRot = rotation
        self.rVel = self.trav * sign(self.rot - self.targetRot - math.pi)

    def update(self, time):
        if(self.rot != self.targetRot):
            self.changeRot = True
            self.rot = self.rot + self.rVel * time
            if(sign(self.rot - self.targetRot - math.pi) != sign(self.rVel)):
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
        out[sockServer.transform.id.value] = self.id
        out[sockServer.transform.target.value] = {}
        if(self.changeRot):
            out[sockServer.transform.rotation.value] = self.rot
            out[sockServer.transform.rVelocity.value]= self.rVel
            self.changeRot = False
        if(self.changePos):
            out[sockServer.transform.position.value] = {'x': self.pos[0], 'y': self.pos[1]}
            out[sockServer.transform.velocity.value] = {'x': self.vel[0], 'y': self.vel[1]}
            self.changePos = False
        return out

    def destory(self):
        self.game.rmTransform(self)

    def setGame(self, game, id):
        self.game = game
        self.id = id

    def getGame():
        return self.game

    def getInfo(self):
        info = {}
        info[sockServer.transform.id.value] = self.id
        info[sockServer.transform.position.value] = {'x': self.pos[0], 'y': self.pos[1]}
        info[sockServer.transform.rotation.value] = self.rot
        info[sockServer.transform.velocity.value] = {'x': self.vel[0], 'y': self.vel[1]}
        info[sockServer.transform.rVelocity.value] = self.rVel

class fleet:
    def __init__(self, size, transform):
        self.transform = (transform.game, transform.pos, transform.rot, transform.maxSpeed, transform.trav)

sign = lambda x: x and (1, -1)[x < 0]
