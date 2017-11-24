from threading import RLock
import hashlib
import secrets
import sockServer
import binascii
from sagittarius import sagGame

rng = secrets.SystemRandom()

class data:
    def __init__(self):
        self.lock = RLock()
        self.users = []
        self.sagGames = []

    def makeUser(self):
        with self.lock:
            newUser = user()
            self.users.append(newUser)
            return newUser

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
size = 128
start = rng.getrandbits(k=size)
key = rng.getrandbits(k=size).to_bytes(int(size / 8), byteorder="big")
def getNewSessionId():
    global start, key, size
    parts = []
    for b1, b2 in zip(start.to_bytes(int(size / 8), byteorder="big"), key):
        parts.append("%x" % (b1 ^ b2))
    start = (start + rng.getrandbits(k=int(size / 2))) % 2^size
    print("Message: " + ''.join(parts))
    return ''.join(parts)
    
    
