import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from models.database import db, Allergy
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

@allergy_bp.route("/", methods=["GET"])
@jwt_required()
def get_allergies():
    user_id = get_jwt_identity()
    allergies = Allergy.query.filter_by(user_id=user_id).all()
    return jsonify({"allergies": [a.name for a in allergies]}), 200

@allergy_bp.route("/add", methods=["POST"])
@jwt_required()
def add_allergy():
    user_id = get_jwt_identity()
    data = request.get_json()
    allergy_name = data.get("allergy", "").strip().lower()

    if not allergy_name:
        return jsonify({"error": "Missing allergy name"}), 400

    exists = Allergy.query.filter_by(name=allergy_name, user_id=user_id).first()
    if exists:
        return jsonify({"message": "Allergy already exists"}), 400

    db.session.add(Allergy(name=allergy_name, user_id=user_id))
    db.session.commit()
    return jsonify({"message": "Allergy added successfully"}), 201

@allergy_bp.route("/delete", methods=["POST"])
@jwt_required()
def delete_allergy():
    user_id = get_jwt_identity()
    data = request.get_json()
    allergy_name = data.get("allergy", "").strip().lower()

    if not allergy_name:
        return jsonify({"error": "Missing allergy name"}), 400

    allergy = Allergy.query.filter_by(name=allergy_name, user_id=user_id).first()
    if not allergy:
        return jsonify({"error": "Allergy not found"}), 404

    db.session.delete(allergy)
    db.session.commit()

    return jsonify({"message": "Allergy deleted successfully"}), 200


@allergy_bp.route("/check_product", methods=["POST"])
@jwt_required()
def check_product():
    user_id = get_jwt_identity()
    data = request.get_json()
    product_name = data.get("product_name", "").strip().lower()

    if not product_name:
        return jsonify({"error": "Missing product name"}), 400

    user_allergies = [a.name for a in Allergy.query.filter_by(user_id=user_id).all()]

    try:
        response = check_product_safety(product_name, user_allergies)
        return jsonify({"message": response}), 200
    except Exception as e:
        return jsonify({"error": "AI check failed", "details": str(e)}), 500
    
@allergy_bp.route("/upload", methods=["POST"])
@jwt_required()
def upload_file():
    user_id = get_jwt_identity()

    if "file" not in request.files:
        return jsonify({"message": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"message": "Invalid file format"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    # Extract text from file
    try:
        if file.filename.lower().endswith(".pdf"):
            extracted_text = extract_text_from_pdf(file_path)
        else:
            extracted_text = extract_text_from_image(file_path)
    except Exception as e:
        os.remove(file_path)
        return jsonify({"error": "Failed to process file", "details": str(e)}), 500

    os.remove(file_path)

    # Extract allergens using AI
    found_allergens = extract_allergens(extracted_text)
    new_allergens = []

    for allergen in found_allergens:
        if not Allergy.query.filter_by(name=allergen, user_id=user_id).first():
            db.session.add(Allergy(name=allergen, user_id=user_id))
            new_allergens.append(allergen)

    db.session.commit()

    if not found_allergens:
        return jsonify({"message": "No allergens found in file"}), 204

    return jsonify({"message": "File processed successfully", "allergens": new_allergens}), 201