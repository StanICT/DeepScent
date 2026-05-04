from flask import Blueprint, render_template, request, redirect, url_for, abort
from flask_login import login_required, current_user
from .models import Product, Brand, db
from werkzeug.utils import secure_filename
import os

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
UPLOAD_PATH = os.path.join(os.path.dirname(__file__), 'static', 'uploads')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_image(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        os.makedirs(UPLOAD_PATH, exist_ok=True)
        file.save(os.path.join(UPLOAD_PATH, filename))
        return filename
    return None

# define ONCE
admin = Blueprint("admin", __name__)

@admin.route("/products")
@login_required
def admin_products():
    if not current_user.is_admin:
        abort(403)  # block non-admins
    products = Product.query.all()
    return render_template("admin_products.html", products=products)

@admin.route("/products/add", methods=["GET","POST"])
@login_required
def add_product():
    if not current_user.is_admin:
        abort(403)
    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        price = float(request.form["price"])
        stock = int(request.form["stock"])
        brand = request.form["brand"]
        gender = request.form.get("gender", "UNISEX")
        image_file = request.files.get("image_file")
        image = save_image(image_file) or "default.png"

        new_product = Product(
            name=name, description=description, price=price,
            stock=stock, image=image, brand=brand, gender=gender
        )
        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for("admin.admin_products"))

    return render_template("add_product.html")

@admin.route("/products/edit/<int:id>", methods=["GET","POST"])
@login_required
def edit_product(id):
    if not current_user.is_admin:
        abort(403)
    product = Product.query.get_or_404(id)
    if request.method == "POST":
        product.name = request.form["name"]
        product.description = request.form["description"]
        product.price = float(request.form["price"])
        product.stock = int(request.form["stock"])
        product.brand = request.form["brand"]
        product.gender = request.form.get("gender", "UNISEX")
        image_file = request.files.get("image_file")
        new_image = save_image(image_file)
        if new_image:
            product.image = new_image
        db.session.commit()
        return redirect(url_for("admin.admin_products"))
    return render_template("edit_product.html", product=product)

@admin.route("/products/delete/<int:id>")
@login_required
def delete_product(id):
    if not current_user.is_admin:
        abort(403)
    product = Product.query.get_or_404(id)
    if product.image:
        file_path = os.path.join(UPLOAD_PATH, product.image)
        if os.path.exists(file_path):
            os.remove(file_path)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for("admin.admin_products"))

# --- Brand CRUD ---

@admin.route("/brands")
@login_required
def admin_brands():
    if not current_user.is_admin:
        abort(403)
    brands = Brand.query.all()
    return render_template("admin_brands.html", brands=brands)

@admin.route("/brands/add", methods=["GET", "POST"])
@login_required
def add_brand():
    if not current_user.is_admin:
        abort(403)
    if request.method == "POST":
        name = request.form["name"].strip()
        logo_file = request.files.get("logo_file")
        logo = save_image(logo_file)
        brand = Brand(name=name, logo=logo)
        db.session.add(brand)
        db.session.commit()
        return redirect(url_for("admin.admin_brands"))
    return render_template("add_brand.html")

@admin.route("/brands/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_brand(id):
    if not current_user.is_admin:
        abort(403)
    brand = Brand.query.get_or_404(id)
    if request.method == "POST":
        brand.name = request.form["name"].strip()
        logo_file = request.files.get("logo_file")
        new_logo = save_image(logo_file)
        if new_logo:
            brand.logo = new_logo
        db.session.commit()
        return redirect(url_for("admin.admin_brands"))
    return render_template("edit_brand.html", brand=brand)

@admin.route("/brands/delete/<int:id>")
@login_required
def delete_brand(id):
    if not current_user.is_admin:
        abort(403)
    brand = Brand.query.get_or_404(id)
    if brand.logo:
        file_path = os.path.join(UPLOAD_PATH, brand.logo)
        if os.path.exists(file_path):
            os.remove(file_path)
    db.session.delete(brand)
    db.session.commit()
    return redirect(url_for("admin.admin_brands"))
