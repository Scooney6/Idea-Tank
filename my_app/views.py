from my_app import app
from flask import render_template, request, redirect
import requests

@app.route("/", methods=["POST", "GET"])
def index():
    return redirect("/home")


@app.route("/home", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        player_name = request.form["player_name"]
        session_code = request.form["session_code"]
    return render_template("home.html")
