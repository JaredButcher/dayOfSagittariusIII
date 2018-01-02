const field = {
    action: "0",
    session: "1",
    servers: "2" ,
    gameId: "3",
    game: "4" ,
    chatContext: "5",
    chatMessage: "6",
    team: "7",
    name: "8",
    transform: "9",
    error: "10"}
const action = {
    ack: "0",
    error: "1",
    update: "2",
    init: "3",
    servers: "4",
    join: "5",
    name: "6",
    makeGame: "7",
    chat: "8",
    joinTeam: "9",
    command: "10"}
const error = {
    repeat: "0",
    stop: "1",
    joinFail: "2",
    createFail: "3",
    badRequest: "4",
    badInitalConn: "5"}
const browser = {
    id: "0",
    name: "1",
    owner: "2",
    players: "3",
    maxPlayers: "4",
    fleetSize: "5",
    fleetPoints: "6",
    gameMode: "7",
    teams: "8"}
const game = {
    browserInfo: "0" ,
    players: "1" ,
    running: "2",
    winner: "3"}
const player = {
    id: "0",
    name: "1",
    team: "2",
    fleets: "3" ,
    scouts: "4" ,
    primary: "5" ,
    primaryAmmo: "6",
    secondary: "7" ,
    secondaryAmmo: "8",
    attack: "9",
    defense: "10",
    scout: "11",
    speed: "12",
    isFlagship: "13" }
const transform = {
    id: "0",
    position: "1" ,
    rotation: "2" ,
    velocity: "3" ,
    hide: "4",
    destory: "5",
    rVelocity: "6" }
const fleet = {
    size: "0",
    transform: "1" }
const weapon = {
    lazer: "0",
    missle: "1",
    rail: "2",
    mine: "3",
    fighter: "4",
    plazma: "5",
    emc: "6",
    jump: "7" }
const chatContext = {
    browser: "0",
    game: "1",
    team: "2" }
const command = {
    destination: "0",
    fire: "1",
    target: "2" ,
    split: "3",
    merge: "4"}

const scenes = {
    start: 0,
    makeGame: 1,
    servers: 2,
    lobby: 3,
    game: 4
};

var currentScene;
var user = {
    name: "",
    points: 0,
    attack: 0,
    defense: 0,
    speed: 0,
    scout: 0,
    fleets: [],
};
var gameInfo = {
    id: "",
    name: "",
    owner: "",
    pointsMax: 0,
    playerCount: 0,
    maxPlayers: 0,
    fleetSize: 0
};

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
        console.log("Action" + data[field.action]);
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
                var info = data[field.game][game.browserInfo];
                console.log(info);
                gameInfo.id = info[browser.id];
                gameInfo.name = info[browser.name];
                gameInfo.owner = info[browser.owner];
                gameInfo.maxPlayers = info[browser.maxPlayers];
                gameInfo.fleetSize = info[browser.fleetSize];
                gameInfo.pointsMax = info[browser.fleetPoints];
                gameInfo.playerCount = (info[browser.players] == []) ? 0 : info[browser.players].length;
                document.getElementById("glName").innerText = gameInfo.name;
                document.getElementById("glOwner").innerText = "Owner: " + gameInfo.owner;
                document.getElementById("glPlayers").innerText = "Players: " + gameInfo.playerCount + "/" + gameInfo.maxPlayers;
                document.getElementById("glFleetSize").innerText = "Fleet Size: " + gameInfo.fleetSize;
                document.getElementById("glAttack").value = 0;
                document.getElementById("glDefense").value = 0;
                document.getElementById("glSpeed").value = 0;
                document.getElementById("glScout").value = 0;
                setStat("Attack");
                setStat("Defense");
                setStat("Speed");
                setStat("Scout");
                scene(scenes.lobby);
            break;
            case action.joinTeam:
            break;
            case action.makeGame:
            break;
            case action.name:
                document.getElementById("userNameError").hidden = true;
                var buttons = document.getElementsByClassName("startNav");
                for(var i = 0; i < buttons.length; ++i){
                    buttons[i].disabled = false;
                }
                user.name = data[field.name];
                document.getElementById("userName").value = user.name;
            break;
            case action.servers:
                var serversS = "";
                if(data[field.servers] == null){
                    serversS = "<div><h2>No games avaliable<h2></div>";
                } else {
                    var info = {}
                    for(var i = 0; i < data[field.servers].length; ++i){
                        info = data[field.servers][i][game.browserInfo];
                        serversS += '<div class="serverInfo"><p>ID: ' + info[browser.id] + "</p><p>Name: " + info[browser.name] + "</p><p>Owner: " + info[browser.owner]
                            + "</p><p>Fleet Size: " + info[browser.fleetSize] + "</p><p>Points: " + info[browser.fleetPoints]
                            + "</p><p>Players: " + (info[browser.players].length || 0) + "/" + info[browser.maxPlayers] + "</p></div>";
                    }
                }
                document.getElementById("serverList").innerHTML = serversS;
            break;
            case action.update:
                if (currentScene = scenes.game){

                } else {

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
    var sendObj = {};
    sendObj[field.action] = action.makeGame;
    var browObj = {};
    browObj[browser.name] = document.getElementById("mgName").value;
    browObj[browser.maxPlayers] = document.getElementById("mgPlayers").value;
    browObj[browser.fleetSize] = document.getElementById("mgFleet").value;
    browObj[browser.fleetPoints] = document.getElementById("mgPoints").value;
    var gameObj = {};
    gameObj[game.browserInfo] = browObj;
    sendObj[field.game] = gameObj;
    Send(sendObj);
}
function computePoints(){
    user.attack = parseInt(document.getElementById("glAttack").value);
    user.defense = parseInt(document.getElementById("glDefense").value);
    user.speed = parseInt(document.getElementById("glSpeed").value);
    user.scout = parseInt(document.getElementById("glScout").value);
    user.points = user.attack + user.defense + user.speed + user.scout;
    document.getElementById("glFleetPoints").innerText = "Points: " + user.points + "/" + gameInfo.pointsMax;
}
function setStat(stat){
    computePoints();
    if(user.points > gameInfo.pointsMax){
        document.getElementById("gl" + stat).value = parseInt(document.getElementById("gl" + stat).value) + gameInfo.pointsMax - user.points;
        computePoints();
    }
    document.getElementById("gl" + stat + "L").innerText = stat + "(" + user[stat.toLowerCase()] + "/" + gameInfo.pointsMax + ")";
    document.getElementById("gl" + stat).setAttribute("max", (gameInfo.pointsMax - user.points));
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