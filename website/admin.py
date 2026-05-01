from flask import Blueprint, render_template, request, redirect, url_for
from .models import Product, db

# define ONCE
admin = Blueprint("admin", __name__)

@admin.route("/products")
def admin_products():
    products = Product.query.all()
    return render_template("admin_products.html", products=products)

@admin.route("/products/add", methods=["GET","POST"])
def add_product():
    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        price = float(request.form["price"])
        stock = int(request.form["stock"])
        image = request.form["image"]
        brand = request.form["brand"]

        new_product = Product(name=name, description=description,
                              price=price, stock=stock,
                              image=image, brand=brand)
        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for("admin.admin_products"))

    return render_template("add_product.html")
