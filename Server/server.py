import httpServer
import sockServer
import dataManagement
import threading

HTTP_PORT = 8000
SOCK_PORT = 8001
HTTP_THREADS = 1
SOCK_THREADS = 2

serverData = dataManagement.data()

httpd = threading.Thread(target = httpServer.start, args=(HTTP_PORT, serverData))
sockd = threading.Thread(target = sockServer.start, args=(SOCK_PORT, serverData))

httpd.start()
sockd.start()






