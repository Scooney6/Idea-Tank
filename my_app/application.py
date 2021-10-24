from random import randint

from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, send, join_room, leave_room, emit
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
            with sql.connect("rooms.db") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO rooms (username, room) VALUES (?, ?)", (username, code))
            return redirect(url_for("lobby", code=code, username=username))
        # otherwise render the home page again with errors if necessary
        else:
            return render_template("home.html", form=home_join_form)
    # otherwise render home with form
    else:
        return render_template("home.html", form=home_join_form)


@app.route("/create", methods=["POST", "GET"])
def create():
    # instantiate create form
    create_form = CreateForm()

    # if the create form is submitted and valid
    if create_form.validate_on_submit():
        code = create_code()
        username = create_form.username.data
        with sql.connect("rooms.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO rooms (username, room) VALUES (?, ?)", (username, code))
            cur.execute("SELECT * FROM rooms")
            print(cur.fetchall())
        return redirect(url_for("lobby", code=code, username=username))
    # otherwise render the template with instantiated form and errors if necessary
    else:
        return render_template("create.html", form=create_form)


@app.route("/lobby", methods=["POST", "GET"])
def lobby():
    cd = request.args.get('code')
    return render_template("lobby.html", code=cd)


@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    with sql.connect("rooms.db") as con:
        cur = con.cursor()
        cur.execute("SELECT username FROM rooms WHERE room = (?)", (room,))
        users = cur.fetchall()
    # Sends to everyone in the room of the sender but not the sender
    emit('newjoin', username, room=room, include_self=False)
    # Sends to only the client sender
    emit('curusers', users, room=request.sid)


@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    send(username + ' has left the room.', room=room)


def create_code():
    temp = ""
    for i in range(0, 4):
        temp += str(randint(0, 9))

    with sql.connect("rooms.db") as con:
        cur = con.cursor()
        cur.execute("SELECT room FROM rooms WHERE room = (?)", (temp,))
        temproom = cur.fetchone()
        if temproom:
            create_code()
        else:
            print(temp)
            return temp


# always true, runs the application on localhost
if __name__ == '__main__':
    socketio.run(app, debug=True)


# Initial database setup
#   with sql.connect("rooms.db") as con:
#        cur = con.cursor()
#        cur.execute("CREATE TABLE rooms (username text, room integer)")
#        con.commit()
