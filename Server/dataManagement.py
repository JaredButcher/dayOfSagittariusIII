from threading import RLock
import hashlib
import secrets
import sockServer
import binascii
from sagittarius import sagGame

rng = secrets.SystemRandom()

class data:
    def __init__(self, debug):
        self.debug = debug
        self.lock = RLock()
        self.users = []
        self.sagGames = []
        self.idCounter = 0;

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

    def makeSagGame(self, owner, size, ships, points, teams, mode):
        with self.lock:
            game = sagGame(self.getNewId(), owner, size, ships, points, teams, mode)
            self.sagGames.append(game)

    def getSagInfo(self):
        info = []
        for game in self.sagGames:
            info.append(game.getInfo())

    def getNewId(self):
        self.idCounter += 1
        return self.idCounter

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

    def getName(self):
        return self.name

    def setName(self, name):
        with self.lock:
            self.name = name
            return self.name


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
    
    
