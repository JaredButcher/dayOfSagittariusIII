import dataManagement
import threading
import math
import time
import sockServer

class gameMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
    def getInfo(self):
        info = {}
        info[sockServer.gameMap.height.value] = self.height
        info[sockServer.gameMap.width.value] = self.width
        return info

class sagGame:
    UPDATE_RATE = 30 #Game updates per second, goal 30 min 10
    def __init__(self, data, id, owner, name, size, ships, points, teams = 2, mode = 1, map=gameMap(1000, 1000)):
        self.dataStor = data
        self.players = []
        self.transforms = []
        self.id = id
        self.map = map
        self.owner = owner
        self.name = name;
        self.maxPlayers = size
        self.shipSize = ships
        self.shipPoints = points
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
    def updateBase(self):
        info = {}
        info[sockServer.field.game.value] = {}
        info[sockServer.field.action.value] = sockServer.action.update.value
        return info
    def recCommand(self, command):
        pass
    def addPlayer(self, player):
        if len(self.players) >= self.maxPlayers: return False
        player.setGame(self, self.getNewId())
        self.players.append(player)
        self.send(player.updateBase(player.getBrowserInfo()))
        return True
    def addUser(self, user):
        return self.addPlayer(player(user, self.shipSize))
    def userLeft(self, user):
        print("userLeft")
        if not self.running: #Remove player if game hasn't started, but keep if it has
            player = self.findPlayer(user)
            if player != None:
                player.destory()           
        alive = False
        for player in self.players:
            if player.user.getSock() != None: 
                alive = True
                break
        if not alive: self.destory()
    def destory(self):
        self.dataStor.sagGames.remove(self)
        self.running = False
        for player in self.players:
            player.user.game = None
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
        info[sockServer.game.shipSize.value] = self.shipSize
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
        #try: #TODO Verify info FIRST, then set values and send
            if user == self.owner:
                sendInfo = False
                if sockServer.game.name.value in info: 
                    self.name = info[sockServer.game.name.value]
                    sendInfo = True
                if sockServer.game.maxPlayers.value in info: 
                    self.maxPlayers = int(info[sockServer.game.maxPlayers.value])
                    sendInfo = True
                if sockServer.game.shipSize.value in info:
                    self.shipSize = int(info[sockServer.game.shipSize.value])
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
                    for i in range(0, int(info[sockServer.game.teams.value])): self.teams.append(team(i))
                if sendInfo: self.send(info)
            info = info[sockServer.game.players.value][0]
            player = self.findPlayer(user)
            sendPlayer = False
            if sockServer.player.team.value in info:
                player.setTeam(int(info[sockServer.player.team.value]))
            if sockServer.player.attack.value in info:
                player.attack = int(info[sockServer.player.attack.value])
                sendPlayer = True
            if sockServer.player.defense.value in info:
                player.defense = int(info[sockServer.player.defense.value])
                sendPlayer = True
            if sockServer.player.speed.value in info:
                player.speed = int(info[sockServer.player.speed.value])
                sendPlayer = True
            if sockServer.player.scout.value in info:
                player.scout = int(info[sockServer.player.scout.value])
                sendPlayer = True
            if sockServer.player.primary.value in info:
                player.primary = info[sockServer.player.primary.value]
                sendPlayer = True
            if sockServer.player.secondary.value in info:
                player.secondary = info[sockServer.player.secondary.value]
                sendPlayer = True
            if sendPlayer: player.send(player.getInfo(True))
            return True
        #except (TypeError, ValueError, AttributeError) as e:
            return False
            print(e)
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
            for team in self.teams:
                team.sendUpdate()
    def send(self, info):
        for player in self.players:
            player.send(info)

