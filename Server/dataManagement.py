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
        self.idCounter = 0
    def makeUser(self):
        with self.lock:
            newUser = user(getNewSessionId(self.users))
            self.users.append(newUser)
            return newUser
    def getUser(self, session):
        for user in self.users:
            if user.getSession() == session:
                return user
    def removeUser(self, user):
        with self.lock:
            self.users.remove(user)
    def makeSagGame(self, owner, name, size, ships, points, teams = 2, mode = 1):
        with self.lock:
            game = sagGame(self, self.getNewId(), owner, name, size, ships, points, teams, mode)
            self.sagGames.append(game)
            return game;
    def getSagInfo(self):
        info = []
        for game in self.sagGames:
            info.append(game.getInfo(True))
        return info
    def getSagGame(self, id):
        for game in self.sagGames:
            if game.id == id: return game
        return None
    def getNewId(self):
        with self.lock:
            self.idCounter += 1
            return self.idCounter
    def setUserName(self, user, name):
        name = name[:20]
        with self.lock:
            for x in self.users:
                if x.getName() == name: return None
            user.setName(name)
            return name

class user:
    def __init__(self, session, sock=None):
        self.lock = RLock()
        self.session = session
        self.sock = sock
        self.game = None
        self.name = None
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
    def rmGame(self):
        with self.lock:
            if self.game != None:
                self.game.userLeft(self)
                self.game = None


#A poor and ineffecent unique random number generator
#TODO replace
size = 128
def getNewSessionId(users):
    key = rng.getrandbits(k=size).to_bytes(int(size / 8), 'big').hex()
    for user in users:
        if user.session == key:
            return getNewSessionId(users)
    print("Session: " + key)
    return key
    
    
