// I am not familiar with js so uh...

// I believe that when the webpage is loaded by a client this starts socketio
document.addEventListener('DOMContentLoaded', () => {
    var socket = io();

    // Event bucket for when the client connects to the server
    socket.on('connect', function() {
       // Sends data to server's message event bucket
       socket.emit('message', {data: 'I\'m connected!'});
    });

    // TODO: add event bucket for player joins
    // socket.on('player-join', )
})
