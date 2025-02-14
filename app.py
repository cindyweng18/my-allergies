import os
from flask import Flask, render_template, request, redirect, url_for
from database import db, Allergy 
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv("SECRET_KEY", "fallback_secret_key")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///allergies.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
with app.app_context():
    db.create_all()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        allergies_input = request.form["allergies"]
        allergies_list = [allergy.strip().lower() for allergy in allergies_input.split(",")]

        for allergy in allergies_list:
            if allergy:  
                new_allergy = Allergy(name=allergy)
                db.session.add(new_allergy)
        
        db.session.commit()
        return redirect(url_for("index"))  
    
    allergies = Allergy.query.all()
    return render_template("index.html", allergies=allergies)

if __name__ == '__main__':
    app.run(debug=True)