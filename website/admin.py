from flask import Blueprint, render_template, request, redirect, url_for, abort
from flask_login import login_required, current_user
from .models import Product, Brand, Order, OrderItem, User, db
from sqlalchemy import text as db_text
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

admin = Blueprint("admin", __name__)

@admin.route("/dashboard")
@login_required
def dashboard():
    if not current_user.is_admin:
        abort(403)
    total_orders = Order.query.count()
    total_revenue = db.session.query(db.func.sum(Order.total)).scalar() or 0
    total_products = Product.query.count()
    total_users = User.query.filter_by(is_admin=False).count()
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    top_products = db.session.query(
        Product.name, db.func.sum(OrderItem.quantity).label('sold')
    ).join(OrderItem).group_by(Product.id).order_by(db_text('sold DESC')).limit(5).all()

    # Revenue by day for last 7 days
    from datetime import datetime, timedelta
    today = datetime.utcnow().date()
    revenue_labels = []
    revenue_data = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        label = day.strftime('%b %d')
        total = db.session.query(db.func.sum(Order.total)).filter(
            db.func.date(Order.created_at) == day
        ).scalar() or 0
        revenue_labels.append(label)
        revenue_data.append(round(float(total), 2))

    return render_template('admin_dashboard.html',
        total_orders=total_orders,
        total_revenue=total_revenue,
        total_products=total_products,
        total_users=total_users,
        recent_orders=recent_orders,
        top_products=top_products,
        revenue_labels=revenue_labels,
        revenue_data=revenue_data
    )

@admin.route("/orders")
@login_required
def admin_orders():
    if not current_user.is_admin:
        abort(403)
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin_orders.html', orders=orders)

@admin.route("/orders/status/<int:order_id>", methods=['POST'])
@login_required
def update_order_status(order_id):
    if not current_user.is_admin:
        abort(403)
    order = Order.query.get_or_404(order_id)
    order.status = request.form.get('status', 'Pending')
    db.session.commit()
    return redirect(url_for('admin.admin_orders'))

@admin.route("/orders/delete/<int:order_id>", methods=['POST'])
@login_required
def delete_order(order_id):
    if not current_user.is_admin:
        abort(403)
    order = Order.query.get_or_404(order_id)
    for item in order.items:
        db.session.delete(item)
    db.session.delete(order)
    db.session.commit()
    return redirect(url_for('admin.admin_orders'))

@admin.route("/customers")
@login_required
def admin_customers():
    if not current_user.is_admin:
        abort(403)
    customers = User.query.filter_by(is_admin=False).all()
    return render_template('admin_customers.html', customers=customers)

@admin.route("/customers/<int:user_id>")
@login_required
def customer_detail(user_id):
    if not current_user.is_admin:
        abort(403)
    from .models import Order
    customer = User.query.get_or_404(user_id)
    orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()
    total_spent = sum(o.total for o in orders)
    return render_template('admin_customer_detail.html', customer=customer, orders=orders, total_spent=total_spent)

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
        stock_50ml = int(request.form.get("stock_50ml", 0))
        stock_100ml = int(request.form.get("stock_100ml", 0))
        price_100ml = float(request.form["price_100ml"]) if request.form.get("price_100ml") else None
        discount = int(request.form.get("discount", 0))
        brand = request.form["brand"]
        gender = request.form.get("gender", "UNISEX")
        image_file = request.files.get("image_file")
        image = save_image(image_file) or "default.png"

        new_product = Product(
            name=name, description=description, price=price,
            stock_50ml=stock_50ml, stock_100ml=stock_100ml,
            price_100ml=price_100ml, discount=discount, image=image, brand=brand, gender=gender
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
        product.stock_50ml = int(request.form.get("stock_50ml", 0))
        product.stock_100ml = int(request.form.get("stock_100ml", 0))
        product.price_100ml = float(request.form["price_100ml"]) if request.form.get("price_100ml") else None
        product.discount = int(request.form.get("discount") or 0)
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
