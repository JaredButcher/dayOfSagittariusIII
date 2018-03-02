import dataManagement
import threading
import math
import time
import sockServer
import html

class gameMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
    def getInfo(self):
        info = {}
        info[sockServer.gameMap.height.value] = self.height
        info[sockServer.gameMap.width.value] = self.width
        return info

class sagConst:
    ships = 15000

class sagGame:
    UPDATE_RATE = 30 #Game updates per second, goal 30 min 10
    def __init__(self, data, id, owner, name, size, damage, points, teams = 2, mode = 1, map=gameMap(1000, 1000)):
        self.dataStor = data
        self.players = []
        self.transforms = []
        self.id = id
        self.map = map
        self.owner = owner
        self.name = name;
        self.maxPlayers = size
        self.shipPoints = points
        self.damage = damage
        self.teams = []
        for i in range(0, min(4, max(2, teams))): self.teams.append(team(i))
        self.mode = mode
        self.winner = None
        self.running = False
        self.idCounter = 0
        self.bind()
        self.gameLoop = threading.Thread(target=self.loop)
    def start(self):
        self.running = True
        self.gameLoop.start()
    def updateBase(self):
        info = {}
        info[sockServer.field.game.value] = {}
        info[sockServer.field.action.value] = sockServer.action.update.value
        return info
    def recCommand(self, command):
        pass
    def addPlayer(self, player):
        if len(self.players) >= self.maxPlayers or self.running: return False
        player.setGame(self, self.getNewId())
        self.players.append(player)
        self.send(player.updateBase(player.getBrowserInfo()))
        return True
    def addUser(self, user):
        return self.addPlayer(player(user))
    def userLeft(self, user):
        if not self.running: #Remove player if game hasn't started, but keep if it has
            player = self.findPlayer(user)
            if player != None:
                player.destory()
        alive = False
        for player in self.players:
            if player.user.getSock() != None and player.user.game == self: 
                alive = True
                break
        if not alive: self.destory()
        self.checkReady()
    def destory(self):
        self.dataStor.sagGames.remove(self)
        self.running = False
        for player in self.players:
            player.user.game = None
            player.destory()
    def addTransform(self, transform):
        self.transforms.append(transform)
        self.game.send(transform.updateBase())
    def rmTransform(self, transform):
        self.transforms.remove(transform)
        send(transform.updateBase({sockServer.transform.destory.value: True}))
    def getNewId(self):
        self.idCounter += 1
        return self.idCounter
    def getInfo(self, browser=False):
        info = {}
        info[sockServer.game.id.value] = self.id
        info[sockServer.game.running.value] = self.running
        if self.winner != None: info[sockServer.game.winner.value] = self.winner
        info[sockServer.game.name.value] = self.name
        info[sockServer.game.owner.value] = self.owner.getName()
        info[sockServer.game.maxPlayers.value] = self.maxPlayers
        info[sockServer.game.damage.value] = self.damage
        info[sockServer.game.shipPoints.value] = self.shipPoints
        info[sockServer.game.mode.value] = self.mode
        info[sockServer.game.teams.value] = len(self.teams)
        info[sockServer.game.map.value] = self.map.getInfo()
        info[sockServer.game.players.value] = []
        for player in self.players:
            if browser:
                info[sockServer.game.players.value].append(player.getBrowserInfo())
            else:
                info[sockServer.game.players.value].append(player.getInfo())
        return info
    def recUpdate(self, user, info):
        sendInfo = False
        if user == self.owner:
            try:
                if sockServer.game.name.value in info:
                    self.name = info[sockServer.game.name.value]
                    sendInfo = True
                if sockServer.game.maxPlayers.value in info:
                    self.maxPlayers = int(info[sockServer.game.maxPlayers.value])
                    sendInfo = True
                if sockServer.game.damage.value in info:
                    self.damage = int(info[sockServer.game.damage.value])
                    sendInfo = True
                if sockServer.game.shipPoints.value in info:
                    self.shipPoints = int(info[sockServer.game.shipPoints.value])
                    sendInfo = True
                if sockServer.game.mode.value in info:
                    self.gameMode = info[sockServer.game.gameMode.value]
                    sendInfo = True
                if sockServer.game.teams.value in info: 
                    sendInfo = True
                    self.teams = []
                    for i in range(0, min(4, max(2, int(info[sockServer.game.teams.value])))): self.teams.append(team(i))
            except (TypeError, ValueError):
                pass
            if sendInfo: 
                self.bind()
                self.send(getInfo(True))
        info = info[sockServer.game.players.value][0]
        player = self.findPlayer(user)
        if player: player.recUpdate(info)
    def findPlayer(self, user):
        for player in self.players:
                if player.user == user: return player
        return None
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
    def send(self, info):
        for player in self.players:
            player.send(info)
    def bind(self):
        if self.name is None or self.name == "":
            self.name = self.owner.getName() + "`s game"
        self.name = self.name[:30]
        if self.maxPlayers is None:
            self.maxPlayers = 6
        self.maxPlayers = min(12, max(2, self.maxPlayers))
        if self.damage is None:
            self.damage = 100
        self.damage = min(10000, max(1, self.damage))
        if self.shipPoints is None:
            self.shipPoints = 200
        self.shipPoints = min(400, max(0, self.shipPoints))
    def checkReady(self):
        if self.running: return
        for player in self.players:
            print(player.ready)
            if player.ready is False: return
        self.running = True
        info = self.updateBase()
        info[sockServer.field.game.value] = self.getInfo(True)
        self.send(info)
        self.gameLoop.start()

