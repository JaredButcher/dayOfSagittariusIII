import dataManagement
import threading
import math
import time

#TODO Userfy this class

class sagGame:
    def __init__(self, size, ships):
        self.players = []
        self.transforms = []
        self.live = True
        self.gameLoop = threading.Thread(target=self.loop)
        self.gameLoop.start()

    def addPlayer(self, player):
        self.players.append(player)

    def addTransform(self, transform):
        self.transforms.append(transform)

    def rmTransform(self, transform):
        self.transforms.remove(transform)

    #def recCommand(self, )

    def loop(self):
        timeP = time.perf_counter() 
        while self.live:
            timeC = time.perf_counter()
            delta = timeC - timeP
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

class transform:
    def __init__(self, game, x = 0,y = 0, r = 0, maxSpeed = 0, Traverse = 0):
        self.x, self.tx, self.y, self.ty = x, x, y, y
        self.r, self.tr = r
        self.maxSpeed = maxSpeed
        self.trav = Traverse
        self.game = game
        self.game.addTransform(self)

    def goTo(self, x,y):
        self.tx, self.ty = x, y
        tempX, tempY = x - self.x, y - self.y
        self.vx = ((tempX^2)/(tempX^2 + tempY^2))^.5
        self.vy = ((tempY^2)/(tempX^2 + tempY^2))^.5

    def turnTo(self, rotation):
        self.tr = rotation
        self.trd = self.r - self.tr - math.pi

    def update(self, time):
        if(self.r != self.tr):
            if(self.trd > 0):
                self.r = self.r + self.trav * time
            else:
                self.r = self.r - self.trav * time
            if((self.r - self.tr + math.pi) * self.trd < 0):
                self.r = self.tr
        if(self.x != self.tx or self.y != self.ty):
            if(self.x < self.tx):
                self.x = max(self.tx, self.x + self.vx * time) 
            else:
                self.x = min(self.tx, self.x + self.vx * time) 
            if(self.y < self.ty):
                self.y = max(self.ty, self.y + self.vy * time) 
            else:
                self.y = min(self.ty, self.y + self.vy * time) 

    def destory(self):
        self.game.rmTransform(self)




