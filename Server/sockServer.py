import asyncio
import dataManagement
from enum import Enum, unique
import html
import json
import threading
import websockets

dataStor = None

def start(port, data):
    global dataStor
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
    await user.beginReceiveLoop()

class client:
    def __init__(self, conn):
        self.conn = conn
        self.alive = True
        self.errorCount = 0
        self.user = None
        self.receiveDele = []
        self.error = False
    async def beginReceiveLoop(self):
        while self.alive:
            global dataStor;
            try:
                data = await self.conn.recv()
            except websockets.exceptions.ConnectionClosed as e:
                self.destory()
                break
            #Start processing and consturcting response
            print("Message: " + data)
            res = {}
            message = None
            try:
                message = json.loads(data)
                if field.action.value in message:
                    #INITAL CONNECTION---------------------------------------------------------
                    if self.user is None: 
                        if message[field.action.value] == action.init.value:
                            if field.session.value in message:
                                user = dataStor.getUser(message[field.session.value])
                                if user != None:
                                    user.setSock(self)
                                    self.user = user
                                    self.user.rmGame()
                                    if not self.user.getName() is None:
                                        res[field.action.value] = action.name.value;
                                        res[field.name.value] = self.user.getName()
                                        self.send(res)
                        if self.user is None:
                            self.sendError(error.badInit.value)
                    #SET NAME-------------------------------------------------------------------
                    elif message[field.action.value] == action.name.value:
                        if dataStor.setUserName(self.user, message[field.name.value]):
                            res[field.action.value] = action.name.value
                            res[field.name.value] = self.user.getName()
                            self.send(res)
                        else:
                            self.sendError(error.nameUsed.value)
                    #SERVER BROWSER-------------------------------------------------------------
                    elif message[field.action.value] == action.servers.value:
                        self.user.rmGame()
                        res[field.action.value] = action.servers.value
                        res[field.servers.value] = dataStor.getSagInfo()
                        self.send(res)
                    #MAKE GAME--------------------------------------------------------------------
                    elif message[field.action.value] == action.makeGame.value:
                        self.user.rmGame()
                        gameB = message[field.game.value]
                        sagGame = None
                        try:
                            sagGame = dataStor.makeSagGame(self.user, gameB[game.name.value][:30], int(gameB[game.maxPlayers.value]),
                            int(gameB[game.shipSize.value]), int(gameB[game.shipPoints.value]))
                        except ValueError:
                            sagGame = None
                        if sagGame is None:
                            self.sendError(error.createFail.value)
                        else:
                            sagGame.addUser(self.user)
                            res[field.action.value] = action.join.value
                            res[field.game.value] = sagGame.getInfo()
                            self.send(res)
                    #JOIN GAME---------------------------------------------------------------------
                    elif message[field.action.value] == action.join.value:
                        self.user.rmGame()
                        sagGame = dataStor.getSagGame(message[field.game.value][game.id.value])
                        if sagGame is None or not sagGame.addUser(self.user):
                            self.sendError(error.joinFail.value)
                        else:
                            res[field.action.value] = action.join.value
                            res[field.game.value] = sagGame.getInfo()
                            self.send(res)
                    #UPDATE--------------------------------------------------------------------------
                    elif message[field.action.value] == action.update.value:
                        self.user.game.recUpdate(self.user, message[field.game.value])
                            
            except json.JSONDecodeError as e:
                print(e.msg)
                self.sendError(error.badRequest)
            if not self.error:
                self.errorCount = 0
            self.error = False
    def sendError(self, errorCode):
        res = {}
        res[field.action.value] = action.error.value
        res[field.error.value] = errorCode
        self.send(res)
    def send(self, data):
        asyncio.get_event_loop().create_task(self._sendHelper(json.dumps(data)))
    async def _sendHelper(self, data):
        try:
            print("Send: " + str(data))
            await self.conn.send(data)
        except websockets.exceptions.ConnectionClosed as e:
            print(e)
            self.destory()
    def destory(self):
        self.alive = False
        if self.user:
            self.user.rmGame()
            self.user.setSock(None)

@unique
class field(Enum):
    action = "0"
    session = "1"
    servers = "2" #[browser]
    game = "3" #game
    chatContext = "4"
    chatMessage = "5"
    name = "6"
    error = "7"
@unique
class action(Enum):
    error = "1"
    update = "2"
    init = "3"
    servers = "4"
    join = "5"
    name = "6"
    makeGame = "7"
    chat = "8"
    command = "9"
@unique
class error(Enum):
    repeat = "0"
    stop = "1"
    badRequest = "2"
    joinFail = "3"
    createFail = "4"
    badInit = "5"
    forbidden = "6"
    nameUsed = "7"
@unique
class game(Enum):
    id = "0"
    players = "1" #[player]
    running = "2"
    winner = "3"
    name = "4"
    owner = "5"
    maxPlayers = "6"
    shipSize = "7"
    shipPoints = "8"
    mode = "9"
    teams = "10"
    map = "11"
@unique
class player(Enum):
    id = "0"
    name = "1"
    team = "2"
    fleets = "3" #[fleet]
    scouts = "4" #[transform]
    primary = "5" #weapon
    primaryAmmo = "6"
    secondary = "7" #weapon
    secondaryAmmo = "8"
    attack = "9"
    defense = "10"
    scout = "11"
    speed = "12"
    isFlagship = "13"
    ships = "14"
    delete = "15"
@unique
class transform(Enum):
    id = "0"
    pos = "1" #{x,y}
    rot = "2" 
    targetPos = "3" #{x,y}
    targetRot = "4"
    posV = "5" #{x,y}
    rotV = "6" 
    hide = "7"
    destory = "8"
@unique
class fleet(Enum):
    size = "0"
    transform = "1" #transform
@unique
class weapon(Enum):
    lazer = "0"
    missle = "1"
    rail = "2"
    mine = "3"
    fighter = "4"
    plazma = "5"
    emc = "6"
    jump = "7"
    point = "8"
@unique
class chatContext(Enum):
    free = "0"
    game = "1"
    team = "2"
@unique
class command(Enum):
    source = "0" #transform
    fire = "1"  #ammo used if applicatble
    target = "2" #transform
    split = "3" #Size of new fleet
    merge = "4" #[transform]
@unique
class gameMap(Enum):
    height = "0"
    width = "1"