from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from website.models import User, db
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

auth = Blueprint("auth", __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

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
    return redirect(url_for("auth.login"))

@auth.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user)

@auth.route("/delete_avatar", methods=["POST"])
@login_required
def delete_avatar():
    if current_user.avatar:
        file_path = os.path.join(os.path.dirname(__file__), "static", "uploads", current_user.avatar)
        if os.path.exists(file_path):
            os.remove(file_path)
        current_user.avatar = None
        db.session.commit()
    return "ok", 200

@auth.route("/upload_avatar", methods=["POST"])
@login_required
def upload_avatar():
    file = request.files.get("avatar")
    if not file or file.filename == "":
        return "no file", 400

    if allowed_file(file.filename):
        filename = secure_filename(f"{current_user.username}_avatar.png")

        upload_path = os.path.join(os.path.dirname(__file__), "static", "uploads")
        os.makedirs(upload_path, exist_ok=True)

        file.save(os.path.join(upload_path, filename))

        current_user.avatar = filename
        db.session.commit()

        print("Saved avatar for:", current_user.username, "->", filename)

    return "ok", 200




