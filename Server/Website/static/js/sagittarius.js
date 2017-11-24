var field = {
    action: 0,
    session: 1,
    servers: 2,
    gameId: 3,
    game: 4,
    chatContext: 5,
    chatMessage: 6,
    team: 7,
    name: 8,
    transform: 9,
    error: 10
};
var action = {
    ack: 0,
    error: 1,
    update: 2,
    init: 3,
    servers: 4,
    join: 5,
    name: 6,
    makeGame: 7,
    chat: 8,
    joinTeam: 9,
    command: 10
};
var error = {
    repeat: 0,
    stop: 1,
    joinFail: 2,
    createFail: 3
};
var browser = {
    id: 0,
    name: 1,
    owner: 2,
    players: 3,
    maxPlayers: 4,
    fleetSize: 5,
    fleetPoints: 6,
    gameMode: 7,
    teams: 8
};
var game = {
    browserInfo: 0, 
    players: 1,
    running: 2,
    winner: 3
};
var player = {
    id: 0,
    name: 1,
    team: 2,
    fleets: 3, 
    scouts: 4,
    primary: 5,
    primaryAmmo: 6,
    secondary: 7,
    secondaryAmmo: 8,
    attack: 9,
    defense: 10,
    scout: 11,
    speed: 12,
    isFlagship: 13
};
var transform = {
    id: 0,
    position: 1, 
    rotation: 2,
    velocity: 3,
    hide: 4,
    destory: 5,
    target: 6
};
var fleet = {
    size: 0,
    transform: 1
};
var weapon = {
    lazer: 0,
    missle: 1,
    rail: 2,
    mine: 3,
    fighter: 4,
    plazma: 5,
    emc: 6,
    jump: 7
};
var chatContext = {
    browser: 0,
    game: 1,
    team: 2
};
var command = {
    destination: 0,
    fire: 1,
    target: 2,
    split: 3,
    merge: 4 
};

var Conn = new WebSocket("ws://" + window.location.hostname + ":8001/sagittarius");

Conn.onopen = function (event) {
    var res = {};
    res[field.action] = action.init;
    res[field.session] = getCookie("session");
    if(res[field.session] != ""){
        Send(res);
    } else {
        browser.cookies.onChanged.addListener(getCookieEvent);
    }
};
Conn.onmessage = function (message) {
    console.log(message.data);
    try{
        data = JSON.parse(message.data);
        console.log(data);
    } catch(e){
        
    }
};
function Send(reqObj) {
    console.log("Sending: " + JSON.stringify(reqObj));
    Conn.send(JSON.stringify(reqObj));
}
function getCookieEvent(callback){
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