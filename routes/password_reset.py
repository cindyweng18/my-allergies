from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_mail import Message
from flask_login import current_user
from models import User, db
from app import mail

password_reset = Blueprint("password_reset", __name__)

@password_reset.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    if request.method == "POST":
        email = request.form["email"]
        user = User.query.filter_by(email=email).first()
        if user:
            send_reset_email(user)
            flash("Password reset email sent!", "info")
            return redirect(url_for("auth.login"))
        flash("Email not found.", "danger")
    return render_template("reset_request.html")

def send_reset_email(user):
    token = user.get_reset_token()
    reset_url = url_for("password_reset.reset_token", token=token, _external=True)
    msg = Message("Password Reset Request", recipients=[user.email])
    msg.body = f"Click the link to reset your password: {reset_url}"
    mail.send(msg)

@password_reset.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    user = User.verify_reset_token(token)
    if not user:
        flash("Invalid or expired token.", "danger")
        return redirect(url_for("password_reset.reset_request"))

    if request.method == "POST":
        password = request.form["password"]
        user.set_password(password)
        db.session.commit()
        flash("Password has been reset!", "success")
        return redirect(url_for("auth.login"))

    return render_template("reset_password.html")
