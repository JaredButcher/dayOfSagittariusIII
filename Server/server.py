import httpServer
import sockServer
import threading
from queue import Queue

HTTP_PORT = 8000
SOCK_PORT = 8001
HTTP_THREADS = 1
SOCK_THREADS = 2

class data:
    def __init__(self):
        self.lock = threading.RLock()
        self.sessions = []
    def addSession(self, session):
        with self.lock:
            self.sessions.append(session)
    def closeSession(self, session):
        with self.lock:
            self.sessions.remove(session)

serverData = data()

httpd = threading.Thread(target = httpServer.start, args=(HTTP_PORT, serverData))
sockd = threading.Thread(target = sockServer.start, args=(SOCK_PORT, serverData))

httpd.start()
sockd.start()






