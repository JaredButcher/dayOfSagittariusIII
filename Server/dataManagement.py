from threading import RLock
import hashlib
import binascii
from secrets import SystemRandom
import sockServer

rng = SystemRandom()

class data:
    def __init__(self):
        self.lock = RLock()
        self.sessions = []
        self.players = []
    def makeSession(self):
        with self.lock:
            sessionT = session()
            self.sessions.append(sessionT)
            return sessionT
    def closeSession(self, session):
        with self.lock:
            self.sessions.remove(session)
    def getSession(self, session=None, client=None):
        with self.lock:
            if(session):
                for sess in self.sessions:
                    if sess.getId() == session:
                        return sess
                return None
            elif(client):
                for sess in self.sessions:
                    if sess.getClient() == client:
                        return sess
                return None

class session:
    def __init__(self):
        self.lock = RLock()
        self.userId = None
        self.id = str(rng.getrandbits(k=64))
    
    def getId(self):
        with self.lock:
            return self.id

    def UserId(self, userId=None):
        with self.lock:
            if userId != None:
                self.userId = userId
            return self.userId

    def setClient(self, client):
        with self.lock:
            self.client = client

    def getClient(self, message):
        with self.lock:
            return self.client

    def rmClient(self):
        with self.lock:
            self.client = None
