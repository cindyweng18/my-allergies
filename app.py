from flask import Flask, redirect, url_for
from flask_migrate import Migrate
from flask_cors import CORS
from config import Config
from extensions import db, mail, bcrypt 
from flask_login import LoginManager
from models.database import User
from routes.auth_routes import auth_bp
from routes.allergy_routes import allergy_bp
from routes.password_reset import password_reset
from itsdangerous import URLSafeTimedSerializer 

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    db.init_app(app)
    migrate = Migrate(app, db)
    mail.init_app(app)
    bcrypt.init_app(app)

    global serializer
    serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])

    login_manager = LoginManager(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info" 

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(allergy_bp, url_prefix="/allergy")
    # app.register_blueprint(allergy_bp)
    app.register_blueprint(password_reset)

    @app.route("/")
    def home():
        return redirect(url_for("allergy.index"))

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
