from flask import Blueprint, request, render_template, redirect, url_for, flash
from itsdangerous import SignatureExpired, BadSignature
from extensions import serializer, mail
from flask_mail import Message
from models.database import User, db


password_reset = Blueprint("password_reset", __name__)

@password_reset.route("/reset", methods=["GET", "POST"])
def reset_request():
    if request.method == "POST":
        email = request.form.get("email")
        user = User.query.filter_by(email=email).first()  # Use email instead of username

        if user:
            token = serializer.dumps(email, salt="password-reset-salt")
            reset_url = url_for("password_reset.reset_token", token=token, _external=True)
            
            msg = Message("Password Reset Request", recipients=[email])
            msg.body = f"Click the link to reset your password: {reset_url}"
            mail.send(msg)

            flash("Check your email for a password reset link.", "info")
        else:
            flash("No account found with that email.", "warning")

        return redirect(url_for("auth.login"))

    return render_template("reset_request.html")


@password_reset.route("/reset_token/<token>", methods=["GET", "POST"])
def reset_token(token):
    try:
        email = serializer.loads(token, salt="password-reset-salt", max_age=3600)
    except SignatureExpired:
        flash("The token has expired.", "danger")
        return redirect(url_for("password_reset.reset"))
    except BadSignature:
        flash("Invalid token.", "danger")
        return redirect(url_for("password_reset.reset"))

    user = User.query.filter_by(email=email).first()

    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("password_reset.reset"))

    if request.method == "POST":
        new_password = request.form.get("password")
        user.set_password(new_password) 
        db.session.commit()
        flash("Your password has been updated!", "success")
        return redirect(url_for("auth.login"))

    return render_template("reset_password.html", token=token)
