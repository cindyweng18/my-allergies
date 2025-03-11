from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask import app
from itsdangerous import URLSafeTimedSerializer 

db = SQLAlchemy()
bcrypt = Bcrypt()
mail = Mail()

def get_serializer():
    return URLSafeTimedSerializer(app.config["SECRET_KEY"])