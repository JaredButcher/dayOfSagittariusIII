import httpServer
import sockServer
import dataManagement
import threading

HTTP_PORT = 8000
SOCK_PORT = 8001
DEBUG = True

serverData = dataManagement.data(DEBUG)

httpd = threading.Thread(target = httpServer.start, args=(HTTP_PORT, serverData))
httpd.start()

while(True):
    try:
        sockd = threading.Thread(target = sockServer.start, args=(SOCK_PORT, serverData))
        sockd.start()
        sockd.join()
    except Exception:
        break;
