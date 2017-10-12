import http.server

PORT = 8000

def startServer(server_class=http.server.HTTPServer, handler_class=http.server.SimpleHTTPRequestHandler):
    serverAddress = ('', PORT)
    httpd = server_class(serverAddress, handler_class)
    httpd.serve_forever()

startServer()
while True:
    pass