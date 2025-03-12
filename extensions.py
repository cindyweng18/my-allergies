from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from itsdangerous import URLSafeTimedSerializer 
from flask import current_app

db = SQLAlchemy()
bcrypt = Bcrypt()
mail = Mail()

def get_serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])