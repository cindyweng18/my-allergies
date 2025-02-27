from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from models.database import db, Allergy

allergy_bp = Blueprint('allergy', __name__)

@allergy_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))
    
    if request.method == "POST":
        allergy_name = request.form["allergies"].strip().lower()
        existing_allergy = Allergy.query.filter_by(name=allergy_name, user_id=current_user.id).first()
        if not existing_allergy:
            allergy = Allergy(name=allergy_name, user_id=current_user.id)
            db.session.add(allergy)
            db.session.commit()
        return redirect("/")

    allergies = Allergy.query.filter_by(user_id=current_user.id).all()
    return render_template("index.html", allergies=allergies)
