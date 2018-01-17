const network = {
    inited: false,
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
        forbidden: "6",
        nameUsed: "7"},
    game: {
        id: "0",
        players: "1", //[player]
        running: "2",
        winner: "3",
        name: "4",
        owner: "5",
        maxPlayers: "6",
        damage: "7",
        shipPoints: "8",
        mode: "9",
        teams: "10",
        map: "11"},
    player: {
        id: "0",
        name: "1",
        team: "2",
        gameObj: "3", //[fleets ]
        primary: "4", //weapon
        primaryAmmo: "5",
        secondary: "6", //weapon
        secondaryAmmo: "7",
        attack: "8",
        defense: "9",
        scout: "10",
        speed: "11",
        isFlagship: "12",
        ships: "13",
        delete: "14"},
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
    gameObj: {
        size: "0",
        type: "1",
        transform: "2"},
    weapon: {
        laser: "0",
        missle: "1",
        rail: "2",
        mine: "3",
        fighter: "4",
        plasma: "5",
        emc: "6",
        jump: "7",
        repair: "8"},
    chatContext: {
        free: "0",
        game: "1",
        team: "2"},
    command: {
        source: "0", //transform
        fire: "1",  //ammo used if applicatble
        target: "2", //transform
        split: "3", //Size of new fleet
        merge: "4",
        weapon: "5"},
    gameMap: {
        height: "0",
        width: "1"},
    objType: {
        fleet: "1",
        scout: "2",
        scoutMove: "3",
        missle: "4",
        plasma: "5",
        rail: "6"},
    conn: new WebSocket("ws://" + window.location.hostname + ":8001/sagittarius"),
    send: function(reqObj) {
        if(!network.inited){
            network.init();
        } else{
            console.log("sending: " + JSON.stringify(reqObj));
            this.conn.send(JSON.stringify(reqObj));
        }
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
        var cookies = decoded.split("; ");
        for(var i = 0; i < cookies.length; i++){
            if(cookies[i].indexOf(name) == 0){
                return cookies[i].substr(name.length, cookies[i].length);
            }
        }
        return "";
    },
    init: function(){
        var res = {};
        console.log("init")
        res[network.field.action] = network.action.init;
        res[network.field.session] = network.getCookie("session");
        if(res[network.field.session] != ""){
            console.log("Cookie")
            network.inited = true;
            network.send(res);
        } else {
            console.log("no")
            if (!chrome){
                console.log(browser);
                browser.cookies.onChanged.addListener(network.getCookieEvent);
            }
        }
    }
};
network.conn.onopen = network.init;
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
                switch(data[network.field.error]){
                    case network.error.nameUsed:
                        if(interface.currentScene == interface.scenes.start){
                            document.getElementById("userNameError").style.visibility = "visible";
                        }
                    break;
                    case network.error.badInit:
                        network.inited = false;
                    break;
                }
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
                sag.gameInfo.damage = info[network.game.damage];
                sag.gameInfo.pointsMax = info[network.game.shipPoints];
                sag.gameInfo.teams = info[network.game.teams];
                sag.gameInfo.players = [];
                for(var i = 0; i < info[network.game.players].length; i++){
                    var play = new player(info[network.game.players][i][network.player.id]);
                    play.update(info[network.game.players][i]);
                    sag.gameInfo.players.push(play);
                    if(play.name == sag.user.name){
                        sag.user.player = play;
                        play.update({});
                    }
                }
                document.getElementById("glName").innerText = sag.gameInfo.name;
                document.getElementById("glOwner").innerText = "Owner: " + sag.gameInfo.owner;
                document.getElementById("glPlayers").innerText = "Players: " + sag.gameInfo.players.length + "/" + sag.gameInfo.maxPlayers;
                document.getElementById("glDamage").innerText = "Damage: " + sag.gameInfo.damage + '%';
                document.getElementById("glAttack").value = 0;
                document.getElementById("glDefense").value = 0;
                document.getElementById("glSpeed").value = 0;
                document.getElementById("glScout").value = 0;
                interface.setStat(null, false);
                interface.weapon("pri", true);
                interface.weapon("sec", true);
                interface.scene(interface.scenes.lobby);
            break;
            case network.action.makeGame:
            break;
            case network.action.name:
                document.getElementById("userNameError").style.visibility = "hidden";
                document.getElementById("nameConfierm").hidden = false;
                document.getElementById("nameConfierm").innerText = "Name set to: " + data[network.field.name];
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
                             + info[network.game.name] + "</p><p>Owner: " + info[network.game.owner] + "</p><p>Damage Multiplyer: " + info[network.game.damage]
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
                    var sendStats = false;
                    var info = data[network.field.game];
                    if(info[network.game.name] != null) sag.gameInfo.name = info[network.game.name];
                    if(info[network.game.owner] != null) sag.gameInfo.owner = info[network.game.owner];
                    if(info[network.game.maxPlayers] != null) sag.gameInfo.maxPlayers = info[network.game.maxPlayers];
                    if(info[network.game.shipSize] != null) sag.gameInfo.fleetSize = info[network.game.shipSize];
                    if(info[network.game.shipPoints] != null) { 
                        sag.gameInfo.pointsMax = info[network.game.shipPoints]; 
                        sendStats = true; 
                    }
                    if(info[network.game.teams] != null) sag.gameInfo.teams = info[network.game.teams];
                    if(info[network.game.players] != null) {
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
                                if(play.name == sag.user.name){
                                    sag.user.player = play;
                                    play.update({});
                                }
                            }
                        }
                    }
                    document.getElementById("glName").innerText = sag.gameInfo.name;
                    document.getElementById("glOwner").innerText = "Owner: " + sag.gameInfo.owner;
                    document.getElementById("glPlayers").innerText = "Players: " + sag.gameInfo.players.length + "/" + sag.gameInfo.maxPlayers;
                    document.getElementById("glDamage").innerText = "Fleet Size: " + sag.gameInfo.fleetSize;
                    interface.setStat("", sendStats);
                    interface.weapon("pri", true);
                    interface.weapon("sec", true);
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
                document.getElementById("mgDamage").value = 100;
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
        document.getElementById("nameConfierm").hidden = true;
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
        gameObj[network.game.damage] = document.getElementById("mgDamage").value;
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
        document.getElementById("attackStats").innerText = "Damage: " + Math.round(100 + sag.user.attack * sag.consts.MOD_ATTACK * 100) + "%";
        document.getElementById("defenseStats").innerText = "Armor: " + Math.round(sag.user.defense * sag.consts.MOD_DEFENSE) + "%";
        document.getElementById("speedStats").innerText = "Speed: " + Math.round((sag.consts.BASE_SPEED + sag.user.speed * sag.consts.MOD_SPEED) * 10) / 10 + " Traverse: " + Math.round((sag.consts.BASE_TRAV + sag.user.speed * sag.consts.MOD_TRAV) * 100) / 100;
        document.getElementById("scoutStats").innerText = "View: " + Math.round(sag.consts.BASE_RANGE + sag.user.scout * sag.consts.MOD_RANGE) + " Scouts: " + Math.floor(sag.consts.BASE_SCOUTS + sag.user.scout * sag.consts.MOD_SCOUTS);
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
    },
    cycleTeam: function(){
        var playerInfo = {};
        playerInfo[network.player.team] = sag.teams[(parseInt(sag.user.player.team.id) + 1) % sag.gameInfo.teams].id;
        var gInfo = {};
        gInfo[network.game.players] = [playerInfo];
        var info = {};
        info[network.field.action] = network.action.update;
        info[network.field.game] = gInfo;
        network.send(info)
    },
    weapon: function(slot, noSend=false, same=false){
        weapon = sag.weapon[document.getElementById(slot + "Sel").value];
        damage = document.getElementById(slot + "Dam");
        ammo = document.getElementById(slot + "Ammo");
        range = document.getElementById(slot + "Range");
        desc = document.getElementById(slot + "Desc");
        damage.hidden = false;
        ammo.hidden = false;
        range.hidden = false;
        desc.hidden = false;
        if(slot == "pri"){
            if(!noSend){
                noSend = sag.user.pri == weapon;
            }
            sag.user.pri = weapon;
        } else{
            if(!noSend){
                noSend = sag.user.sec == weapon;
            }
            sag.user.sec = weapon;
        }
        if(sag.user.pri == sag.user.sec && slot == "sec"){
            damage.hidden = true;
            ammo.hidden = true;
            range.hidden = true;
            desc.hidden = false;
            if("ammo" in weapon){
                desc.innerText = "Incresses ammo of primary weapon";
            } else if(weapon == sag.weapon.ecm) {
                desc.innerText = "Incresses range of primary weapon";
            } else {
                desc.innerText = "Buffs the damage of the primary weapon";
            }
        } else {
            if("damage" in weapon){
                if(sag.user.pri == sag.user.sec){
                    damage.innerText = "Damage/sec: " + Math.round(sag.calcAttack(weapon.damage * 1.5, sag.consts.SHIPS));
                } else {
                    damage.innerText = "Damage/sec: " + Math.round(sag.calcAttack(weapon.damage, sag.consts.SHIPS));
                }
            }
            if("range" in weapon) range.innerText = "Range: " + weapon.range;
            switch(weapon){
                case sag.weapon.laser:
                    ammo.hidden = true;
                    desc.innerText = "Lasers mounted on fully traversable turrents offer a flexable and moderate amount of damage at medium ranges."
                break;
                case sag.weapon.plasma:
                    ammo.hidden = true;
                    desc.innerText = "Large plasma cannons mounted in the bow offer a large amount of damage at medium ranges"
                break;
                case sag.weapon.repair:
                    if(sag.user.pri == sag.user.sec){
                        ammo.innerText = "Supplies: " + weapon.ammo * sag.consts.SHIPS * 2;
                    } else {
                        ammo.innerText = "Supplies: " + weapon.ammo * sag.consts.SHIPS;
                    }
                    damage.innerText = "Repair Speed: " + Math.round(-1 * weapon.damage * sag.consts.SHIPS);
                    desc.innerText = "Massive quanaties of nanobots directed by super computers are directed to repair minor damage, create and replace componets, or even recreate entire ships"
                break;
                case sag.weapon.missle:
                    if(sag.user.pri == sag.user.sec){
                        ammo.innerText = "Ammo: " + weapon.ammo * sag.consts.SHIPS * 2;
                    } else {
                        ammo.innerText = "Ammo: " + weapon.ammo * sag.consts.SHIPS;
                    }
                    damage.innerText = "Damage/volly: " + Math.round(sag.calcAttack(weapon.damage, sag.consts.SHIPS));
                    range.hidden = true;
                    desc.innerText = "A set missle battery that launch powerful self guilded missles over a huge distance, they lose contact if the target is no longer spoted and can be shot down."
                break;
                case sag.weapon.rail:
                    if(sag.user.pri == sag.user.sec){
                        ammo.innerText = "Ammo: " + weapon.ammo * sag.consts.SHIPS * 2;
                    } else {
                        ammo.innerText = "Ammo: " + weapon.ammo * sag.consts.SHIPS;
                    }
                    damage.innerText = "Damage/volly: " + Math.round(sag.calcAttack(weapon.damage, sag.consts.SHIPS));
                    range.hidden = true;
                    desc.innerText = "An electromagetic railgun that streches the length of the ship, it accurity launches powerful projectiles at excessive speeds to just about anywhere, even outside of sensor range."
                break;
                case sag.weapon.ecm:
                    if(sag.user.pri == sag.user.sec){
                        range.innerText = "Range: " + weapon.range * 1.5;
                    }
                    ammo.hidden = true;
                    damage.innerText = "Damage/sec: " + weapon.damage * sag.consts.SHIPS;
                    desc.innerText = "Massive arryes of sensors and antennas along with banks of quantam computes are used to acheive electronic superiority, while active it will double sensor range and destory enemy scout drones and missles within range."
                break;
                case sag.weapon.jump:
                    damage.hidden = true;
                    range.hidden = true;
                    ammo.innerText = "Jump Cores: " + weapon.ammo;
                    desc.innerText = "A large and power-hungry device that uses sheer force to tear a hole though space itself, sensors must be onsite to provide spacel data."
                break;
            }
        }
        if(!same && slot == "pri") {
            interface.weapon("sec", false, true);
        } else if(!same){
            interface.weapon("pri", false, true);
        }
        if(!noSend){
            var playerInfo = {};
            playerInfo[network.player.primary] = sag.user.pri.id;
            playerInfo[network.player.secondary] = sag.user.sec.id;
            var gInfo = {};
            gInfo[network.game.players] = [playerInfo];
            var info = {};
            info[network.field.action] = network.action.update;
            info[network.field.game] = gInfo;
            network.send(info)
        }
    }
};
const sag = {
    user: {
        name: "",
        player: null,
        points: 0,
        attack: 0,
        defense: 0,
        speed: 0,
        scout: 0,
        fleets: [],
        pri: 0,
        sec: 0
    },
    teams: {
        0: {
            id: 0,
            name: "red",
            color: "#ff0000"
        },
        1: {
            id: 1,
            name: "blue",
            color: "#0000ff"
        },
        2: {
            id: 2,
            name: "green",
            color: "#00ff00"
        },
        3: {
            id: 3,
            name: "yellow",
            color: "#ffff00"
        }
    },
    gameInfo: {
        id: "",
        name: "",
        owner: "",
        teams: 1,
        pointsMax: 0,
        players: [],
        maxPlayers: 0,
        damage: 0
    },
    weapon: {
        laser: {
            damage: 0.05,
            range: 100,
            id: network.weapon.laser
        },
        plasma: {
            damage: 0.1,
            range: 100,
            speed: 100,
            id: network.weapon.plasma
        },
        rail: {
            damage: 0.05,
            ammo: 50,
            speed: 250,
            id: network.weapon.rail
        },
        missle: {
            damage: 0.1,
            ammo: 20,
            speed: 50,
            id: network.weapon.missle
        },
        ecm: {
            damage: 0.02,
            range: 200,
            spotting: 2,
            id: network.weapon.ecm
        },
        jump: {
            ammo: 10,
            id: network.weapon.jump
        },
        repair: {
            damage: -0.01,
            range: 100,
            ammo: 1,
            id: network.weapon.repair
        },
        mine: {

        },
        fighter: {

        }
    },
    consts: {
        SHIPS: 15000,
        BASE_SPEED: 10,
        BASE_TRAV: Math.PI / 4,
        BASE_SCOUTS: 10,
        BASE_RANGE: 50,
        BASE_ATTACK: 1,
        BASE_DEFENSE: 1,
        MOD_SPEED: .2,
        MOD_TRAV: Math.PI / 50,
        MOD_ATTACK: .01,
        MOD_DEFENSE: 2/3,
        MOD_SCOUTS: .1,
        MOD_RANGE: .5
    },
    calcAttack: function(base, ships){
        return base * (1 + sag.user.attack * sag.consts.MOD_ATTACK) * sag.gameInfo.damage / 100 * ships;
    },
    calcDefense: function(damage){
        return damage / (sag.user.defense * sag.consts.MOD_DEFENSE);
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
        this.name = "";
        this.team = sag.teams[0];
        this.ready = false;
        this.gameObjs = [];
        document.getElementById("glPlayerInfo").innerHTML += '<div class="gridContainer, player" id="player'+ this.id +'"><p>Name: '+ this.name 
        +'</p>' + this.teamButton() + '<p>'+ this.ready +'</p></div>';
    }
    update(info={}){
        if(info[network.player.name] != null) this.name = info[network.player.name];
        if(info[network.player.team] != null) this.team = sag.teams[info[network.player.team]];
        if(info[network.player.gameObj] != null){
            for(var i = 0; i < info[network.player.gameObj].length; i++){
                var unfound = true;
                for(var j = 0; j < this.fleets.length; j++){
                    if(this.gameObj[j].id == info[network.player.gameObj][i][network.gameObj.transform][network.transform.id]){
                        unfound = false;
                        this.gameObj[j].update(info[network.player.gameObj][i]);
                        break;
                    }
                }
                if(unfound){
                    var unit;
                    switch(info[network.player.gameObj][i][network.gameObj.type]){
                        case network.objType.fleet:
                            unit = new fleet(info[network.player.gameObj][i][network.gameObj.transform][network.transform.id], this);
                        break;
                        case network.objType.scout:
                            unit = new scout(info[network.player.gameObj][i][network.gameObj.transform][network.transform.id], this);
                        break;
                        //TODO add rest of types
                        default:
                            unit = new transform(info[network.player.gameObj][i][network.gameObj.transform][network.transform.id], this);
                        break;
                    }
                    unit.update(info[network.player.gameObj][i]);
                    this.gameObj.push(unit);
                }
            }
        }
        document.getElementById('player'+ this.id).innerHTML = '<p>Name: '+ this.name +'</p>' + this.teamButton() + '<p>'+ this.ready +'</p>';
        if(info[network.player.delete] != null) this.delete();
    }
    get id(){
        return this.id;
    }
    id(x){
        this.id = x;
    }
    teamButton(){
        return '<lable>Team: </lable><button style="background-color: ' + this.team.color + ';"' + (this == sag.user.player ? 'id="team'
         + this.id + '" onclick="interface.cycleTeam();"' : '') + '>' + this.team.name + '</button>'
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
        super.transform(id, player);
    }
    update(info){
        super.update(info[network.gameObj.transform]);
    }
};
class scout extends transform{

};
