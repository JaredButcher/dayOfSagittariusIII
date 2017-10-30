import dataManagement
import threading

class sagGame:
    def __init__(self):
        self.players = []
        self.live = True
        self.gameLoop = threading.Thread(target=self.loop)
        self.gameLoop.start()

    def addPlayer(self, player):
        self.players.append(player)

    def recCommand(self, )

    def loop(self):
        while self.live:



