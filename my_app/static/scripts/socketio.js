// I am not familiar with js so uh...

// I believe that when the webpage is loaded by a client this starts socketio
document.addEventListener('DOMContentLoaded', () => {
    var socket = io();

    var usernames = [];
    var queryString = window.location.href;
    var url = new URL(queryString);
    var room = url.searchParams.get("code");
    var username = url.searchParams.get("username");
    var Leader = "Loading..."

    // Event bucket for when the client connects to the server
    socket.on('connect', function() {
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
    }
    // Event bucket for when someone else joins the room.
    socket.on('newjoin', data => {
        console.log("New player: " + data);
        usernames.push(data);
        document.getElementById("users").innerHTML = usernames;
    });
    // Event bucket for when someone else leaves the room.
    socket.on('newleave', data => {
        console.log("Player Left: " + data);
        var index = usernames.indexOf(data);
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
        console.log(users);
        console.log(leader);
        document.getElementById("users").innerHTML = usernames;
        document.getElementById("leader").innerHTML = leader;
    });
    // Event bucket for when a new leader is selected
    socket.on('newleader', newleader => {
        console.log("New leader: " + newleader);
        document.getElementById("leader").innerHTML = newleader;
    });
});
