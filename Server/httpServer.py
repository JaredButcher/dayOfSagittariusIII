from http.server import BaseHTTPRequestHandler, HTTPServer
from http import cookies
import dataManagement
import time
import math

dataStor = None
_timeP = 0

def start(port, data):
    global dataStor
    dataStor = data
    serverAddress = ('', port)
    httpd = HTTPServer(serverAddress, HTTPHandler)
    httpd.serve_forever()

def timeF(lable):
    global _timeP
    timeR = math.floor(((time.perf_counter() - _timeP) * 1000000))
    print(lable + ": " + str(timeR))
    _timeP = time.perf_counter()
    return timeR

def timeCalibrate():
    global _timeP
    _timeP = time.perf_counter()

class HTTPHandler(BaseHTTPRequestHandler):

    content = "Server/Website/"
    defaultTitle = "Day of Sagittarius III"
    paths = {"home": "cHome", "user":None, "static":"cStatic", "sagittarius":"cSag"}
    mimes = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "html": "text/html",
        "htm": "text/html",
        "txt": "text/plain",
        "png": "image/png",
        "gif": "image/gif",
        "css": "text/css",
        "js": "application/javascript",
        "json": "application/json",
        "mp4": "video/mp4",
        "ico": "image/x-icon"}

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.handleCookies()
        self.end_headers()
    def do_GET(self):
        #self.totalTime = 0
        #timeCalibrate()
        self.statusCode = 200
        self.mime = "text/html"
        body = bytes(self.route(), "utf8")
        #self.totalTime += timeF("Body")
        self.send_response(self.statusCode)
        self.send_header("Content-type", self.mime)
        self.handleCookies()
        #self.totalTime += timeF("Cookies")
        self.end_headers()
        self.wfile.write(body)
        #self.totalTime += timeF("Write")
        #print("Total: " + str(self.totalTime))
        #print()

    def handleCookies(self):
        global dataStor
        cook = cookies.SimpleCookie()
        if "Cookie" in self.headers:
            cook.load(self.headers["Cookie"])
            if "session" in cook:
                self.user = dataStor.getUser(cook["session"].value)
                if self.user != None:
                    return
        user = dataStor.makeUser()
        cook["session"] = user.getSession()
        cook["session"]["path"] = "/"
        cook["session"]["max-age"] = 259200
        self.send_header("Set-Cookie", str(cook["session"])[12:])
        self.user = user


    def log_message(self, format, *args):
        return
    
    def route(self):
        path = self.path.split('/')
        if self.path == "/":
            return self.cHome()
        elif path[1] in self.paths:
            if len(path) == 2 or path[2] == "":
                return getattr(self, self.paths[path[1]])()
            else:
                return getattr(self, self.paths[path[1]])(path[2])
        else:
            self.statusCode = 404
            return self.cHome("error")

    def cHome(self, view = "index"):
        if view == "index":
            return self.layout(self.readFile("home/index.html"))
        elif view == "about":
            return self.layout(self.readFile("home/about.html"))
        else:
            fContent = self.readFile("home/error.html")
            if(self.statusCode == 200):
                self.statusCode = 403
            fContent = fContent.format(error = self.statusCode)
            return self.layout(fContent)

    def cSag(self, view = "game"):
        if view == "game":
            return self.layout(self.readFile("sagittarius/game.html"))
        else:
            return self.cHome("error")

    def cStatic(self, unused):
        path = self.path[len("/"):]
        try:
            fContent = self.readFile(path)
            self.mime = self.mimes[path[path.rindex(".") + 1:]]
            return fContent
        except IOError:
            return self.cHome("error")


    
    def readFile(self, fPath):
        with open(self.content + fPath) as f:
            fContent = f.read()
            f.close()
            return fContent

    def layout(self, pContent = None, pTitle = None):
        pTitle = pTitle or self.defaultTitle
        with open(self.content + "layout.html") as f:
                fLayout = f.read()
                f.close()
                fLayout = fLayout.format(title = pTitle, content = pContent)
                return fLayout
            