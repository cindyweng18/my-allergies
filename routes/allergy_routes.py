import os
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.database import db, Allergy
from werkzeug.utils import secure_filename
from utils.pdf_processing import extract_text_from_pdf
from utils.image_processing import extract_text_from_image
from utils.ai_processing import extract_allergens

allergy_bp = Blueprint("allergy", __name__)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

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

        # Handle file upload (PDF or image)
        file = request.files.get("file")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)

            if filename.endswith(".pdf"):
                extracted_text = extract_text_from_pdf(file_path)
            else:
                extracted_text = extract_text_from_image(file_path)

            found_allergens = extract_allergens(extracted_text)

            for allergen in found_allergens:
                if not Allergy.query.filter_by(name=allergen, user_id=current_user.id).first():
                    db.session.add(Allergy(name=allergen, user_id=current_user.id))

            db.session.commit()
            os.remove(file_path)

            flash(f"Detected Allergens: {', '.join(found_allergens)}", "success")

            return redirect(url_for("allergy.index"))

    allergies = Allergy.query.filter_by(user_id=current_user.id).all()
    return render_template("index.html", allergies=allergies)

