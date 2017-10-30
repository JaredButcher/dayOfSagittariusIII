var Conn = new WebSocket("ws://" + window.location.hostname + ":8001/sagittarius");

fields = {
    action: 0,
    session: 1
}
actions = {
    ack: 0,
    errorStop: 1,
    errorResend: 2,
    init: 3,
    servers: 4
}

Conn.onopen = function (event) {
    newGame();
};
Conn.onmessage = function (message) {
    console.log(message.data);
    data = JSON.parse(message.data);
};
function Send(reqObj) {
    print("Sending: " + JSON.stringify(reqObj));
    Conn.send(JSON.stringify(reqObj));
}
function newGame() {
    var res = {};
    res[fields.action] = acitons.init;
    res[fields.session] = getCookie("session");
    if(res[fields.session] != ""){
        Send(res);
    }
}
function getCookie(cook){
    var name = cook + '=';
    var decoded = decodeURI(document.cookie);
    var cookies = decoded.split(';');
    for(var i = 0; i < cookies.length; i++){
        if(coockies[i].indexOf(name) == 0){
            return coockies[i].substr(name.length, coockies[i].length);
        }
    }
    return "";
}