class player:
    #TODO Rework scout
    #TODO Add weapons list
    BASE_SPEED = 10
    BASE_TRAV = math.pi / 4
    BASE_SCOUTS = 10
    BASE_RANGE = 100
    BASE_ATTACK = 1
    BASE_DEFENSE = 1
    MOD_SPEED = 5
    MOD_TRAV = math.pi / 50
    MOD_ATTACK = 1
    MOD_DEFENSE = 2/3
    MOD_SCOUTS = 5
    MOD_RANGE = 1
    def __init__(self, user):
        self.user = user
        self.wepPri = None
        self.wepSec = None
        self.wepPriAmmo = 0
        self.wepSecAmmo = 0
        self.attack = 0
        self.defense = 0
        self.speed = 0
        self.scout = 0
        self.gameObjs = []
        self.team = None
        self.ships = sagConst.ships
        self.ready = False
    def setGame(self, game, id):
        self.user.game = game
        self.game = game
        self.id = id
        self.setTeam(self.game.teams[0])
    def send(self, message):
        self.user.getSock().send(message)
    def getUpdate(self, transforms = None):
        out = {}
        out[sockServer.player.ships.value] = self.ships
        out[sockServer.player.gameObj.value] = []
        if transforms != None:
            for transform in transforms:
                out[sockServer.player.gameObj.value].append(transform.getUpdate())
        else:
            for transform in self.gameObjs:
                out[sockServer.player.gameObj.value].append(transform.getUpdate())
        return out
    def clearUpdate(self):
        for transform in self.gameObjs:
            transform.updateInfo = {}
    def update(self, delta):
        for transform in self.gameObjs: transform.update(delta)
    def makeFleet(self, size, pos, rot):
        nFleet = fleet(size, self, self.game.getNewId(), pos, rot, BASE_SPEED + self.speed / MOD_SPEED, BASE_TRAV + math.pi / MOD_TRAV * self.speed, self.game.map)
        self.transform.append(nFleet)
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
        if len(self.scouts) < 10 + math.floor(self.scout / MOD_SCOUTS):
            scout = scout(self, self.game.getNewIdl(), fleet.pos, BASE_SPEED + self.speed / MOD_SPEED, pos, map)
            self.gameObjs.append(scout)
            self.game.addTransform(scout)
            if bound:
                fleet.addScout(scout)
    def rmTransform(self, transform):
        self.game.rmTransform(transform)
        for team in self.game.teams:
            if team != self.team:
                while True:
                    try: team.spoting.remove(transform)
                    except ValueError: break
    def getInfo(self, statsOnly=False):
        info = {}
        info[sockServer.player.id.value] = self.id
        info[sockServer.player.name.value] = self.user.getName()
        if self.team: info[sockServer.player.team.value] = self.team.number
        info[sockServer.player.gameObj.value] = []
        info[sockServer.player.primary.value] = self.wepPri
        info[sockServer.player.primaryAmmo.value] = self.wepPriAmmo
        info[sockServer.player.secondary.value] = self.wepSec
        info[sockServer.player.secondaryAmmo.value] = self.wepSecAmmo
        info[sockServer.player.attack.value] = self.attack
        info[sockServer.player.defense.value] = self.defense
        info[sockServer.player.scout.value] = self.scout
        info[sockServer.player.speed.value] = self.speed
        info[sockServer.player.isFlagship.value] = False
        info[sockServer.player.ready.value] = self.ready
        if not statsOnly:
            for gameObj in self.gameObjs:
                info[sockServer.player.gameObj.value].append(gameObj.getInfo())
        return info;
    def getBrowserInfo(self):
        info = {}
        info[sockServer.player.id.value] = self.id
        info[sockServer.player.name.value] = self.user.getName()
        if self.team: info[sockServer.player.team.value] = self.team.number
        return info
    def updateBase(self, message):
        message[sockServer.player.id.value] = self.id
        info = self.game.updateBase()
        info[sockServer.field.game.value][sockServer.game.players.value] = [message]
        return info
    def setTeam(self, team):
        if self.team: self.team.players.remove(self)
        self.team = team
        team.players.append(self)
        self.game.send(self.updateBase({sockServer.player.team.value: self.team.number}))
    def destory(self):
        self.game.send(self.updateBase({sockServer.player.delete.value: True}))
        self.game.players.remove(self)
        if self.user == self.game.owner and len(self.game.players) > 0:
            self.game.owner = self.game.players[0].user
        if self.team: self.team.players.remove(self)
        self.team = None
        for transform in self.gameObjs:
            transform.destory()
        self.game = None
    def recUpdate(self, info):
        try:
            if self.game.running == False and sockServer.player.team.value in info:
                teamInt = int(info[sockServer.player.team.value])
                for team in self.game.teams:
                    if team.number == teamInt and self.team != team:
                        self.setTeam(team)
            if sockServer.player.attack.value in info:
                player.attack = min(100, int(info[sockServer.player.attack.value]))
                if self.statCount() > self.game.shipPoints:
                    self.attack = max(0, self.attack - (self.statCount - self.game.shipPoints))
            if sockServer.player.defense.value in info:
                player.defense = min(100, int(info[sockServer.player.defense.value]))
                if self.statCount() > self.game.shipPoints:
                    self.defense = max(0, self.defense - (self.statCount - self.game.shipPoints))
            if sockServer.player.speed.value in info:
                player.speed = min(100, int(info[sockServer.player.speed.value]))
                if self.statCount() > self.game.shipPoints:
                    self.speed = max(0, self.speed - (self.statCount - self.game.shipPoints))
            if sockServer.player.scout.value in info:
                player.scout = min(100, int(info[sockServer.player.scout.value]))
                if self.statCount() > self.game.shipPoints:
                    self.scout = max(0, self.scout - (self.statCount - self.game.shipPoints))
            if sockServer.player.primary.value in info:
                player.primary = info[sockServer.player.primary.value]
            if sockServer.player.secondary.value in info:
                player.secondary = info[sockServer.player.secondary.value]
            if sockServer.player.ready.value in info:
                self.ready = info[sockServer.player.ready.value]
                print("Ready")
                self.user.game.checkReady()
        except (TypeError, ValueError):
            pass
        self.statLimit()
        self.game.send(self.updateBase(self.getInfo(True)))
    def statCount(self):
        return self.attack + self.defense + self.speed + self.scout
    def statLimit(self):
        if self.statCount() > self.game.shipPoints:
            self.attack = 0
            self.defense = 0
            self.speed = 0
            self.scout = 0

