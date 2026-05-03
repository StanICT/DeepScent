from flask import Blueprint, render_template, request, redirect, url_for, abort
from flask_login import login_required, current_user
from .models import Product, db

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
        image = request.form["image"]
        brand = request.form["brand"]
        gender = request.form.get("gender", "UNISEX")

        new_product = Product(
            name=name,
            description=description,
            price=price,
            stock=stock,
            image=image,
            brand=brand,
            gender=gender
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
        product.image = request.form["image"]
        product.brand = request.form["brand"]
        product.gender = request.form.get("gender", "UNISEX")
        db.session.commit()
        return redirect(url_for("admin.admin_products"))
    return render_template("edit_product.html", product=product)

@admin.route("/products/delete/<int:id>")
@login_required
def delete_product(id):
    if not current_user.is_admin:
        abort(403)
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for("admin.admin_products"))
