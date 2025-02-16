import os
from flask import Flask, render_template, request, redirect, url_for, flash
from database import db, User, Allergy 
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt

app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv("SECRET_KEY", "fallback_secret_key")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///allergies.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
bcrypt = Bcrypt(app)

db.init_app(app)
with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        allergy_name = request.form["allergies"].strip().lower()
        existing_allergy = Allergy.query.filter_by(name=allergy_name, user_id=current_user.id).first()
        if not existing_allergy:
            allergy = Allergy(name=allergy_name, user_id=current_user.id)
            db.session.add(allergy)
            db.session.commit()
        return redirect(url_for("index"))

    allergies = Allergy.query.filter_by(user_id=current_user.id).all()
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

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists!", "danger")
            return redirect(url_for("register"))
        
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful! You can log in now.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid username or password.", "danger")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "success")
    return redirect(url_for("login"))

if __name__ == '__main__':
    app.run(debug=True)