class transform: #Base class for all gameobjects
    def __init__(self, player, id, position, rotaion, speed, traverse, map):
        self.rot = rotaion
        self.targetRot = rotaion
        self.pos = position
        self.targtPos = position
        self.vel = 0, 0
        self.rVel = 0
        self.changeRot = False
        self.changePos = False
        self.speed = speed
        self.trav = traverse
        self.player = player
        self.id = id
        self.map = map
        self.spoting = []
        self.spoted = []
        self.viewing = False
        self.moveTurning = False
        self.updateInfo = {}
    def goTo(self, target, turn=True):
        self.targtPos[0] = min(self.map.width, max(0, target[0]))
        self.targtPos[1] = min(self.map.height, max(0, target[1]))
        adTarg = target[0] - self.pos[0], target[1] - self.pos[1]
        distance = (adTarg[0]^2 + adTarg[1]^2)^.5
        unitTarg = adTarg[0] / distance, adTarg[1] / distance
        direction = (math.acos(unitTarg[0]) if unitTarg > 0 else 2 * math.pi - math.acos(unitTarg[0])) % (2 * math.pi)
        if direction == self.rot:
            vel = self.speed
        else:
            vel = self.speed / 2
            if turn: 
                self.turnTo(direction, True)
                self.moveTurning = True
        self.vel = adTarg[0] / vel, adTarg[1] / vel
        self.send(self.updateBase(sendPos = True))
    def turnTo(self, rotation, noSend=False):
        self.targetRot = rotation
        self.rVel = self.trav * (1 if self.rot > math.pi * 2 - self.rot else -1)
        self.moveTurning = False
        if not noSend: self.send(self.updateBase(sendPos = True))
    def update(self, time):
        self.spottingComputed = False
        if(self.rot != self.targetRot):
            self.updateInfo = {}
            self.changeRot = True
            self.rot = (self.rot + self.rVel * time) % (math.pi * 2)
            if min(self.rot, math.pi * 2 - self.rot) < abs(self.rVel): #Check if it overshot
                self.rot = self.targetRot
                self.rVel = 0
        elif self.moveTurning:
            self.vel[0] *= 2
            self.vel[1] *= 2
            self.moveTurning = False
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
        else:
            self.vel = 0,0
    def destory(self):
        if self.player != None: self.player.rmTransform(self)
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
        return ((self.pos[0] - transform.pos[0])^2 + (self.pos[1] - transform.pos[1])^2)^.5 <= player.BASE_RANGE + self.player.scout * player.MOD_RANGE
    def computeSpotting(self, transform=None):
        if self.viewing:
            if transform is None:
                for team in player.game.teams:
                    if team != player.team:
                        for player in team.players:
                            for transform in player.gameObjs:
                                spot = inSpotingRange(transform)
                                if spot and not transform in self.spoting:
                                    self.addSpot(transform)
                                    transform.computeSpotting(self)
                                elif not spot and transform in self.spoting:
                                    self.rmSpot(transform)
                                    transform.computeSpotting(self)
                                elif transform in self.spoted:
                                    transform.computeSpotting(self)
            else:
                spot = inSpotingRange(transform)
                if spot and not transform in self.spoting:
                    self.addSpot(transform)
                elif not spot and transform in self.spoting:
                    self.rmSpot(transform)
    def addSpot(transform):
        self.spoting.append(transform)
        transform.spoted.append(self)
        if not transform in self.player.team.spoting:
            self.player.team.send(self.updateBase(sendPos = True))
        self.player.team.spoting.append(transform)
    def rmSpot(transform):
        self.spoting.remove(transform)
        transform.spoted.remove(self)
        self.player.team.spoting.remove(transform)
        if not transform in self.player.team.spoting:
            message = {}
            message[sockServer.transform.hide.value] = True
            self.player.team.send(self.updateBase(message))
    def updateBase(self, message = {}, sendPos = False):
        message[sockServer.transform.id.value] = self.id
        if sendPos:
            message[sockServer.transform.pos.value] = {'x': self.pos[0], 'y': self.pos[1]}
            message[sockServer.transform.rot.value] = self.rot
            if self.pos != self.targtPos: message[sockServer.transform.targtPos.value] = {'x': self.targtPos[0], 'y': self.targtPos[1]}
            if self.rot != self.targetRot: message[sockServer.transform.targetRot.value] = self.targetRot
        info = player.updateBase()
        info[sockServer.field.game.value][sockServer.game.players.value][0][sockServer.player.gameObj.value] = [message]
        return info
    def send(self, info):
        self.player.team.send(info)
        for team in self.player.game.teams:
            if team != self.player.team:
                if self in team.spoting:
                    team.send(info)

