const field = {
    action: "0",
    session: "1",
    servers: "2", //[browser]
    game: "3", //game
    chatContext: "4",
    chatMessage: "5",
    name: "6",
    error: "7"};
const action = {
    error: "1",
    update: "2",
    init: "3",
    servers: "4",
    join: "5",
    name: "6",
    makeGame: "7",
    chat: "8",
    command: "9"};
const error = {
    repeat: "0",
    stop: "1",
    badRequest: "2",
    joinFail: "3",
    createFail: "4",
    badInit: "5",
    forbidden: "6"};
const game = {
    id: "0",
    players: "1", //[player]
    running: "2",
    winner: "3",
    name: "4",
    owner: "5",
    maxPlayers: "6",
    shipSize: "7",
    shipPoints: "8",
    mode: "9",
    teams: "10",
    map: "11"};
const player = {
    id: "0",
    name: "1",
    team: "2",
    fleets: "3", //[fleet]
    scouts: "4", //[transform]
    primary: "5", //weapon
    primaryAmmo: "6",
    secondary: "7", //weapon
    secondaryAmmo: "8",
    attack: "9",
    defense: "10",
    scout: "11",
    speed: "12",
    isFlagship: "13",
    ships: "14",
    delete: "15"};
const transform = {
    id: "0",
    pos: "1", //{x,y}
    rot: "2", 
    targetPos: "3", //{x,y}
    targetRot: "4",
    posV: "5", //{x,y}
    rotV: "6", 
    hide: "7",
    destory: "8"}
const fleet = {
    size: "0",
    transform: "1"};
const weapon = {
    lazer: "0",
    missle: "1",
    rail: "2",
    mine: "3",
    fighter: "4",
    plazma: "5",
    emc: "6",
    jump: "7",
    point: "8"};
const chatContext = {
    free: "0",
    game: "1",
    team: "2"};
const command = {
    source: "0", //transform
    fire: "1",  //ammo used if applicatble
    target: "2", //transform
    split: "3", //Size of new fleet
    merge: "4"};
const gameMap = {
    height: "0",
    width: "1"};
const scenes = {
    start: 0,
    makeGame: 1,
    servers: 2,
    lobby: 3,
    game: 4};


var currentScene;
var user = {
    name: "",
    points: 0,
    attack: 0,
    defense: 0,
    speed: 0,
    scout: 0,
    fleets: []};
var gameInfo = {
    id: "",
    name: "",
    owner: "",
    pointsMax: 0,
    players: [],
    maxPlayers: 0,
    fleetSize: 0};

function scene(current){ //Changes Scene
    document.getElementById("start").hidden = true;
    document.getElementById("makeGame").style.display = "none";
    document.getElementById("servers").hidden = true;
    document.getElementById("lobby").style.display = "none";
    document.getElementById("game").hidden = true;
    switch(current){
        case scenes.start:
        document.getElementById("start").hidden = false;
        var buttons = document.getElementsByClassName("startNav"); //CSS display overides the html hidden attribute
        for(var i = 0; i < buttons.length; ++i){
            buttons[i].disabled = true;
        }
        break;
        case scenes.makeGame:
            document.getElementById("makeGame").style.display = "grid";
            document.getElementById("mgName").value = user.name + "`s game";
            document.getElementById("mgPlayers").value = 6;
            document.getElementById("mgFleet").value = 10000;
            document.getElementById("mgPoints").value = 200;
        break;
        case scenes.servers:
            document.getElementById("servers").hidden = false;
            serverBrowser();
        break;
        case scenes.lobby:
            document.getElementById("lobby").style.display = "grid";
        break;
        case scenes.game:
            document.getElementById("game").hidden = false;
        break;
    }
    currentScene = current;
}

var Conn = new WebSocket("ws://" + window.location.hostname + ":8001/sagittarius");

