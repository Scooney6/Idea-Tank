from random import randint
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, join_room, leave_room, emit
from my_app.WTForms import *


app = Flask(__name__)  # Flask init
app.secret_key = config.secret_key
socketio = SocketIO(app)  # SocketIO init


# MySQL Connection helper function
def connect():
    return mysql.connector.connect(user=config.user, password=config.password,
                                   host=config.host,
                                   database=config.database)


# index goes to /home just because
@app.route("/", methods=["POST", "GET"])
def index():
    return redirect("/home")


# home route renders the home join or create form
@app.route("/home", methods=["POST", "GET"])
def home():
    # instantiate the form
    home_join_form = HomeJoinForm(request.form)
    if request.method == "POST":
        # if the create form is submitted
        if request.form.get("Create"):
            return redirect("/create")
        # if the home form is submitted and is valid
        elif home_join_form.validate():
            code = home_join_form.join_code.data
            username = home_join_form.username.data
            # enter the user to the db as not a leader
            with connect() as con:
                print("Inserting " + username + " in room " + str(code) + " and is not the leader")
                cur = con.cursor()
                cur.execute("INSERT INTO Users (RoomID, Username, IsLeader) VALUES (%s, %s, %s)",
                            (code, username, False))
                con.commit()
            return redirect(url_for("lobby", code=code, username=username))
        # otherwise render the home page again with errors if necessary
        else:
            return render_template("home.html", form=home_join_form)
    # otherwise render home with form
    else:
        return render_template("home.html", form=home_join_form)


# create route renders create lobby form
@app.route("/create", methods=["POST", "GET"])
def create():
    # instantiate create form
    create_form = CreateForm()
    # if the create form is submitted and valid
    if create_form.validate_on_submit():
        code = create_code()
        username = create_form.username.data
        time = create_form.time_limit.data
        topic = create_form.topic.data
        # add the user to the db as the leader of this room
        with connect() as con:
            cur = con.cursor()
            print("Inserting " + username + " in room " + str(code) + " and is the leader")
            cur.execute("INSERT INTO Rooms (RoomID, Topic, TimeLimit) VALUES (%s, %s, %s)", (code, topic, time))
            con.commit()
            cur.execute("INSERT INTO Users (RoomID, Username, IsLeader) VALUES (%s, %s, %s)", (code, username, True))
            con.commit()
        return redirect(url_for("lobby", code=code, username=username))
    # otherwise render the template with instantiated form and errors if necessary
    else:
        return render_template("create.html", form=create_form)


# render the lobby with the code, everything else is taken care of with js
@app.route("/lobby", methods=["POST", "GET"])
def lobby():
    cd = request.args.get('code')
    return render_template("lobby.html", code=cd)


# Event bucket for when the client connects
@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    # put the user in their socketio room
    join_room(room)
    # get the current users and leader from the db
    with connect() as con:
        cur = con.cursor()
        # Retrieves list of tuples of usernames in room
        cur.execute("SELECT Username FROM Users WHERE RoomID = %s", (room,))
        users = cur.fetchall()
        # Makes users just a list of strings
        for i in range(0, len(users)):
            users[i] = users[i][0]
        cur.execute("SELECT Username FROM Users WHERE RoomID = %s AND IsLeader = %s",
                    (room, True))  # Retrieves a tuple of the leader's username
        leader = cur.fetchone()[0]  # [0] Converts tuple to string
        print("Retreived " + str(users) + " and the leader " + leader + " for the user " + username)
    # Send the username of the player that just connected to everyone in the room except the new player
    emit('newjoin', username, room=room, include_self=False)
    # Send the current users and the leader to the new player
    emit('curusers', (users, leader), room=request.sid)


# Event bucket for when a client disconnects
@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    isleader = data['isleader']
    # Make the user leave their socketio room
    leave_room(room)
    # Remove them from the db
    with connect() as con:
        cur = con.cursor()
        cur.execute("DELETE FROM Users WHERE Username = %s and RoomID = %s", (username, room))
        con.commit()
        print("Removed " + username + " from room " + str(room))
        # If they were the leader, and if there is someone else in the room, select a new one
        if isleader == 1:
            cur.execute("SELECT Username FROM Users WHERE RoomID = %s ORDER BY rand() LIMIT 1",
                        (room,))  # Retreives tuple of string username
            newlead = cur.fetchone()
            if newlead is not None:
                newlead = newlead[0]  # Converts tuple to string
                print("Making " + newlead + " the new leader for room " + str(room))
                cur.execute("UPDATE Users SET IsLeader = 1 WHERE Username = %s and RoomID = %s", (newlead, room))
                # Notify everyone else in the room of the new leader
                emit('newleader', newlead, room=room, include_self=False)
            else:
                # If the room is now empty, remove it
                print("Room " + str(room) + " is now empty, deleting it")
                cur.execute("DELETE FROM Rooms WHERE RoomID = %s", (room,))
                con.commit()
    # Notify everyone else in the room that user has left
    emit('newleave', username, room=room, include_self=False)


@socketio.on('start')
def start(data):
    room = data['room']
    with connect() as con:
        cur = con.cursor()
        cur.execute("SELECT Topic, TimeLimit FROM Rooms WHERE RoomID = %s", (room,))
        info = cur.fetchone()
    print("Sending start trigger with topic: " + str(info[0]) + " and time: " + str(info[1]) + " to room " + str(room))
    emit('startinfo', (info[0], info[1]), room=room)


# registers submitted ideas to db
@socketio.on('newidea')
def newidea(data):
    with connect() as con:
        cur = con.cursor()
        cur.execute("INSERT INTO Ideas (RoomID, Username, Idea) VALUES (%s, %s, %s)",
                    (data['room'], data['user'], data['idea']))
        con.commit()


@socketio.on('votestart')
def votestart(data):
    with connect() as con:
        cur = con.cursor()
        cur.execute("SELECT Idea FROM Ideas WHERE RoomID = %s", (data['room'],))
        emit('IdeasSent', cur.fetchall(), room=data['room'])


@socketio.on('vote')
def vote(data):
    pass


# Function to create a join code
def create_code():
    # create a code
    temp = ""
    for i in range(0, 4):
        temp += str(randint(0, 9))
    # check if the code already exists
    with connect() as con:
        cur = con.cursor()
        cur.execute("SELECT RoomID FROM Rooms WHERE RoomID = %s", (temp,))
        temproom = cur.fetchone()
        # if the code already exists, try again
        if temproom:
            create_code()
        # otherwise send the code
        else:
            return temp


# always true, runs the application on localhost
if __name__ == '__main__':
    socketio.run(app, debug=True)
