import dataManagement
import threading
import math

class sagGame:
    def __init__(self, size, ships):
        self.players = []
        self.live = True
        self.gameLoop = threading.Thread(target=self.loop)
        self.gameLoop.start()

    def addPlayer(self, player):
        self.players.append(player)

    #def recCommand(self, )

    def loop(self):
        while self.live:

class player:
    def __init__(self, socket, team, ships, attack, defense, speed, scout, wepPri, wepSec):
        self.socket = socket
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
    def __init__(self, x = 0,y = 0, r = 0, maxSpeed = 0, Traverse = 0):
        self.x, self.tx, self.y self.ty = x, x, y, y
        self.r, self.tr = r
        self.maxSpeed = maxSpeed
        self.trav = Traverse

    def goTo(self, x,y):
        self.tx, self.ty = x, y
        tempX, tempY = x - self.x, y - self.y
        self.vx = ((tempX^2)/(tempX^2 + tempY^2))^.5
        self.vy = ((tempY^2)/(tempX^2 + tempY^2))^.5

    def turnTo(self, rotation):
        self.tr = rotation
        self.trd = self.r - self.tr - math.pi
        self.trd != -1 * math.pi or self.trd = 0

    def update(self, time):
        if(self.r != self.rt):
            if(self.trd > 0):
                self.r = self.r + self.trav
            else:
                self.r = self.r - self.trav
            if((self.r - self.tr + math.pi) * self.trd < 0):
                self.r = self.tr
        if(self.x != self.tx or self.y != self.ty):
            if(self.x < self.tx):
                self.x = max(self.tx, self.x + self.vx) 
            else:
                self.x = min(self.tx, self.x + self.vx) 
            if(self.y < self.ty):
                self.y = max(self.ty, self.y + self.vy) 
            else:
                self.y = min(self.ty, self.y + self.vy) 




