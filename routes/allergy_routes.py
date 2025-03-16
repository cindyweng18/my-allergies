import os
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.database import db, Allergy
from werkzeug.utils import secure_filename
from utils.pdf_processing import extract_text_from_pdf, allowed_file
from utils.ai_processing import extract_allergens

allergy_bp = Blueprint('allergy', __name__)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf"}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@allergy_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        # Handle manual allergy input
        allergy_name = request.form.get("allergies", "").strip().lower()
        if allergy_name:
            existing_allergy = Allergy.query.filter_by(name=allergy_name, user_id=current_user.id).first()
            if not existing_allergy:
                allergy = Allergy(name=allergy_name, user_id=current_user.id)
                db.session.add(allergy)
                db.session.commit()
            return redirect(url_for("allergy.index"))

        # Handle PDF upload
        file = request.files.get("pdf")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)

            extracted_text = extract_text_from_pdf(file_path)
            found_allergens = extract_allergens(extracted_text)
            flash(found_allergens)

            # allergens_list = [allergy.name for allergy in Allergy.query.filter_by(user_id=current_user.id).all()]

            # detected_allergens = find_allergens(extracted_text, allergens_list)

            # if detected_allergens:
            #     flash(f"Found these allergens in the document: {', '.join(detected_allergens)}", "danger")
            # else:
            #     flash("No known allergens found in the document.", "success")

            return redirect(url_for("allergy.index"))

    allergies = Allergy.query.filter_by(user_id=current_user.id).all()
    return render_template("index.html", allergies=allergies)

