from flask import Flask
from config import Config
from extensions import db, mail, serializer
from flask_login import LoginManager
from models.database import User
from routes.auth_routes import auth_bp
from routes.allergy_routes import allergy_bp
from routes.password_reset import password_reset

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
mail.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(allergy_bp)
app.register_blueprint(password_reset)

if __name__ == "__main__":
    app.run(debug=True)