Conn.onopen = function (event) {
    var res = {};
    //Send cookie or wait to receive one
    res[field.action] = action.init;
    res[field.session] = getCookie("session");
    if(res[field.session] != ""){
        Send(res);
    } else {
        browser.cookies.onChanged.addListener(getCookieEvent);
    }
};
Conn.onmessage = function (message) { //Receive and direct or process all socket messages
    console.log(message.data);
    try{
        var data = JSON.parse(message.data);
        switch(data[field.action]){
            case action.ack:
            break;
            case action.chat:
            break;
            case action.command:
            break;
            case action.error:
            break;
            case action.init:
            break;
            case action.join:
                console.log("Join");
                document.getElementById("glPlayerInfo").innerHTML = "";
                var info = data[field.game];
                gameInfo.id = info[game.id];
                gameInfo.name = info[game.name];
                gameInfo.owner = info[game.owner];
                gameInfo.maxPlayers = info[game.maxPlayers];
                gameInfo.fleetSize = info[game.shipSize];
                gameInfo.pointsMax = info[game.shipPoints];
                gameInfo.players = [];
                for(var i = 0; i < info[game.players].length; i++){
                    var play = new gamePlayer(info[game.players][i][player.id]);
                    play.update(info[game.players][i]);
                    gameInfo.players.push(play);
                }
                document.getElementById("glName").innerText = gameInfo.name;
                document.getElementById("glOwner").innerText = "Owner: " + gameInfo.owner;
                document.getElementById("glPlayers").innerText = "Players: " + gameInfo.players.length + "/" + gameInfo.maxPlayers;
                document.getElementById("glFleetSize").innerText = "Fleet Size: " + gameInfo.fleetSize;
                document.getElementById("glAttack").value = 0;
                document.getElementById("glDefense").value = 0;
                document.getElementById("glSpeed").value = 0;
                document.getElementById("glScout").value = 0;
                setStats(false);
                scene(scenes.lobby);
            break;
            case action.joinTeam:
            break;
            case action.makeGame:
            break;
            case action.name:
                console.log("Name");
                document.getElementById("userNameError").hidden = true;
                var buttons = document.getElementsByClassName("startNav");
                for(var i = 0; i < buttons.length; ++i){
                    buttons[i].disabled = false;
                }
                user.name = data[field.name];
                document.getElementById("userName").value = user.name;
            break;
            case action.servers:
                console.log("Servers");
                var serversS = "";
                if(data[field.servers] == null){
                    serversS = "<div><h2>No games avaliable<h2></div>";
                } else {
                    var info = {}
                    for(var i = 0; i < data[field.servers].length; ++i){
                        info = data[field.servers][i];
                        serversS += '<div class="serverInfo" onclick="join(' + info[game.id] + ');"><p>ID: ' + info[game.id] + "</p><p>Name: " + info[game.name]
                            + "</p><p>Owner: " + info[game.owner] + "</p><p>Fleet Size: " + info[game.shipSize] + "</p><p>Points: " + info[game.shipPoints]
                            + "</p><p>Players: " + (info[game.players].length || 0) + "/" + info[game.maxPlayers] + "</p></div>";
                    }
                }
                document.getElementById("serverList").innerHTML = serversS;
            break;
            case action.update:
                console.log("Update");
                if (currentScene == scenes.game){

                } else if (currentScene == scenes.lobby) {
                    var info = data[field.game];
                    if(info[game.name]) gameInfo.name = info[game.name];
                    if(info[game.owner]) gameInfo.owner = info[game.owner];
                    if(info[game.maxPlayers]) gameInfo.maxPlayers = info[game.maxPlayers];
                    if(info[game.shipSize]) gameInfo.fleetSize = info[game.shipSize];
                    if(info[game.shipPoints]) gameInfo.pointsMax = info[game.shipPoints];
                    if(info[game.players]) {
                        for(var i = 0; i < info[game.players].length; i++){
                            var unfound = true;
                            for(var j = 0; j < gameInfo.players.length; j++){
                                if(gameInfo.players[j].id == info[game.players][i][player.id]){
                                    unfound = false;
                                    gameInfo.players[j].update(info[game.players][i]);
                                    break;
                                }
                            }
                            if(unfound){
                                var play = new gamePlayer(info[game.players][i][player.id]);
                                play.update(info[game.players][i]);
                                gameInfo.players.push(play);
                            }
                        }
                    }
                    document.getElementById("glName").innerText = gameInfo.name;
                    document.getElementById("glOwner").innerText = "Owner: " + gameInfo.owner;
                    document.getElementById("glPlayers").innerText = "Players: " + gameInfo.players.length + "/" + gameInfo.maxPlayers;
                    document.getElementById("glFleetSize").innerText = "Fleet Size: " + gameInfo.fleetSize;
                    setStats();
                }
            break;
        }
    } catch(e){
        console.log(e);
    }
};
function Send(reqObj) {
    console.log("Sending: " + JSON.stringify(reqObj));
    Conn.send(JSON.stringify(reqObj));
}
function getCookieEvent(callback){ //Run when the session cookie is set
    if(!callback.changeInfo.removed && callback.changeInfo.cookie.name == "session"){
        var res = {};
        res[field.action] = action.init;
        res[field.session] = callback.changeInfo.cookie.value;
        Send(res);
        browser.cookies.onChanged.removeListener(getCookieEvent)
    }
}
function getCookie(cook){
    var name = cook + '=';
    var decoded = decodeURI(document.cookie);
    var cookies = decoded.split(';');
    for(var i = 0; i < cookies.length; i++){
        if(cookies[i].indexOf(name) == 0){
            return cookies[i].substr(name.length, cookies[i].length);
        }
    }
    return "";
}
class gamePlayer{
    constructor(id){
        this.id = id;
        this.name = ""
        this.team = 0
        this.ready = false
        this.fleets = []
        this.scouts = []
        document.getElementById("glPlayerInfo").innerHTML += '<div class="gridContainer" id="player'+ this.id +'"><p>Name: '+ this.name 
        +'</p><p>Team: '+ this.team +'</p><p>'+ this.ready +'</p></div>';
    }
    update(info){
        if(info[player.delete]) this.delete();
        if(info[player.name]) this.name = info[player.name];
        if(info[player.team]) this.team = info[player.team];
        if(info[player.fleets]){
            for(var i = 0; i < info[player.fleets].length; i++){
                var unfound = true;
                for(var j = 0; j < this.fleets.length; j++){
                    if(this.fleets[j].id == info[player.fleets][i][fleet.transform][transform.id]){
                        unfound = false;
                        this.fleets[j].update(info[player.fleets][i]);
                        break;
                    }
                }
                if(unfound){
                    var unit = new gameFleet(info[player.fleets][i][fleet.transform][transform.id], this);
                    unit.update(info[player.fleets][i]);
                    this.fleets.push(unit);
                }
            }
        }
        if(info[player.scouts]){
            for(var i = 0; i < info[player.scouts].length; i++){
                var unfound = true;
                for(var j = 0; j < this.scouts.length; j++){
                    if(this.scouts[j].id == info[player.scouts][i][transform.id]){
                        unfound = false;
                        this.scouts[j].update(info[player.scouts][i]);
                        break;
                    }
                }
                if(unfound){
                    var unit = new gameTransform(info[player.scouts][i][transform.id], this);
                    unit.update(info[player.scouts][i]);
                    this.scouts.push(unit);
                }
            }
        }
        document.getElementById('player'+ this.id).innerHTML = '<p>Name: '+ this.name 
        +'</p><p>Team: '+ this.team +'</p><p>'+ this.ready +'</p>';
    }
    get id(){
        return this.id;
    }
    id(x){
        this.id = x;
    }
    delete(){
        gameInfo.players.splice(gameInfo.players.indexOf(this), 1);
        document.getElementById("glPlayers").innerText = "Players: " + gameInfo.players.length + "/" + gameInfo.maxPlayers;
        document.getElementById("player"+ this.id).remove();
    }
}
class gameTransform{
    constructor(id, player){
        this.id = id;
        this.player = player
    }
    update(info){

    }
    delete(){

    }
}
class gameFleet extends gameTransform{
    constructor(id, player){
        this.id = id;
        this.player = player
    }
    update(info){
        super.update(info[fleet.transform])
    }
}
//BUTTONS -----------------------------------------------------------------------------------------------------------
function setName(){
    var name = document.getElementById("userName").value;
    var sendObj = {};
    sendObj[field.action] = action.name;
    sendObj[field.name] = name;
    Send(sendObj);
}
function serverBrowser(){
    var sendObj = {};
    sendObj[field.action] = action.servers;
    Send(sendObj);
}
function makeGame(){
    console.log("Make Game");
    var sendObj = {};
    sendObj[field.action] = action.makeGame;
    var gameObj = {};
    gameObj[game.name] = document.getElementById("mgName").value;
    gameObj[game.maxPlayers] = document.getElementById("mgPlayers").value;
    gameObj[game.shipSize] = document.getElementById("mgFleet").value;
    gameObj[game.shipPoints] = document.getElementById("mgPoints").value;
    sendObj[field.game] = gameObj;
    Send(sendObj);
}
function computePoints(){
    user.attack = parseInt(document.getElementById("glAttack").value) || 0;
    user.defense = parseInt(document.getElementById("glDefense").value) || 0;
    user.speed = parseInt(document.getElementById("glSpeed").value) || 0;
    user.scout = parseInt(document.getElementById("glScout").value) || 0;
    user.points = user.attack + user.defense + user.speed + user.scout;
    document.getElementById("glFleetPoints").innerText = "Points: " + user.points + "/" + gameInfo.pointsMax;
    document.getElementById("glAttack").setAttribute("max", (Math.min(100, gameInfo.pointsMax - user.points + user.attack)));
    document.getElementById("glDefense").setAttribute("max", (Math.min(100, gameInfo.pointsMax - user.points + user.defense)));
    document.getElementById("glSpeed").setAttribute("max", (Math.min(100, gameInfo.pointsMax - user.points + user.speed)));
    document.getElementById("glScout").setAttribute("max", (Math.min(100, gameInfo.pointsMax - user.points + user.scout)));
}
function setStat(stat, sendStats=true){
    computePoints();
    if(user.points > gameInfo.pointsMax){
        document.getElementById("gl" + stat).value = Math.min(100, parseInt(document.getElementById("gl" + stat).value) + gameInfo.pointsMax - user.points || 0);
        computePoints();
    }
    if(sendStats){
        var playerInfo = {};
        playerInfo[player.attack] = user.attack;
        playerInfo[player.defense] = user.defense;
        playerInfo[player.speed] = user.speed;
        playerInfo[player.scout] = user.scout;
        var gInfo = {};
        gInfo[game.players] = [playerInfo];
        var info = {};
        info[field.action] = action.update;
        info[field.game] = gInfo;
        Send(info)
    }
}
function setStats(sendStats=true){
    computePoints();
    if(user.points > gameInfo.pointsMax){
        document.getElementById("glAttack").value = 0;
        document.getElementById("glDefense").value = 0;
        document.getElementById("glSpeed").value = 0;
        document.getElementById("glScout").value = 0;
        computePoints();
    }
    if(sendStats){
        var playerInfo = {};
        playerInfo[player.attack] = user.attack;
        playerInfo[player.defense] = user.defense;
        playerInfo[player.speed] = user.speed;
        playerInfo[player.scout] = user.scout;
        var gInfo = {};
        gInfo[game.players] = [playerInfo];
        var info = {};
        info[field.action] = action.update;
        info[field.game] = gInfo;
        Send(info)
    }
}
function join(gameId){
    var obj = {};
    obj[field.action] = action.join;
    obj[field.game] = {};
    obj[field.game][game.id] = gameId;
    Send(obj);
}
//GAME ----------------------------------------------------------------------------------------------------------------
var delta = 0;
var lastFrameTime = 0;
var MAX_FRAMERATE = 30; //TODO: find a reasonable number for this, 60 is goal
function gameLoop(timestamp){
    if(lastFrameTime == 0){
        lastFrameTime = timestamp;
    }
    delta = timestamp - lastFrameTime;
    if(delta < 1 / MAX_FRAMERATE){
        requestAnimationFrame(gameLoop)
        return
    }
    lastFrameTime = delta;
    //Update, draw
    
    requestAnimationFrame(gameLoop)
}

function start(){
    scene(scenes.start);
}