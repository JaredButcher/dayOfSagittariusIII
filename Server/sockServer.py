import websockets
import asyncio
import threading
import dataManagement
import json
from enum import IntEnum, unique
        
clients = []
dataStor = None

def start(port, data):
    dataStor = data
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    coro = websockets.server.serve(handle_conn, host='', port=port, loop=loop)
    server = loop.run_until_complete(coro)
    loop.run_forever()
    print("close")
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()
    
async def handle_conn(conn, Uri):
    print("URI: " + Uri)
    user = client(conn)
    clients.append(user)
    await user.beginReceiveLoop()

@unique
class fields(IntEnum):
    action = 0
    session = 1
@unique
class actions(IntEnum):
    ack = 0
    errorStop = 1
    errorResend = 2
    init = 3
    servers = 4

class client:
    def __init__(self, conn):
        self.conn = conn
        self.alive = True
        self.errorCount = 0
        self.session = None
    
    async def beginReceiveLoop(self):
        while self.alive:
            try:
                data = await self.conn.recv()
            except websockets.exceptions.ConnectionClosed as e:
                print(e)
                self.destory()
                break;
            #Start processing and consturcting response
            print(str(data))
            res = {}
            errorRe = False
            try:
                message = json.load(data.decode())
            except json.JSONDecodeError as e:
                print(e.msg)
                message = None
            #Process message
            if fields.action in message:
                if message[fields.action] == actions.init:
                    if fields.session in message:
                        user = data.getSession(fields.session)
                        if(user != None):
                            user.setClient(self)
                            self.session = user
                        else:
                            errorRe = True
                    else:
                        errorRe = True
                else:
                    errorRe = True
                print(json.dumps(message))
            else:
                errorRe = True
            #Tell to repeat or stop repeating error
            if(errorRe):
                if self.errorCount < 10:
                    self.destory()
                elif self.errorCount < 5:
                    res[fields.action] = actions.errorResend
                else:
                    res[fields.action] = actions.errorStop
            else:
                self.errorCount = 0
            #Send message
            if(res != {}):
                asyncio.get_event_loop().create_task(self.send(str.encode(json.dumps(res))))

    async def send(self, data):
        try:
            await self.conn.send(data)
        except websockets.exceptions.ConnectionClosed as e:
            print(e)
            self.destory()
    
    def destory(self):
        self.alive = False
        if self.session:
            self.session.rmClient()
        clients.remove(self)
        