import socket
import asyncio
import threading
import dataManagement
        
clients = []
dataStor = dataManagement.data

def start(port, data):
    dataStor = data
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    coro = asyncio.start_server(handle_conn, '', port, loop=loop)
    server = loop.run_until_complete(coro)
    try:
        loop.run_forever()
    except socket.error as e:
        print(e)
    print("close")
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()

async def handle_conn(reader, writer):
    clients.append(client(reader, writer))

class client:
    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer
        self.alive = True
        asyncio.get_event_loop().create_task(self.beginReceiveLoop())
    
    async def beginReceiveLoop(self):
        while self.alive:
            try:
                data = await self.reader.read(1024)
            except socket.error as e:
                print(e)
                self.destory()
                break;
            message = data.decode()
            print(message)
            asyncio.get_event_loop().create_task(self.send(str.encode(message)))

    async def send(self, data):
        self.writer.write(data)
        try:
            await self.writer.drain()
        except socket.error as e:
            print(e)
            self.destory()
    
    def destory(self):
        self.alive = False
        clients.remove(self)
        