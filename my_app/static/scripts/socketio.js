// I am not familiar with js so uh...
var socket = io();
var queryString = window.location.href;
var url = new URL(queryString);
var room = url.searchParams.get("code");
var username = url.searchParams.get("username");
var usernames = [];
var Leader = ""
// Triggers when page loads
document.addEventListener('DOMContentLoaded', () => {
    // Event bucket for when the client connects to the server
    socket.on('connect', function () {
        // Sends a request for a room
        socket.emit('join', {'room': room, 'username': username});
    });
    // Just before the page gets closed, notify server we left.
    window.onbeforeunload = function () {
        if (username == Leader) {
            socket.emit('leave', {'room': room, 'username': username, 'isleader': 1})
        } else {
            socket.emit('leave', {'room': room, 'username': username, 'isleader': 0});
        }
    };
    // Event bucket for when someone else joins the room.
    socket.on('newjoin', data => {
        let index = usernames.indexOf(data);
        if (index === -1) {
            console.log("New player: " + data);
            usernames.push(data);
            document.getElementById("users").innerHTML = usernames;
        } else {
            console.log("Player: " + data + " reconnected.");
        }
    });
    // Event bucket for when someone else leaves the room.
    socket.on('newleave', data => {
        console.log("Player Left: " + data);
        let index = usernames.indexOf(data);
        if (index > -1) {
            usernames.splice(index, 1);
            console.log("Removed player from list")
        }
        document.getElementById("users").innerHTML = usernames;
    });
    // Event bucket for when we join the room and request the current users
    socket.on('curusers', (users, leader) => {
        for (let i in users) {
            usernames.push(users[i]);
        }
        Leader = leader;
        if (username == Leader) {
            document.getElementById("start").style.visibility = "visible";
        }
        console.log(users);
        console.log(leader);
        document.getElementById("users").innerHTML = usernames;
        document.getElementById("leader").innerHTML = leader;
    });
    // Event bucket for when a new leader is selected
    socket.on('newleader', newleader => {
        Leader = newleader;
        console.log("New leader: " + newleader);
        if (username == Leader) {
            document.getElementById("start").style.visibility = "visible";
        }
        document.getElementById("leader").innerHTML = Leader;
    });
    // Event bucket for recieving the start game info
    socket.on('startinfo', (topic, time) => {
        document.getElementById("topic").innerHTML = topic;
        document.getElementById("idea_submition").style.visibility = "visible";
        startTimer(time);
    });
    socket.on('IdeasSent', (ideas) => {
        var docideas = [];
        for (let i in ideas){
            docideas.push(document.createElement("button"));
            docideas[i].innerHTML = ideas[i];
            document.body.appendChild(docideas[i]);
        }
    })
});
// Event handler for start button press
document.getElementById("start").onclick = function () {
    document.getElementById("start").style.visibility = "hidden";
    socket.emit('start', {'room': room});
};
function getIdea() {
    let idea = document.getElementById("ideabox").value;
    document.getElementById("ideabox").value = "";
    socket.emit('newidea', {'user': username, 'room': room, 'idea': idea});
}
function startTimer(duration) {
    var dur = duration;
    var timer = setInterval(function () {
        let minutes = parseInt(dur / 60, 10);
        let seconds = parseInt(dur % 60, 10);

        minutes = minutes < 10 ? "0" + minutes : minutes;
        seconds = seconds < 10 ? "0" + seconds : seconds;

        document.getElementById("timer").textContent = minutes + ":" + seconds;

        if (--dur <= 0) {
            clearInterval(timer);
            document.getElementById("idea_submition").style.visibility = "hidden";
            if(username == Leader) {
                socket.emit('votestart', {'room': room})
            }
        }
    }, 1000);
}

/*
Leader presses go
everyone gets the prompt displayed and a text box for idea submissions
The timer gets displayed and counts down
timer reaches zero, text box disappears.

Leader notifies server when timer is up
Server sends all ideas back
Clients cast vote
winner is displayed
*/