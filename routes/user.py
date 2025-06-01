from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.database import User
from extensions import db

user_bp = Blueprint("user", __name__, url_prefix="/user")

@user_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "username": user.username,
        "email": user.email,
    }), 200

@user_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"message": "No JSON data received"}), 400

    username = data.get("username", "").strip()
    email = data.get("email", "").strip()

    if not username or not email:
        return jsonify({"message": "Username and email are required."}), 400

    conflict = User.query.filter(
        ((User.email == email) | (User.username == username)) & (User.id != user_id)
    ).first()
    if conflict:
        return jsonify({"message": "Email or Username already taken."}), 400

    user.username = username
    user.email = email
    db.session.commit()

    return jsonify({"message": "Profile updated successfully."}), 200