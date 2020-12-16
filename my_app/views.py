from my_app import app
from flask import render_template, request, redirect
from my_app import game_session


@app.route("/", methods=["POST", "GET"])
def index():
    return redirect("/home")


@app.route("/home", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        if request.form.get("Join"):
            player_name = request.form["player_name"]
            session_code = request.form["session_code"]
        elif request.form.get("Create"):
            return redirect("/create")
        else:
            return render_template("home.html")
    else:
        return render_template("home.html")


@app.route("/create", methods=["POST", "GET"])
def create():
    s1 = game_session.GameSession(12, "Big booty bitches")
    return render_template("create.html")
