import os, re
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.database import Allergy
from utils.pdf_processing import extract_text_from_pdf, extract_allergens
from utils.ai_processing import extract_allergens, check_product_safety
from models.database import User
from extensions import db

allergy_bp = Blueprint("allergy", __name__)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def is_valid_allergen(name):
    return bool(re.match(r"^[a-zA-Z\s\-]{2,50}$", name.strip()))

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

    if not allergy_name or not re.match(r'^[a-zA-Z\s\-]+$', allergy_name):
        return jsonify({"message": "Invalid allergy name"}), 400

    existing = Allergy.query.filter_by(user_id=user_id, name=allergy_name).first()
    if existing:
        return jsonify({"message": "Allergy already exists"}), 409

    new_allergy = Allergy(name=allergy_name, user_id=user_id)
    db.session.add(new_allergy)
    db.session.commit()

    return jsonify({"message": "Allergy added successfully"}), 200

@allergy_bp.route("/edit", methods=["PUT"])
@jwt_required()
def edit_allergy():
    data = request.get_json()
    user_id = get_jwt_identity()
    old_name = data.get("old_name", "").strip().lower()
    new_name = data.get("new_name", "").strip().lower()

    allergy = Allergy.query.filter_by(name=old_name, user_id=user_id).first()
    if not allergy:
        return jsonify({"message": "Allergy not found"}), 404

    allergy.name = new_name
    db.session.commit()
    return jsonify({"message": "Allergy updated"}), 200

@allergy_bp.route("/<string:allergy_name>", methods=["DELETE"])
@jwt_required()
def delete_allergy(allergy_name):
    user_id = get_jwt_identity()
    normalized_name = allergy_name.strip().lower()

    allergy = Allergy.query.filter_by(user_id=user_id, name=normalized_name).first()
    if not allergy:
        return jsonify({"message": "Allergy not found"}), 404

    db.session.delete(allergy)
    db.session.commit()
    return jsonify({"message": f"Allergy '{normalized_name}' deleted."}), 200

@allergy_bp.route("/delete_batch", methods=["POST"])
@jwt_required()
def delete_allergies():
    user_id = get_jwt_identity()
    data = request.get_json()
    allergies = data.get("allergies", [])

    if not allergies or not isinstance(allergies, list):
        return jsonify({"error": "Invalid allergy list"}), 400

    deleted = []
    for name in allergies:
        allergy = Allergy.query.filter_by(name=name.strip().lower(), user_id=user_id).first()
        if allergy:
            db.session.delete(allergy)
            deleted.append(name)

    db.session.commit()
    return jsonify({"message": "Deleted", "deleted": deleted}), 200


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
    if "file" not in request.files:
        return jsonify({"message": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"message": "No selected file"}), 400

    try:
        text = extract_text_from_pdf(file) 
        possible_allergens = extract_allergens(text) 

        return jsonify({
            "allergens": possible_allergens,
            "message": "Select only the allergies you actually have."
        }), 200

    except Exception as e:
        return jsonify({"message": f"Error processing file: {str(e)}"}), 500

@allergy_bp.route("/save", methods=["POST"])
@jwt_required()
def save_selected_allergies():
    user_id = get_jwt_identity()
    data = request.get_json()
    selected_allergies = data.get("allergies", [])

    if not selected_allergies:
        return jsonify({"message": "No allergies submitted"}), 400

    user = User.query.get(user_id)
    for a in selected_allergies:
        if a not in user.allergies:
            user.allergies.append(a)

    db.session.commit()
    return jsonify({"message": "Allergies saved successfully."}), 200

@allergy_bp.route("/add_batch", methods=["POST"])
@jwt_required()
def add_batch_allergies():
    user_id = get_jwt_identity()
    data = request.get_json()
    allergy_list = data.get("allergies", [])

    if not isinstance(allergy_list, list) or not allergy_list:
        return jsonify({"message": "No valid allergy list provided"}), 400

    existing = {a.name for a in Allergy.query.filter_by(user_id=user_id).all()}

    added = []
    for name in allergy_list:
        normalized = name.strip().lower()
        if normalized and normalized not in existing:
            db.session.add(Allergy(name=normalized, user_id=user_id))
            added.append(normalized)

    db.session.commit()
    return jsonify({"message": f"Added {len(added)} new allergies.", "added": added}), 200
