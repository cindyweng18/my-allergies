from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
from models.database import db
from routes.auth_routes import auth_bp
from routes.allergy_routes import allergy_bp
from models.database import db, User

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(allergy_bp)

if __name__ == "__main__":
    app.run(debug=True)
