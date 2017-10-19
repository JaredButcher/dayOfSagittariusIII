import socket
import threading

def accept(server):
    while True:
        conn, address = server.accept()
        print("Connection established")
        

def start(port, data):
    serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv.setblocking(1)
    serv.bind(('',port))
    serv.listen(1)
    accept(serv)
    
'''
class ComControl:
    def send(self, data):
        """
        Sends data to the controler
        :param data: String from ComData
        """
        self._loop.run_in_executor(None, self._send, str.encode(data))

    def _receive(self):
        try:
            data = self._conn.recv(1024)
            self._onReceived(data)
            self._loop.run_in_executor(None, self._receive)
        except socket.error as e:
            print("Connection lost")
            self._loop.run_in_executor(None, self._accept)
    
    def _send(self, data):
        try:
            self._conn.sendall(data)
        except socket.error as e:
            print("Connection lost")
            self._loop.run_in_executor(None, self._accept)

    def _onReceived(self, data):
        pass

    def _onDisconnect(self):
        pass
'''