class player:
    BASE_SPEED = 10
    BASE_TRAV = math.pi / 4
    BASE_SCOUTS = 10
    BASE_RANGE = 100
    BASE_ATTACK = 1
    BASE_DEFENSE = 1
    def __init__(self, user, ships):
        self.user = user
        self.wepPri = None
        self.wepSec = None
        self.wepPriAmmo = 0
        self.wepSecAmmo = 0
        self.attack = 0
        self.defense = 0
        self.speed = 0
        self.scout = 0
        self.fleets = []
        self.scouts = []
        self.ships = ships
        self.team = None
    def setGame(self, game, id):
        self.user.game = game
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
        nFleet = fleet(size, self, self.game.getNewId(), pos, rot, BASE_SPEED + self.speed / 10, BASE_TRAV + math.pi / 25 * self.speed, self.game.map)
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
            scout = transform(self, self.game.getNewIdl(), fleet.pos, 0, scout, map)
            if bound:
                fleet.addScout(scout)
    def rmTransform(self, transform):
        self.game.rmTransform(transform)
        for team in self.game.teams:
            if team != self.team:
                while True:
                    try: team.spoting.remove(transform)
                    except ValueError: break
        try: self.fleets.remove[transform]
        except ValueError:
            try:
                self.scouts.remove[transform]
                for fleet in fleets:
                    fleet.rmScout(transform)
            except ValueError: pass
    def getInfo(self, statsOnly=False):
        info = {}
        info[sockServer.player.id.value] = self.id
        info[sockServer.player.name.value] = self.user.getName()
        if self.team: info[sockServer.player.team.value] = self.team.number
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
        if not statsOnly:
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
        if self.team: info[sockServer.player.team.value] = self.team.number
        return info
    def updateBase(self, message):
        message[sockServer.player.id.value] = self.id
        info = self.game.updateBase()
        info[sockServer.field.game.value][sockServer.game.players.value] = [message]
        return info
    def setTeam(self, team):
        self.team = team
        self.teams[player.team].players.append(player)
        player = {}
        player[sockServer.player.id.value] = self.id
        player[sockServer.player.team.value] = self.team
        game = {}
        game[sockServer.game.players.value] = [player]
        info = {}
        info[sockServer.field.game.value] = game
        info[sockServer.field.action.value] = sockServer.action.update.value
        self.game.send(info)
    def destory(self):
        self.game.send(self.updateBase({sockServer.player.delete.value: True}))
        self.game.players.remove(self)
        if self.user == self.game.owner and len(self.game.players) > 0:
            self.game.owner = self.game.players[0].user
        if self.team: self.team.players.remove(self)
        self.team = None
        for transform in self.fleets + self.scouts:
            transform.destory()
        self.game = None

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
        self.spotingComputed = False
        self.updateInfo = {}
    def goTo(self, target):
        self.targtPos[0] = min(self.map.width, max(0, target[0]))
        self.targtPos[1] = min(self.map.height, max(0, target[1]))
        adTarg = target[0] - self.pos[0], target[1] - self.pos[1]
        vel = (adTarg[0]^2 + adTarg[1]^2)^.5 / self.speed
        self.vel = adTarg[0] / vel, adTarg[1] / vel
        self.send(self.updateBase(sendPos = True))       
    def turnTo(self, rotation):
        self.targetRot = rotation
        self.rVel = self.trav * (1 if self.rot > math.pi * 2 - self.rot else -1)
        self.send(self.updateBase(sendPos = True))
    def update(self, time):
        self.spottingComputed = False
        if(self.rot != self.targetRot):
            self.updateInfo = {}
            self.changeRot = True
            self.rot = (self.rot + self.rVel * time) % (math.pi * 2)
            if min(self.rot, math.pi * 2 - self.rot) < abs(self.rVel): #Check if it overshot
                self.rot = self.targetRot
                self.rVel = 0
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
        return ((self.pos[0] - transform.pos[0])^2 + (self.pos[1] - transform.pos[1])^2)^.5 <= self.player.BASE_RANGE + self.player.scout
    def computeSpotting(self, transform=None):
        if transform is None:
            for team in player.game.teams:
                if team != player.setTeam:
                    for player in team.players:
                        for transform in player.fleets + player.scouts:
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
        info[sockServer.field.game.value][sockServer.game.players.value][0][sockServer.player.scouts.value] = [message]
        return info
    def send(self, info):
        self.player.team.send(info)
        for team in self.player.game.teams:
            if team != self.player.team:
                if self in team.spoting:
                    team.send(info)

class fleet(transform):
    def __init__(self, size, player, id, position, rotaion, speed, traverse, map):
        self.size = size
        self.scouts = []
        self.merging = None
        super().__init__(game, pos, rot, maxSpeed, trav, map)
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
    def updateBase(self, message = {sockServer.fleet.transform.value: {}}, sendPos = False):
        if message[sockServer.fleet.transform.value] is None:
            message[sockServer.fleet.transform.value] = {}
        message[sockServer.fleet.transform.value] = super.updateBase(message, sendPos)
        info = player.updateBase()
        info[sockServer.field.game.value][sockServer.game.players.value][0][sockServer.player.fleets.value] = [message]
        return info

class team:
    def __init__(self, number):
        self.number = number
        self.players = []
        self.spoting = []
    def send(self, message):
        for player in players:
            player.send(message)