class fleet(transform):
    def __init__(self, size, player, id, position, rotaion, speed, traverse, map):
        super().__init__(player, id, position, rot, speed, traverse, map)
        self.size = size
        self.scouts = []
        self.merging = None
        self.viewing = True
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
        out[sockServer.gameObj.size.value] = self.size
        out[sockServer.gameObj.type.value] = sockServer.objType.fleet.value
        out[sockServer.gameObj.transform.value] = super().getUpdate
        return out
    def updateBase(self, message = {sockServer.gameObj.transform.value: {}}, sendPos = False):
        if message[sockServer.gameObj.transform.value] is None:
            message[sockServer.gameObj.transform.value] = {}
        message[sockServer.gameObj.transform.value] = super.updateBase(message[sockServer.gameObj.transform.value], sendPos)
        info = player.updateBase()
        info[sockServer.field.game.value][sockServer.game.players.value][0][sockServer.player.gameObj.value] = [message]
        return info

class scout(transform):
    def __init__(self, player, id, position, speed, map, destination):
        #TODO desnitaion stuff
        super().__init__(player, id, pos, 0, speed, 0, map)
    def getUpdate(self):
        out = {}
        out[sockServer.gameObj.type.value] = sockServer.objType.scout.value if self.viewing else sockServer.objType.scoutMove.value
        out[sockServer.gameObj.transform.value] = super().getUpdate
        return out

class team:
    def __init__(self, number):
        self.number = number
        self.players = []
        self.spoting = []
    def send(self, message):
        for player in players:
            player.send(message)

