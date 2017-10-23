from threading import RLock
import hashlib
import binascii
from secrets import SystemRandom

rng = SystemRandom()

class data:
    def __init__(self):
        self.lock = RLock()
        self.sessions = []
    def makeSession(self):
        with self.lock:
            sessionT = session()
            self.sessions.append(sessionT)
            return sessionT
    def closeSession(self, session):
        with self.lock:
            self.sessions.remove(session)
    def getSession(self, session):
        with self.lock:
            for sess in self.sessions:
                if sess.getId() == session:
                    return sess
            return None

class session:
    def __init__(self):
        self.lock = RLock()
        self.userId = None
        self.id = str(rng.getrandbits(k=128))
    
    def getId(self):
        with self.lock:
            return self.id

    def UserId(self, userId=None):
        with self.lock:
            if userId != None:
                self.userId = userId
            return self.userId