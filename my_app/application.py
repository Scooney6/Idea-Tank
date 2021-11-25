from random import randint

from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, join_room, leave_room, emit
from my_app.WTForms import *
import sqlite3 as sql

# Flask init
app = Flask(__name__)
app.secret_key = 'ilsjgnsjnslkn'

# SocketIO init
socketio = SocketIO(app)


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
            with sql.connect("rooms.db") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO rooms (username, room, isleader) VALUES (?, ?, ?)", (username, code, 0))
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
        # add the user the the db as the leader of this room
        with sql.connect("rooms.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO rooms (username, room, isleader) VALUES (?, ?, ?)", (username, code, 1))
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
    with sql.connect("rooms.db") as con:
        cur = con.cursor()
        cur.execute("SELECT username FROM rooms WHERE room = (?)", (room,))
        users = cur.fetchall()
        cur.execute("SELECT username FROM rooms WHERE room = (?) AND isleader = (?)", (room, 1))
        leader = cur.fetchone()
    # Send the username of the player that just connected to everyone in the room except the new player
    emit('newjoin', username, room=room, include_self=False)
    # Send the current users and the leader to the new player
    for i in range(0, len(users)):
        users[i] = users[i][0]
    emit('curusers', (users, leader[0]), room=request.sid)


# Event bucket for when a client disconnects
@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    isleader = data['isleader']
    # Make the user leave their socketio room
    leave_room(room)
    # Remove them from the db
    with sql.connect("rooms.db") as con:
        cur = con.cursor()
        cur.execute("DELETE FROM rooms WHERE username = (?) and room = (?)", (username, room))
        if isleader == 1:
            cur.execute("SELECT username FROM rooms WHERE room = (?)", (room,))
            newlead = cur.fetchone()
            cur.execute("UPDATE rooms SET isleader = 1 WHERE username = (?) and room = (?)", (newlead[0], room))
            emit('newleader', newlead, room=room, include_self=False)
    # Notify everyone else in the room that user has left
    emit('newleave', username, room=room, include_self=False)


# Function to create a join code
def create_code():
    # create a code
    temp = ""
    for i in range(0, 4):
        temp += str(randint(0, 9))
    # check if the code already exists
    with sql.connect("rooms.db") as con:
        cur = con.cursor()
        cur.execute("SELECT room FROM rooms WHERE room = (?)", (temp,))
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


# Initial database setup
#   with sql.connect("rooms.db") as con:
#        cur = con.cursor()
#        cur.execute("CREATE TABLE rooms (username text, room integer, isleader BOOLEAN NOT NULL)")
#        con.commit()
