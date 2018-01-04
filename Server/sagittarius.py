import dataManagement
import threading
import math
import time
import sockServer

sign = lambda x: x and (1, -1)[x < 0]

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
        self.teams = []
        for i in range(0, teams): self.teams.append(team(i))
        self.mode = mode
        self.winner = None
        self.running = False
        self.idCounter = 0
        self.gameLoop = threading.Thread(target=self.loop)
    def start(self):
        self.running = True
        self.gameLoop.start()
    def recCommand(self, command):
        pass
    def addPlayer(self, player):
        player.setGame(self, self.getNewId())
        self.players.append(player)
    def addUser(self, user):
        self.addPlayer(player(user, self.teams[0], self.fleetSize))
    def rmPlayer(self, player):
        self.players.remove(player)
    def addTransform(self, transform):
        self.transforms.append(transform)
    def rmTransform(self, transform):
        self.transforms.remove(transform)
    def getNewId(self):
        self.idCounter += 1
        return self.idCounter
    def getInfo(self, browser = False):
        info = {}
        info[sockServer.game.id.value] = self.id
        info[sockServer.game.owner.value] = self.owner.getName()
        info[sockServer.game.name.value] = self.name
        info[sockServer.game.maxPlayers.value] = self.maxPlayers
        info[sockServer.game.fleetSize.value] = self.fleetSize
        info[sockServer.game.fleetPoints.value] = self.points
        info[sockServer.game.gameMode.value] = self.mode
        info[sockServer.game.teams.value] = len(self.teams)
        info[sockServer.game.players.value] = len(self.players)
        if self.winner: info[sockServer.game.winner.value] = self.winner
        info[sockServer.game.running.value] = self.running
        info[sockServer.game.players.value] = []
        for player in self.players:
            if browser:
                info[sockServer.game.players.value].append(player.getBrowserInfo())
            else:
                info[sockServer.game.players.value].append(player.getInfo())
        return info
    def loop(self):
        timeP = time.perf_counter() 
        while self.running:
            timeC = time.perf_counter()
            delta = timeC - timeP
            if(delta < 1/self.UPDATE_RATE): continue #Binds it to max updates per second
            timeP = timeC
            for player in self.players: player.update(delta)
            for transform in self.transforms: 
                if transform.changePos: transform.computeSpotting()
            for team in self.teams:
                team.sendUpdate()

