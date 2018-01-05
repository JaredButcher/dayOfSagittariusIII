import websockets
import asyncio
import threading
import dataManagement
import json
from enum import Enum, unique
        
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
                            self.sendError(error.badInitalConn.value)
                    #SET NAME-------------------------------------------------------------------
                    elif message[field.action.value] == action.name.value:
                        if dataStor.setUserName(self.user, message[field.name.value]):
                            res[field.action.value] = action.name.value
                            res[field.name.value] = self.user.getName()
                            self.send(res)
                        else:
                            self.sendError(error.createFail.value)
                    #SERVER BROWSER-------------------------------------------------------------
                    elif message[field.action.value] == action.servers.value:
                        print("Server Browser")
                        self.user.rmGame()
                        res[field.action.value] = action.servers.value
                        res[field.servers.value] = dataStor.getSagInfo()
                        self.send(res)
                    #MAKE GAME--------------------------------------------------------------------
                    elif message[field.action.value] == action.makeGame.value:
                        self.user.rmGame()
                        gameB = message[field.game.value]
                        try:
                            sagGame = dataStor.makeSagGame(self.user, gameB[game.name.value], int(gameB[game.maxPlayers.value]),
                            int(gameB[game.fleetSize.value]), int(gameB[game.fleetPoints.value]))
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
                        if not self.user.game.recUpdate(self, message[field.game.value]):
                            self.sendError(error.badRequest.value)
                            
            except json.JSONDecodeError as e:
                print(e.msg)
                self.sendError(error.badRequest)
            if not self.error:
                self.errorCount = 0
            self.error = False

    def sendError(self, errorCode = 0):
        self.errorCount += 1
        self.error = True
        res = {}
        res[field.action.value] = action.error.value
        res[field.error.value] = errorCode
        if self.errorCount > 5:
            res[field.error.value] = error.stop.value
        self.send(res)
    def send(self, data):
        asyncio.get_event_loop().create_task(self._sendHelper(json.dumps(data)))
    async def _sendHelper(self, data):
        try:
            print("SendHelp: " + str(data))
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
    gameId = "3"
    game = "4" #game
    chatContext = "5"
    chatMessage = "6"
    team = "7"
    name = "8"
    transform = "9"
    error = "10"
@unique
class action(Enum):
    ack = "0"
    error = "1"
    update = "2"
    init = "3"
    servers = "4"
    join = "5"
    name = "6"
    makeGame = "7"
    chat = "8"
    joinTeam = "9"
    command = "10"
@unique
class error(Enum):
    repeat = "0"
    stop = "1"
    joinFail = "2"
    createFail = "3"
    badRequest = "4"
    badInitalConn = "5"
@unique
class game(Enum):
    id = "0"
    players = "1" #[player]
    running = "2"
    winner = "3"
    name = "4"
    owner = "5"
    maxPlayers = "6"
    fleetSize = "7"
    fleetPoints = "8"
    gameMode = "9"
    teams = "10"
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
@unique
class transform(Enum):
    id = "0"
    position = "1" #{x,y}
    rotation = "2" 
    velocity = "3" #{x,y}
    hide = "4"
    destory = "5"
    rVelocity = "6"
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
@unique
class chatContext(Enum):
    browser = "0"
    game = "1"
    team = "2"
@unique
class command(Enum):
    destination = "0" #transform
    fire = "1"
    target = "2" #transform
    split = "3"
    merge = "4" #[transform]