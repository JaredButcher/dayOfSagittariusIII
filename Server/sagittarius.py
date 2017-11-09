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

    def recCommand(self, )

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
    def __init__(self, x = 0,y = 0, rot = 0, maxSpeed = 0, maxRot = 0):
        self.x = x
        self.y = y
        self.rot = rot
        self.maxSpeed = maxSpeed
        self.maxRot = maxRot

    def goTo(self, x,y):
        self.tx = x
        self.ty = y
        self.vx = 
        self.vy

    def turn(self, rot):
        self.tr = rot

    def update(self, time):
        if(self.x != self.tx or self.y != self.ty):
            if(self.rot != self.rt):
                
            else:
                tempX = (self.tx - self.x) self.maxSpeed



