import os
from flask import Flask, render_template, request, session, redirect, url_for
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv("SECRET_KEY", "fallback_secret_key")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        allergies = request.form["allergies"].split(",") 
        allergies = [allergy.strip().lower() for allergy in allergies]
        session["allergies"] = allergies 

        return redirect(url_for("allergy_list"))

    return render_template("index.html")

@app.route("/allergies")
def allergy_list():
    allergies = session.get("allergies", [])
    return render_template("allergies.html", allergies=allergies)

if __name__ == '__main__':
    app.run(debug=True)