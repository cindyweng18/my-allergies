from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        allergies = request.form["allergies"].split(",") 
        allergies = [allergy.strip().lower() for allergy in allergies] 

    return render_template("index.html")

if __name__ == '__main__':
    app.run()