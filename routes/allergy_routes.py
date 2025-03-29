import os
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models.database import db, Allergy
from werkzeug.utils import secure_filename
from utils.pdf_processing import extract_text_from_pdf
from utils.image_processing import extract_text_from_image
from utils.ai_processing import extract_allergens, check_product_safety

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
    if request.method == "GET":
        allergies = Allergy.query.filter_by(user_id=current_user.id).all()
        return jsonify({"allergies": [allergy.name for allergy in allergies]})

    if request.method == "POST":
        data = request.json 

        # Handle manual allergy input
        allergy_name = data.get("allergy", "").strip().lower()
        if allergy_name:
            if not Allergy.query.filter_by(name=allergy_name, user_id=current_user.id).first():
                db.session.add(Allergy(name=allergy_name, user_id=current_user.id))
                db.session.commit()
                return jsonify({"message": "Allergy added successfully"}), 201
            return jsonify({"message": "Allergy already exists"}), 400

        # Handle product safety check
        product_name = data.get("product_name", "").strip().lower()
        if product_name:
            user_allergies = [a.name for a in Allergy.query.filter_by(user_id=current_user.id).all()]
            response = check_product_safety(product_name, user_allergies)
            return jsonify({"message": response})

        return jsonify({"error": "Invalid request"}), 400

@allergy_bp.route("/upload", methods=["POST"])
@login_required
def upload_file():
    if "file" not in request.files:
        return jsonify({"message": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"message": "Invalid file format"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    # Process file (PDF or Image)
    if file.filename.endswith(".pdf"):
        extracted_text = extract_text_from_pdf(file_path)
    else:
        extracted_text = extract_text_from_image(file_path)

    found_allergens = extract_allergens(extracted_text)

    for allergen in found_allergens:
        if not Allergy.query.filter_by(name=allergen, user_id=current_user.id).first():
            db.session.add(Allergy(name=allergen, user_id=current_user.id))

    db.session.commit()
    os.remove(file_path)

    return jsonify({"message": "File processed successfully", "allergens": found_allergens}), 201