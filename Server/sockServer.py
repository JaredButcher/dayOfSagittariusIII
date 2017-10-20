import socket
import asyncio
import threading
        
clients = []

def start(port, data):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    coro = asyncio.start_server(handle_conn, '', port, loop=loop)
    server = loop.run_until_complete(coro)
    print("server")
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("interupt")
        pass
    print("close")
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()

async def handle_conn(reader, writer):
    print("connection handler")
    clients.append(client(reader, writer))

class client:
    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer
        asyncio.get_event_loop().create_task(self.beginReceiveLoop())
        print("init")
    
    async def beginReceiveLoop(self):
        print("Receive")
        while True:
            data = await self.reader.read(100)
            message = data.decode()
            print(message)
            asyncio.get_event_loop().create_task(self.send(str.encode(message)))

    async def send(self, data):
        self.writer.write(data)
        await self.writer.drain()
        