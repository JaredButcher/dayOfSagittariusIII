import websockets
import asyncio
import threading
import dataManagement
import json
from enum import IntEnum, unique
        
clients = []
dataStor = None

#TODO Userfy this class

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

class client:
    def __init__(self, conn):
        self.conn = conn
        self.alive = True
        self.errorCount = 0
        self.session = None
        self.receiveDele = []
        self.onReceiveAdd(self.initalConn)
        self.error = False

    '''
    delegate: (data) json string
    '''
    def onReceiveAdd(self, delegate):
        self.receiveDele.append(delegate)

    def onReceiveRm(self, delegate):
        self.receiveDele.remove(delegate)
    
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
            message = None
            try:
                message = json.load(data.decode())
            except json.JSONDecodeError as e:
                print(e.msg)
            for dele in self.receiveDele:
                dele(message)
            if not self.error:
                self.errorCount = 0
            self.error = False
            if self.errorCount > 10:
                self.destory()
    
    def initalConn(self, message):
        print(json.dumps(message))
        if field.action in message and message[field.action] == action.init:
            if field.session in message:
                user = dataStor.getSession(field.session)
                if(user != None):
                    user.setClient(self)
                    self.session = user
                    self.onReceiveRm(self.initalConn)
                    return
        self.sendError()

    def sendError(self, errorCode = 0):
        self.errorCount += 1
        self.error = True
        res = {}
        res[field.action] = action.error
        res[field.error] = errorCode
        if self.errorCount > 5:
            res[field.error] = error.stop
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

@unique
class field(IntEnum):
    action = 0
    session = 1
    servers = 2 #[browser]
    gameId = 3
    game = 4 #game
    chatContext = 5
    chatMessage = 6
    team = 7
    name = 8
    transform = 9
    error = 10
@unique
class action(IntEnum):
    ack = 0
    error = 1
    update = 2
    init = 3
    servers = 4
    join = 5
    name = 6
    makeGame = 7
    chat = 8
    joinTeam = 9
    command = 10
@unique
class error(IntEnum):
    repeat = 0
    stop = 1
    joinFail = 2
    createFail = 3
@unique
class browser(IntEnum):
    id = 0
    name = 1
    owner = 2
    players = 3
    maxPlayers = 4
    fleetSize = 5
    fleetPoints = 6
    gameMode = 7
    teams = 8
@unique
class game(IntEnum):
    browserInfo = 0 #browser
    players = 1 #[player]
    running = 2
    winner = 3
@unique
class player(IntEnum):
    id = 0
    name = 1
    team = 2
    fleets = 3 #[fleet]
    scouts = 4 #[transform]
    primary = 5 #weapon
    primaryAmmo = 6
    secondary = 7 #weapon
    secondaryAmmo = 8
    attack = 9
    defense = 10
    scout = 11
    speed = 12
    isFlagship = 13
@unique
class transform(IntEnum):
    id = 0
    position = 1 #{x,y}
    rotation = 2 
    velocity = 3 #{x,y}
    hide = 4
    destory = 5
@unique
class fleet(IntEnum):
    size = 0
    transform = 1 #transform
@unique
class weapon(IntEnum):
    lazer = 0
    missle = 1
    rail = 2
    mine = 3
    fighter = 4
    plazma = 5
    emc = 6
    jump = 7
@unique
class chatContext(IntEnum):
    browser = 0
    game = 1
    team = 2
@unique
class command(IntEnum):
    destination = 0 #transform
    fire = 1
    target = 2 #transform
    split = 3
    merge = 4 #[transform]