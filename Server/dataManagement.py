from threading import RLock
import hashlib
import binascii
from secrets import SystemRandom
import sockServer
from sagittarius import sagGame

rng = SystemRandom()

class data:
    def __init__(self):
        self.lock = RLock()
        self.users = []
        self.sagGames = []

    def makeUser(self):
        with self.lock:
            newUser = user()
            self.users.append(newUser)
            return user

    def getUser(self, session):
        for user in self.users:
            if user.getSession() == session:
                return user

    def removeUser(self, user):
        with self.lock:
            self.users.remove(user)

    #TODO take a look at the player here
    def makeSagGame(self, size, ships, player):
        with self.lock:
            game = sagGame(size, ships)
            game.addPlayer(player)
            self.sagGames.append(game)

class user:
    def __init__(self, session=None, sock=None):
        self.lock = RLock()
        self.session = session
        if(session == None):
            self.session = getNewSessionId()
        self.sock = sock
        self.game = None

    def setSock(self, sock):
        with self.lock:
            self.sock = sock

    def getSock(self):
        with self.lock:
            return self.sock

    def getSession(self):
        return self.session


#A poor and insecure unique random number generator
#TODO replace
start = rng.getrandbits(k=64)
key = rng.getrandbits(k=64)
def getNewSessionId():
    parts = []
    for b1, b2 in zip(start, key):
        parts.append(bytes(b1 ^ b2))
    start = (start + 1) % 2^64
    return b''.join(parts)
    
    