class player:
    BASE_SPEED = 10
    BASE_TRAV = math.pi / 4
    BASE_SCOUTS = 10
    BASE_RANGE = 100
    BASE_ATTACK = 1
    BASE_DEFENSE = 1
    def __init__(self, user, team, ships, attack = 0, defense = 0, speed = 0, scout = 0, wepPri = 0, wepSec = 0):
        self.user = user
        self.wepPri = wepPri
        self.wepSec = wepSec
        self.wepPriAmmo = 0
        self.wepSecAmmo = 0
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
    def send(self, message):
        self.user.getSock().send(message)
    def getUpdate(self, transforms = None):
        out = {}
        out[sockServer.player.ships.value] = self.ships
        out[sockServer.player.fleets.value] = []
        out[sockServer.player.scouts.value] = []
        if transforms != None:
            for transform in transforms:
                if type(transform) is fleet:
                    out[sockServer.player.fleets.value].append(transform.getUpdate())
                else:
                    out[sockServer.player.scouts.value].append(transform.getUpdate())
        else:
            for fleet in self.fleets:
                out[sockServer.player.fleets.value].append(fleet.getUpdate())
            for scout in self.scouts:
                out[sockServer.player.scouts.value].append(scout.getUpdate())
        return out
    def clearUpdate(self):
        for fleet in self.fleets:
            fleet.updateInfo = {}
        for scout in self.scouts:
            scout.updateInfo = {}
    def update(self, delta):
        for fleet in self.fleets: fleet.update(delta)
        for scout in self.scouts: scout.update(delta)
    def makeFleet(self, size, pos, rot):
        nFleet = fleet(size, self, self.game.getNewId(), pos, rot, BASE_SPEED + self.speed / 10, BASE_TRAV + math.pi / 25 * self.speed)
        self.fleets.append(nFleet)
        self.game.addTransform(nFleet)
        return nFleet
    def makeSubFleet(self, pFleet, size):
        if(size < fleet.size):
            cFleet = self.makeFleet(size, pFleet.pos, pFleet.rot)
            pFleet.size -= size
            cFleet.goTo(math.sin(cFleet.pos[0]) * 10, math.cos(cFleet.pos[0]) * 10)
    def mergeFleet(self, fleets):
        min = fleets[0].pos
        max = fleets[0].pos
        for fleet in fleets:
            if fleet.pos[0] < min[0]: min[0] = fleet.pos[0]
            elif fleet.pos[0] > max[0]: max[0] = fleet.pos[0]
            if fleet.pos[1] < min[1]: min[1] = fleet.pos[1]
            elif fleet.pos[1] < max[1]: max[1] = fleet.pos[1]
        point = min[0] + (max[0] - min[0]) / 2, min[1] + (max[1] - min[1]) / 2
        for fleet in fleets:
            fleet.startMerge(point)   
    def makeScout(self, fleet, bound, pos):
        if len(self.scouts) < 10 + math.floor(self.scout / 5):
            scout = transform(self, self.game.getNewIdl(), fleet.pos, 0, scout)
            if bound:
                fleet.addScout(scout)
    def rmTransform(self, transform):
        self.game.rmTransform(transform)
        for team in game.teams:
            if team == self.team: continue
            for spot in team.spotedEnemies:
                if spot.player == self:
                    while True:
                        try: spot.transforms.remove(transform)
                        except ValueError: break
        try: self.fleets.remove[transform]
        except ValueError:
            try:
                self.scouts.remove[transform]
                for fleet in fleets:
                    fleet.rmScout(transform)
            except ValueError: pass
    def getInfo(self):
        info = {}
        info[sockServer.player.id.value] = self.id
        info[sockServer.player.name.value] = self.user.getName()
        info[sockServer.player.team.value] = self.team.number
        info[sockServer.player.fleets.value] = []
        info[sockServer.player.scouts.value] = []
        info[sockServer.player.primary.value] = self.wepPri
        info[sockServer.player.primaryAmmo.value] = self.wepPriAmmo
        info[sockServer.player.secondary.value] = self.wepSec
        info[sockServer.player.secondaryAmmo.value] = self.wepSecAmmo
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
    def getBrowserInfo(self):
        info = {}
        info[sockServer.player.id.value] = self.id
        info[sockServer.player.name.value] = self.user.getName()
        info[sockServer.player.team.value] = self.team.number
        return info

class transform: #Base class for all gameobjects
    def __init__(self, player, id, position, rotaion, speed, traverse):
        self.rot, self.targetRot = rotaion
        self.pos, self.targtPos = position
        self.vel = 0, 0
        self.rVel = 0
        self.changeRot = False
        self.changePos = False
        self.speed = speed
        self.trav = traverse
        self.player = player
        self.id = id
        self.spoting = []
        self.spoted = []
        self.spotingComputed = False
        self.updateInfo = {}
    def goTo(self, target): #TODO bind to play field
        self.targtPos = target
        adTarg = target[0] - self.pos[0], target[1] - self.pos[1]
        vel = (adTarg[0]^2 + adTarg[1]^2)^.5 / self.speed
        self.vel = adTarg[0] / vel, adTarg[1] / vel
    def turnTo(self, rotation):
        self.targetRot = rotation
        self.rVel = self.trav * sign(self.rot - self.targetRot - math.pi)
    def update(self, time):
        self.spottingComputed = False
        if(self.rot != self.targetRot):
            self.updateInfo = {}
            self.changeRot = True
            self.rot = self.rot + self.rVel * time
            if(sign(self.rot - self.targetRot - math.pi) != sign(self.rVel)):
                self.rot = self.targetRot
        if(self.pos != self.targtPos):
            self.updateInfo = {}
            self.changePos = True
            if(self.pos[0] < self.targtPos[0]):
                self.pos[0] = max(self.targtPos[0], self.pos[0] + self.vel[0] * time) 
            else:
                self.pos[0] = min(self.targtPos[0], self.pos[0] + self.vel[0] * time)
            if(self.pos[1] < self.targtPos[1]):
                self.pos[1] = max(self.targtPos[1], self.pos[1] + self.vel[1] * time) 
            else:
                self.pos[1] = min(self.targtPos[1], self.pos[1] + self.vel[1] * time) 
    def getUpdate(self):
        if self.updateInfo != {}: return self.updateInfo
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
        self.player.rmTransform(self)
        for transform in self.spoted:
            transform.spoting.remove(self)
        for transform in self.spoting:
            transform.spoted.remove(self)
    def getInfo(self):
        info = {}
        info[sockServer.transform.id.value] = self.id
        info[sockServer.transform.position.value] = {'x': self.pos[0], 'y': self.pos[1]}
        info[sockServer.transform.rotation.value] = self.rot
        info[sockServer.transform.velocity.value] = {'x': self.vel[0], 'y': self.vel[1]}
        info[sockServer.transform.rVelocity.value] = self.rVel
    def inSpotingRange(self, transform):
        return ((self.pos[0] - transform.pos[0])^2 + (self.pos[1] - transform.pos[1])^2)^.5 <= self.player.BASE_RANGE + self.player.scout
    def computeSpotting(self):
        if not self.spotingComputed:
            self.spotingComputed = True
            for spotedEnemy in self.player.team.spotedEnemies:
                for transform in spotedEnemy.player.fleets + spotedEnemy.player.scouts:
                    spoted = self.inSpotingRange(transform)
                    if transform in self.spoting and not spoted:
                        self.spoting.remove(transform)
                        transform.spoted.remove(self)
                        transform.computeSpotting()
                        spotedEnemy.transforms.remove(transform)
                    elif spoted:
                        self.spoting.append(transform)
                        transform.spoted.append(self)
                        transform.computeSpotting()
                        spotedEnemy.transforms.append(transform)

class fleet(transform):
    def __init__(self, size, player, id, position = 0, rotaion = 0, speed = 0, traverse = 0):
        self.size = size
        self.scouts = []
        self.merging = None
        super().__init__(game, pos, rot, maxSpeed, trav)
    def goTo(target):
        self.merging = None
        super().goTo(pos)
        if len(self.scouts) > 0:
            normTarg = target[0] - self.pos[0], target[1] - self.pos[1]
            for scout in self.scouts:
                scout.goTo(scout.pos[0] + normTarg[0], scout.pos[1] + normTarg[1])
    def addScout(self, scout):
        self.scouts.append(scout)
    def rmScout(self, scout):
        try:
            self.scouts.remove(scout)
        except ValueError:
            pass
    def startMerge(self, fleets, pos):
        goTo(pos)
        self.merging = fleets
    def update(self, time):
        if self.merging != None and self.pos == self.targetPos:
            for fleet in self.merging:
                if fleet.pos == self.pos and fleet.merging != None:
                    fleet.destory()
                    self.destory()
                    nfleet = player.makeFleet(fleet.size + self.size, self.pos, self.rot)
                    nfleet.scouts = self.scouts + fleet.scouts
        super().update(time)
    def getUpdate(self):
        out = {}
        out[sockServer.fleet.size.value] = self.size
        out[sockServer.fleet.transform.value] = super().getUpdate
        return out

class team:
    def __init__(self, number):
        self.number = number
        self.players = []
        self.spotedEnemies = []
    def sendUpdate(self):
        info = {}
        info[sockServer.field.action.value] = sockServer.action.update.value
        info[sockServer.field.game.value] = {}
        info[sockServer.field.game.value][sockServer.game.players.value] = []
        for player in self.players:
            info[sockServer.field.game.value][sockServer.game.players.value].append(player.getUpdate())
        for spot in self.spotedEnemies:
            info[sockServer.field.game.value][sockServer.game.players.value].append(spot.player.getUpdate(set(spot.transforms)))
        for player in self.players:
            player.send(info)

class spotedEnemy:
    def __init__(self, player):
        self.player = player
        self.transforms = []
