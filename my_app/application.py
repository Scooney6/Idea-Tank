from flask import render_template, request, redirect
from flask import Flask
from flask_socketio import SocketIO, send
from my_app.WTForms import *

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
    home_join_form = HomeJoinForm()

    # if the join form is submitted and is valid
    if home_join_form.validate_on_submit():
        # TODO: make the join button do stuff
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
    if create_form.validate_on_submit():
        # TODO: create random room code then add code, topic, and limit to list then send client to that room
        return render_template("lobby.html")

    # otherwise render the template with instantiated form
    return render_template("create.html", form=create_form)


@app.route("/lobby", methods=["POST", "GET"])
def lobby():
    return render_template("lobby.html")


# when the server receives data from a client send method
@socketio.on('message')
def message(data):
    print(data)
    # sends data to all clients in the message event
    send(data)


# always true, runs the application on localhost
if __name__ == '__main__':
    socketio.run(app, debug=True)
