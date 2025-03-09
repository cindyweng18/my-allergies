from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import secrets
from datetime import datetime, timedelta
from extensions import db, bcrypt
from flask_login import UserMixin
from sqlalchemy.schema import UniqueConstraint
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    UniqueConstraint('email', name='uq_user_email')
    UniqueConstraint('username', name='uq_user_username')
    password_hash = db.Column(db.String(128), nullable=False)
    reset_token = db.Column(db.String(100), unique=True, nullable=True)
    reset_token_expiration = db.Column(db.DateTime, nullable=True)

    @property
    def is_active(self):
        return True 

    def set_password(self, password):
        """Hashes and stores the password securely."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Checks if the provided password matches the stored hash."""
        return check_password_hash(self.password_hash, password)

    def generate_reset_token(self):
        """Generates a secure reset token and sets its expiration."""
        self.reset_token = secrets.token_hex(16)  
        self.reset_token_expiration = datetime.utcnow() + timedelta(hours=1)

    def validate_reset_token(self, token):
        """Checks if the provided token matches and is not expired."""
        return self.reset_token == token and datetime.utcnow() < self.reset_token_expiration

class Allergy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', name="fk_allergy_user_id"), nullable=False)
    user = db.relationship('User', backref=db.backref('allergies', lazy=True))
