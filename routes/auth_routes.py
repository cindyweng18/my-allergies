"""
Authentication Blueprint for a Flask application.

This module defines routes for user registration, login, and accessing a protected resource.
It uses JWT (JSON Web Tokens) for authentication and `werkzeug.security` for password hashing.

Routes:
- POST /register: Register a new user with email, username, and password.
- POST /login: Authenticate a user and return a JWT access token.
- GET /protected: A route that requires a valid JWT token to access.

Dependencies:
- Flask
- flask_jwt_extended
- werkzeug.security
- SQLAlchemy (via `extensions.db`)
- A User model from `models.database`

Blueprint:
- `auth_bp`: Can be registered with a Flask app to enable these authentication routes.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from models.database import User
from extensions import db

auth_bp = Blueprint('auth', __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Register a new user.

    Expected JSON payload:
    {
        "email": "user@example.com",
        "username": "user123",
        "password": "securepassword"
    }

    Returns:
        201: Registration successful.
        400: Missing or invalid data.
        415: Incorrect content type (not JSON).
    """
    data = request.get_json()
    email = data.get("email")
    username = data.get("username")
    password = data.get("password")

    if not request.is_json:
        return jsonify({"message": "Request must be JSON"}), 415
    if not data:
        return jsonify({"message": "No JSON data received"}), 400
    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400

    existing_user = User.query.filter((User.email == email) | (User.username == username)).first()
    if existing_user:
        return jsonify({"message": "Email or Username already taken."}), 400

    hashed_password = generate_password_hash(password)
    new_user = User(email=email, username=username, password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "Registration successful!"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Authenticate a user and return a JWT access token.

    Expected JSON payload:
    {
        "username": "user123",
        "password": "securepassword"
    }

    Returns:
        200: Login successful with access token.
        400: Missing or invalid credentials.
        401: Invalid username or password.
        415: Incorrect content type (not JSON).
    """
    if not request.is_json:
        return jsonify({"message": "Request must be JSON"}), 415

    data = request.get_json()
    if not data:
        return jsonify({"message": "No JSON data received"}), 400

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"message": "Invalid username or password"}), 401

    access_token = create_access_token(identity=str(user.id))
    return jsonify({"access_token": access_token, "message": "Login successful!"})


@auth_bp.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    """
    Access a protected route that requires a valid JWT token.

    Returns:
        200: A greeting message including the user's ID from the token.
    """
    user_id = get_jwt_identity()
    return jsonify({"message": f"Hello User {user_id}, this is a protected route!"})
