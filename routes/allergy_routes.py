"""
Allergy Management Blueprint for a Flask application.

This module provides routes to manage user allergies, including:
- Adding, editing, deleting, and listing allergies
- Batch operations for allergy management
- Uploading files (e.g., PDFs) to extract allergens via AI
- Checking product safety against known allergies using AI

Routes:
- GET /             : Get a list of user's allergies
- POST /add         : Add a new allergy
- PUT /edit         : Edit an existing allergy
- DELETE /<name>    : Delete a specific allergy
- POST /delete_batch: Delete multiple allergies at once
- POST /add_batch   : Add multiple allergies at once
- POST /check_product: Check if a product is safe based on allergies
- POST /upload      : Upload a file to extract possible allergens
- POST /save        : Save selected extracted allergens to user's profile

Dependencies:
- Flask
- flask_jwt_extended
- werkzeug
- SQLAlchemy
- Custom utility modules: `pdf_processing`, `ai_processing`
"""

import os, re
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.database import Allergy, User
from utils.pdf_processing import extract_text_from_pdf, extract_allergens
from utils.ai_processing import extract_allergens, check_product_safety
from extensions import db

allergy_bp = Blueprint("allergy", __name__)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    """Check if a file has an allowed extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def is_valid_allergen(name):
    """Validate an allergen name using regex."""
    return bool(re.match(r"^[a-zA-Z\s\-]{2,50}$", name.strip()))

@allergy_bp.route("/", methods=["GET"])
@jwt_required()
def get_allergies():
    """
    Retrieve the list of allergies associated with the authenticated user.

    Returns:
        200 OK with a list of allergy names.
    """
    user_id = get_jwt_identity()
    allergies = Allergy.query.filter_by(user_id=user_id).all()
    return jsonify({"allergies": [a.name for a in allergies]}), 200

@allergy_bp.route("/add", methods=["POST"])
@jwt_required()
def add_allergy():
    """
    Add a new allergy for the authenticated user.

    JSON Body:
        {
            "allergy": "peanuts"
        }

    Returns:
        200 OK if added successfully.
        400 Bad Request for invalid input.
        409 Conflict if allergy already exists.
    """
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
    """
    Edit the name of an existing allergy.

    JSON Body:
        {
            "old_name": "peanuts",
            "new_name": "tree nuts"
        }

    Returns:
        200 OK if updated.
        404 Not Found if allergy not found.
    """
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
    """
    Delete a specific allergy by name.

    Path Parameter:
        allergy_name (str): The name of the allergy to delete.

    Returns:
        200 OK if deleted.
        404 Not Found if allergy does not exist.
    """
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
    """
    Delete multiple allergies at once.

    JSON Body:
        {
            "allergies": ["peanuts", "soy"]
        }

    Returns:
        200 OK with list of successfully deleted allergies.
        400 Bad Request if input is invalid.
    """
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
    """
    Use AI to check if a product is safe based on user's allergies.

    JSON Body:
        {
            "product_name": "chocolate bar"
        }

    Returns:
        200 OK with AI response.
        400 Bad Request if product name is missing.
        500 Internal Server Error if AI call fails.
    """
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
    """
    Upload a PDF file and extract possible allergens using AI.

    Form-Data:
        file: A file (PDF, JPG, PNG, JPEG)

    Returns:
        200 OK with a list of detected allergens.
        400 Bad Request if no file is provided.
        500 Internal Server Error on processing failure.
    """
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
    """
    Save selected allergens from the uploaded file to the user's allergy list.

    JSON Body:
        {
            "allergies": ["soy", "gluten"]
        }

    Returns:
        200 OK if allergies saved.
        400 Bad Request if no allergies provided.
    """
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
    """
    Add multiple allergies at once.

    JSON Body:
        {
            "allergies": ["soy", "peanuts", "gluten"]
        }

    Returns:
        200 OK with number of allergies added.
        400 Bad Request if input is invalid.
    """
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
