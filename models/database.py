import secrets
from datetime import datetime, timedelta
from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    """
    User model for storing account details and handling authentication.
    Inherits from SQLAlchemy's db.Model and Flask-Login's UserMixin.
    """

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    reset_token = db.Column(db.String(100), unique=True, nullable=True)
    reset_token_expiration = db.Column(db.DateTime, nullable=True)

    @property
    def is_active(self):
        """
        Required by Flask-Login. Indicates whether this user account is active.
        Always returns True in this implementation.
        """
        return True

    def set_password(self, password):
        """
        Hashes the provided plaintext password and stores it in the user instance.

        Args:
            password (str): The user's plaintext password.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Checks whether the provided password matches the stored hashed password.

        Args:
            password (str): The plaintext password to verify.

        Returns:
            bool: True if the password matches, False otherwise.
        """
        return check_password_hash(self.password_hash, password)

    def generate_reset_token(self):
        """
        Generates a secure token for password reset and sets its expiration time
        to one hour from the current time.
        """
        self.reset_token = secrets.token_hex(16)
        self.reset_token_expiration = datetime.utcnow() + timedelta(hours=1)

    def validate_reset_token(self, token):
        """
        Validates the provided token by checking if it matches the stored token
        and has not expired.

        Args:
            token (str): The reset token to validate.

        Returns:
            bool: True if the token is valid and not expired, False otherwise.
        """
        return self.reset_token == token and datetime.utcnow() < self.reset_token_expiration


class Allergy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', name="fk_allergy_user_id"), nullable=False)
    user = db.relationship('User', backref=db.backref('allergies', lazy=True))

    __table_args__ = (
        db.UniqueConstraint('user_id', 'name', name='uq_user_allergy'),
    )
