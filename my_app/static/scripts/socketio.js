// I am not familiar with js so uh...

// I believe that when the webpage is loaded by a client this starts socketio
document.addEventListener('DOMContentLoaded', () => {
    var socket = io();
    // Event bucket for when the client connects to the server
    socket.on('connect', function() {
        var queryString = window.location.href;
        var url = new URL(queryString);
        var room = url.searchParams.get("code");
        var username = url.searchParams.get("username")
       // Sends a request for a room
       socket.emit('join', {'room': room, 'username': username});
    });
    socket.on('newjoin', data => {
        console.log("New player: " + data)
        var usernames = document.getElementById("users").innerHTML;
        document.getElementById("users").innerHTML = usernames + " " + data;
    });
    socket.on('curusers', data => {
        document.getElementById("users").innerHTML = data;
    });

});


// JOIN MAPPING
// If code exists, send room to client, client sends room back to server where the client joins the room. server sends back topic, time limit, and players (use kwargs)
// Socket sends name to all

// CREATE MAPPING
// Send code, topic, time-limit, and username to client. Client sends back id and is added to room.