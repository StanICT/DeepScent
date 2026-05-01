from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user
from website.models import User, db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, current_user

auth = Blueprint("auth", __name__)

@auth.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already taken.")
            return redirect(url_for("auth.signup"))

        new_user = User(
            username=username,
            password=generate_password_hash(password, method="pbkdf2:sha256"),
            is_admin=False
        )
        db.session.add(new_user)
        db.session.commit()

        flash("Account created! You can now log in.")
        return redirect(url_for("auth.login"))

    return render_template("signup.html")

@auth.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user is None:
            flash("No account found with that username.", "error")
            return redirect(url_for("auth.login"))

        if not check_password_hash(user.password, password):
            flash("Incorrect password. Please try again.", "error")
            return redirect(url_for("auth.login"))

        login_user(user)
        flash("Logged in successfully!", "success")
        return redirect(url_for("views.home"))

    return render_template("login.html")

@auth.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))

@auth.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user)
