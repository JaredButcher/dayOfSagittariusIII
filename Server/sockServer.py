import socket
import asyncio
import threading
        
clients = []

def start(port, data):
    loop = asyncio.get_event_loop()
    serv = asyncio.start_server(handle_echo, '127.0.0.1', 8888, loop=loop)
    server = loop.run_until_complete(serv)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()

async def connectLoop(port):
    serv = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
    serv.bind(('', port))
    serv.listen(4)
    while True:
        conn, address = await serv.accept()
        clients.append(client(conn))


class client:
    def __init__(self, conn):
        self.conn = conn
    
    async def beginReceiveLoop():
        data = await comm.recv(1024)
        

async def handle_echo(reader, writer):
    data = await reader.read(100)
    message = data.decode()
    addr = writer.get_extra_info('peername')
    print("Received %r from %r" % (message, addr))

    print("Send: %r" % message)
    writer.write(data)
    await writer.drain()

    print("Close the client socket")
    writer.close()
    
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