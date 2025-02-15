import os
from flask import Flask, render_template, request, redirect, url_for, flash
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
                existing_allergy = Allergy.query.filter_by(name=allergy).first()
                if not existing_allergy: 
                    new_allergy = Allergy(name=allergy)
                    db.session.add(new_allergy)
        
        db.session.commit()
        return redirect(url_for("index"))  
    
    allergies = Allergy.query.all()
    return render_template("index.html", allergies=allergies)

@app.route("/delete/<int:allergy_id>")
def delete_allergy(allergy_id):
    allergy = Allergy.query.get_or_404(allergy_id)
    db.session.delete(allergy)
    db.session.commit()
    return redirect(url_for("index"))

@app.route("/edit/<int:allergy_id>", methods=["GET", "POST"])
def edit_allergy(allergy_id):
    allergy = Allergy.query.get_or_404(allergy_id)

    if request.method == "POST":
        new_name = request.form["allergy"].strip().lower()
        existing_allergy = Allergy.query.filter_by(name=new_name).first()

        if existing_allergy:
            flash("This allergy already exists!", "error")
        else:
            allergy.name = new_name
            db.session.commit()
            return redirect(url_for("index"))

    return render_template("edit.html", allergy=allergy)

if __name__ == '__main__':
    app.run(debug=True)