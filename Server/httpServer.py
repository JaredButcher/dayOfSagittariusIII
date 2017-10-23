from http.server import BaseHTTPRequestHandler, HTTPServer
from http import cookies
import dataManagement

dataStor = dataManagement.data()

def start(port, data):
    dataStor = data
    serverAddress = ('', port)
    httpd = HTTPServer(serverAddress, HTTPHandler)
    httpd.serve_forever()


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
        self.end_headers()
    def do_GET(self):
        self.statusCode = 200
        self.mime = "text/html"
        body = bytes(self.route(), "utf8")
        self.send_response(self.statusCode)
        self.send_header("Content-type", self.mime)
        self.handleCookies()
        self.end_headers()
        self.wfile.write(body)

    def handleCookies(self):
        cook = cookies.SimpleCookie()
        if "Cookie" in self.headers:
            cook.load(self.headers["Cookie"])
            if "session" in cook:
                self.session = dataStor.getSession(cook["session"].value)
                if self.session != None:
                    return
        session = dataStor.makeSession()
        cook["session"] = session.getId()
        cook["session"]["path"] = "/"
        cook["session"]["max-age"] = 259200
        self.send_header("Set-Cookie", str(cook["session"])[12:])
        self.session = session


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

    def cSag(self, view = None):
        self.statusCode = 404
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
            