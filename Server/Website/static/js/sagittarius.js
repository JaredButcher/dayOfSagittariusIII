const network = {
    field: {
        action: "0",
        session: "1",
        servers: "2", //[browser]
        game: "3", //game
        chatContext: "4",
        chatMessage: "5",
        name: "6",
        error: "7"},
    action: {
        error: "1",
        update: "2",
        init: "3",
        servers: "4",
        join: "5",
        name: "6",
        makeGame: "7",
        chat: "8",
        command: "9"},
    error: {
        repeat: "0",
        stop: "1",
        badRequest: "2",
        joinFail: "3",
        createFail: "4",
        badInit: "5",
        forbidden: "6"},
    game: {
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
        map: "11"},
    player: {
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
        delete: "15"},
    transform: {
        id: "0",
        pos: "1", //{x,y}
        rot: "2", 
        targetPos: "3", //{x,y}
        targetRot: "4",
        posV: "5", //{x,y}
        rotV: "6", 
        hide: "7",
        destory: "8"},
    fleet: {
        size: "0",
        transform: "1"},
    weapon: {
        lazer: "0",
        missle: "1",
        rail: "2",
        mine: "3",
        fighter: "4",
        plazma: "5",
        emc: "6",
        jump: "7",
        point: "8"},
    chatContext: {
        free: "0",
        game: "1",
        team: "2"},
    command: {
        source: "0", //transform
        fire: "1",  //ammo used if applicatble
        target: "2", //transform
        split: "3", //Size of new fleet
        merge: "4"},
    gameMap: {
        height: "0",
        width: "1"},
    conn: new WebSocket("ws://" + window.location.hostname + ":8001/sagittarius"),
    send: function(reqObj) {
        console.log("sending: " + JSON.stringify(reqObj));
        this.conn.send(JSON.stringify(reqObj));
    },
    getCookieEvent: function (callback){ //Run when the session cookie is set
        if(!callback.changeInfo.removed && callback.changeInfo.cookie.name == "session"){
            var res = {};
            res[field.action] = action.init;
            res[field.session] = callback.changeInfo.cookie.value;
            send(res);
            browser.cookies.onChanged.removeListener(getCookieEvent)
        }
    },
    getCookie: function(cook){
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
};
network.conn.onopen = function (event) {
    var res = {};
    //send cookie or wait to receive one
    res[network.field.action] = network.action.init;
    res[network.field.session] = network.getCookie("session");
    if(res[network.field.session] != ""){
        network.send(res);
    } else {
        browser.cookies.onChanged.addListener(getCookieEvent);
    }
};
network.conn.onmessage = function (message) { //Receive and direct or process all socket messages
    console.log(message.data);
    var data = null;
    try{
        data = JSON.parse(message.data);
    } catch(e){
        console.log(e);
    }
    if(data){
        switch(data[network.field.action]){
            case network.action.ack:
            break;
            case network.action.chat:
            break;
            case network.action.command:
            break;
            case network.action.error:
            break;
            case network.action.init:
            break;
            case network.action.join:
                console.log("Join");
                document.getElementById("glPlayerInfo").innerHTML = "";
                var info = data[network.field.game];
                sag.gameInfo.id = info[network.game.id];
                sag.gameInfo.name = info[network.game.name];
                sag.gameInfo.owner = info[network.game.owner];
                sag.gameInfo.maxPlayers = info[network.game.maxPlayers];
                sag.gameInfo.fleetSize = info[network.game.shipSize];
                sag.gameInfo.pointsMax = info[network.game.shipPoints];
                sag.gameInfo.players = [];
                for(var i = 0; i < info[network.game.players].length; i++){
                    var play = new player(info[network.game.players][i][network.player.id]);
                    play.update(info[network.game.players][i]);
                    sag.gameInfo.players.push(play);
                }
                document.getElementById("glName").innerText = sag.gameInfo.name;
                document.getElementById("glOwner").innerText = "Owner: " + sag.gameInfo.owner;
                document.getElementById("glPlayers").innerText = "Players: " + sag.gameInfo.players.length + "/" + sag.gameInfo.maxPlayers;
                document.getElementById("glFleetSize").innerText = "Fleet Size: " + sag.gameInfo.fleetSize;
                document.getElementById("glAttack").value = 0;
                document.getElementById("glDefense").value = 0;
                document.getElementById("glSpeed").value = 0;
                document.getElementById("glScout").value = 0;
                interface.setStat(null, false);
                interface.scene(interface.scenes.lobby);
            break;
            case network.action.joinTeam:
            break;
            case network.action.makeGame:
            break;
            case network.action.name:
                console.log("Name");
                document.getElementById("userNameError").hidden = true;
                var buttons = document.getElementsByClassName("startNav");
                for(var i = 0; i < buttons.length; ++i){
                    buttons[i].disabled = false;
                }
                sag.user.name = data[network.field.name];
                document.getElementById("userName").value = sag.user.name;
            break;
            case network.action.servers:
                console.log("Servers");
                var servers = "";
                if(data[network.field.servers] == null){
                    servers = "<div><h2>No games avaliable<h2></div>";
                } else {
                    var info = {}
                    for(var i = 0; i < data[network.field.servers].length; ++i){
                        info = data[network.field.servers][i];
                        servers += '<div class="serverInfo" onclick="interface.join(' + info[network.game.id] + ');"><p>ID: ' + info[network.game.id] + "</p><p>Name: "
                             + info[network.game.name] + "</p><p>Owner: " + info[network.game.owner] + "</p><p>Fleet Size: " + info[network.game.shipSize]
                             + "</p><p>Points: " + info[network.game.shipPoints] + "</p><p>Players: " + (info[network.game.players].length || 0) + "/"
                             + info[network.game.maxPlayers] + "</p></div>";
                    }
                }
                document.getElementById("serverList").innerHTML = servers;
            break;
            case network.action.update:
                console.log("Update");
                if (interface.currentScene == interface.scenes.game){

                } else if (interface.currentScene == interface.scenes.lobby) {
                    var info = data[network.field.game];
                    if(info[network.game.name]) sag.gameInfo.name = info[network.game.name];
                    if(info[network.game.owner]) sag.gameInfo.owner = info[network.game.owner];
                    if(info[network.game.maxPlayers]) sag.gameInfo.maxPlayers = info[network.game.maxPlayers];
                    if(info[network.game.shipSize]) sag.gameInfo.fleetSize = info[network.game.shipSize];
                    if(info[network.game.shipPoints]) sag.gameInfo.pointsMax = info[network.game.shipPoints];
                    if(info[network.game.players]) {
                        for(var i = 0; i < info[network.game.players].length; i++){
                            var unfound = true;
                            for(var j = 0; j < sag.gameInfo.players.length; j++){
                                if(sag.gameInfo.players[j].id == info[network.game.players][i][network.player.id]){
                                    unfound = false;
                                    sag.gameInfo.players[j].update(info[network.game.players][i]);
                                    break;
                                }
                            }
                            if(unfound){
                                var play = new player(info[network.game.players][i][network.player.id]);
                                play.update(info[network.game.players][i]);
                                sag.gameInfo.players.push(play);
                            }
                        }
                    }
                    document.getElementById("glName").innerText = sag.gameInfo.name;
                    document.getElementById("glOwner").innerText = "Owner: " + sag.gameInfo.owner;
                    document.getElementById("glPlayers").innerText = "Players: " + sag.gameInfo.players.length + "/" + sag.gameInfo.maxPlayers;
                    document.getElementById("glFleetSize").innerText = "Fleet Size: " + sag.gameInfo.fleetSize;
                    interface.setStat();
                }
            break;
        }
    }
};
const interface = {
    scenes: {
        start: 0,
        makeGame: 1,
        servers: 2,
        lobby: 3,
        game: 4
    },
    currentScene: null,
    scene: function(current){ //Changes Scene
        document.getElementById("start").hidden = true;
        document.getElementById("makeGame").style.display = "none";
        document.getElementById("servers").hidden = true;
        document.getElementById("lobby").style.display = "none";
        document.getElementById("game").hidden = true;
        switch(current){
            case this.scenes.start:
            document.getElementById("start").hidden = false;
            var buttons = document.getElementsByClassName("startNav"); //CSS display overides the html hidden attribute
            for(var i = 0; i < buttons.length; ++i){
                buttons[i].disabled = true;
            }
            break;
            case this.scenes.makeGame:
                document.getElementById("makeGame").style.display = "grid";
                document.getElementById("mgName").value = sag.user.name + "`s game";
                document.getElementById("mgPlayers").value = 6;
                document.getElementById("mgFleet").value = 10000;
                document.getElementById("mgPoints").value = 200;
            break;
            case this.scenes.servers:
                document.getElementById("servers").hidden = false;
                this.serverBrowser();
            break;
            case this.scenes.lobby:
                document.getElementById("lobby").style.display = "grid";
            break;
            case this.scenes.game:
                document.getElementById("game").hidden = false;
            break;
        }
        this.currentScene = current;
    },
    //BUTTONS -----------------------------------------------------------------------------------------------------------
    setName: function(){
        var name = document.getElementById("userName").value;
        var sendObj = {};
        sendObj[network.field.action] = network.action.name;
        sendObj[network.field.name] = name;
        network.send(sendObj);
    },
    serverBrowser: function(){
        var sendObj = {};
        sendObj[network.field.action] = network.action.servers;
        network.send(sendObj);
    },
    makeGame: function(){
        console.log("Make Game");
        var sendObj = {};
        sendObj[network.field.action] = network.action.makeGame;
        var gameObj = {};
        gameObj[network.game.name] = document.getElementById("mgName").value;
        gameObj[network.game.maxPlayers] = document.getElementById("mgPlayers").value;
        gameObj[network.game.shipSize] = document.getElementById("mgFleet").value;
        gameObj[network.game.shipPoints] = document.getElementById("mgPoints").value;
        sendObj[network.field.game] = gameObj;
        network.send(sendObj);
    },
    computePoints: function(){
        sag.user.attack = parseInt(document.getElementById("glAttack").value) || 0;
        sag.user.defense = parseInt(document.getElementById("glDefense").value) || 0;
        sag.user.speed = parseInt(document.getElementById("glSpeed").value) || 0;
        sag.user.scout = parseInt(document.getElementById("glScout").value) || 0;
        sag.user.points = sag.user.attack + sag.user.defense + sag.user.speed + sag.user.scout;
        document.getElementById("glFleetPoints").innerText = "Points: " + sag.user.points + "/" + sag.gameInfo.pointsMax;
        document.getElementById("glAttack").setAttribute("max", (Math.min(100, sag.gameInfo.pointsMax - sag.user.points + sag.user.attack)));
        document.getElementById("glDefense").setAttribute("max", (Math.min(100, sag.gameInfo.pointsMax - sag.user.points + sag.user.defense)));
        document.getElementById("glSpeed").setAttribute("max", (Math.min(100, sag.gameInfo.pointsMax - sag.user.points + sag.user.speed)));
        document.getElementById("glScout").setAttribute("max", (Math.min(100, sag.gameInfo.pointsMax - sag.user.points + sag.user.scout)));
    },
    setStat: function(stat="", sendStats=true){
        this.computePoints();
        if(sag.user.points > sag.gameInfo.pointsMax){
            if(stat==""){
                document.getElementById("glAttack").value = 0;
                document.getElementById("glDefense").value = 0;
                document.getElementById("glSpeed").value = 0;
                document.getElementById("glScout").value = 0;
            } else {
                document.getElementById("gl" + stat).value = Math.min(100, parseInt(document.getElementById("gl" + stat).value) + sag.gameInfo.pointsMax - sag.user.points || 0);
            }
            this.computePoints();
        }
        if(sendStats){
            var playerInfo = {};
            playerInfo[network.player.attack] = sag.user.attack;
            playerInfo[network.player.defense] = sag.user.defense;
            playerInfo[network.player.speed] = sag.user.speed;
            playerInfo[network.player.scout] = sag.user.scout;
            var gInfo = {};
            gInfo[network.game.players] = [playerInfo];
            var info = {};
            info[network.field.action] = network.action.update;
            info[network.field.game] = gInfo;
            network.send(info)
        }
    },
    join: function(gameId){
        var obj = {};
        obj[network.field.action] = network.action.join;
        obj[network.field.game] = {};
        obj[network.field.game][network.game.id] = gameId;
        network.send(obj);
    },
    start: function(){
        this.scene(this.scenes.start);
    }
};
const sag = {
    user: {
        name: "",
        points: 0,
        attack: 0,
        defense: 0,
        speed: 0,
        scout: 0,
        fleets: []
    },
    gameInfo: {
        id: "",
        name: "",
        owner: "",
        pointsMax: 0,
        players: [],
        maxPlayers: 0,
        fleetSize: 0
    },
    //GAME ----------------------------------------------------------------------------------------------------------------
    delta: 0,
    lastFrameTime: 0,
    MAX_FRAMERATE: 30, //TODO: find a reasonable number for this, 60 is goal
    loop: function(timestamp){
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
};
class player{
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
        if(info[network.player.name]) this.name = info[network.player.name];
        if(info[network.player.team]) this.team = info[network.player.team];
        if(info[network.player.fleets]){
            for(var i = 0; i < info[network.player.fleets].length; i++){
                var unfound = true;
                for(var j = 0; j < this.fleets.length; j++){
                    if(this.fleets[j].id == info[network.player.fleets][i][network.fleet.transform][network.transform.id]){
                        unfound = false;
                        this.fleets[j].update(info[network.player.fleets][i]);
                        break;
                    }
                }
                if(unfound){
                    var unit = new fleet(info[network.player.fleets][i][network.fleet.transform][network.transform.id], this);
                    unit.update(info[network.player.fleets][i]);
                    this.fleets.push(unit);
                }
            }
        }
        if(info[network.player.scouts]){
            for(var i = 0; i < info[network.player.scouts].length; i++){
                var unfound = true;
                for(var j = 0; j < this.scouts.length; j++){
                    if(this.scouts[j].id == info[network.player.scouts][i][network.transform.id]){
                        unfound = false;
                        this.scouts[j].update(info[network.player.scouts][i]);
                        break;
                    }
                }
                if(unfound){
                    var unit = new transform(info[network.player.scouts][i][network.transform.id], this);
                    unit.update(info[network.player.scouts][i]);
                    this.scouts.push(unit);
                }
            }
        }
        document.getElementById('player'+ this.id).innerHTML = '<p>Name: '+ this.name 
        +'</p><p>Team: '+ this.team +'</p><p>'+ this.ready +'</p>';
        if(info[network.player.delete]) this.delete();
    }
    get id(){
        return this.id;
    }
    id(x){
        this.id = x;
    }
    delete(){
        sag.gameInfo.players.splice(sag.gameInfo.players.indexOf(this), 1);
        document.getElementById("glPlayers").innerText = "Players: " + sag.gameInfo.players.length + "/" + sag.gameInfo.maxPlayers;
        document.getElementById("player"+ this.id).remove();
    }
};
class transform{
    constructor(id, player){
        this.id = id;
        this.player = player
    }
    update(info){

    }
    delete(){

    }
};
class fleet extends transform{
    constructor(id, player){
        this.id = id;
        this.player = player
    }
    update(info){
        super.update(info[network.fleet.transform])
    }
};
