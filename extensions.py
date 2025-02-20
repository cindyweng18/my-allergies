from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from itsdangerous import URLSafeTimedSerializer
from config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
mail = Mail()
serializer = URLSafeTimedSerializer(Config.SECRET_KEY)