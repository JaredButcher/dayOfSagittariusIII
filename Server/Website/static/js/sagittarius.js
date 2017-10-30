var Conn = new WebSocket("ws://" + window.location.hostname + ":8001/sagittarius");

var fields = {
    action: 0,
    session: 1
}
var actions = {
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
    res[fields.action] = actions.init;
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
        if(cookies[i].indexOf(name) == 0){
            return cookies[i].substr(name.length, cookies[i].length);
        }
    }
    return "";
}