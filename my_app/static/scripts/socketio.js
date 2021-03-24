// I am not familiar with js so uh...

// I believe that when the webpage is loaded by a client this starts socketio
document.addEventListener('DOMContentLoaded', () => {
    var socket = io();

    // Event bucket for when the client connects to the server
    socket.on('connect', function() {
       // Sends a request for a room
       socket.emit('join');
    });

    // Event bucket for when the client has created a room
    socket.on('Create', function() {
        socket.emit()
    })
    // TODO: add event bucket for player joins
    // socket.on('player-join', )
})

// JOIN MAPPING
// If code exists, send room to client, client sends room back to server where the client joins the room. server sends back topic, time limit, and players (use kwargs)
// Socket sends name to all

// CREATE MAPPING
// Send code, topic, time-limit, and username to client. Client sends back id and is added to room.
