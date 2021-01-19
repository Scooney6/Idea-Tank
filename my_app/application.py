from random import randint

from flask import render_template, request, redirect
from flask import Flask
from flask_socketio import SocketIO, send, join_room, leave_room
from my_app.WTForms import *

# Flask init
app = Flask(__name__)
app.secret_key = 'ilsjgnsjnslkn'

# SocketIO init
socketio = SocketIO(app)

global code_list


# index goes to /home just because
@app.route("/", methods=["POST", "GET"])
def index():
    return redirect("/home")


@app.route("/home", methods=["POST", "GET"])
def home():
    # instantiate the form
    home_join_form = HomeJoinForm()

    # if the join form is submitted and is valid
    if home_join_form.validate():
        # TODO: get field data
        pass

    # if the create form is submitted
    elif request.form.get("Create"):
        return redirect("/create")

    # otherwise render home with instantiated form
    else:
        return render_template("home.html", form=home_join_form)


@app.route("/create", methods=["POST", "GET"])
def create():
    # instantiate create form
    create_form = CreateForm()

    # if the create form is submitted and valid
    if request.method .validate():
        print("bruh")
        code = create_code()
        return redirect("/lobby", code=code)
    else:
        print("nope")
        return render_template("create.html", form=create_form)

        # TODO: create random room code then add code, topic, and limit to list then send client to that room
    # otherwise render the template with instantiated form
    return render_template("create.html", form=create_form)


@app.route("/lobby", methods=["POST", "GET"])
def lobby(code):
    return render_template("lobby.html", code=code)


# when the server receives data from a client send method
@socketio.on('message')
def message(data):
    print(data)
    # sends data to all clients in the message event
    send(data)


@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    send(username + ' has entered the room.', room=room)


@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    send(username + ' has left the room.', room=room)


def create_code():
    temp = ""
    for i in range(0, 3):
        temp += str(randint(0, 9))

    if temp in code_list:
        create_code()

    code_list.add(temp)
    return temp


# always true, runs the application on localhost
if __name__ == '__main__':
    socketio.run(app, debug=True)
