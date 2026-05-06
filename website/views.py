from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import current_user, login_required
from website.models import Product, Brand, CartItem
from website.extensions import db

views = Blueprint('views', __name__)

@views.route('/')
def home():
    brands = Brand.query.all()
    return render_template('home.html', brands=brands)

@views.route('/perfumes/<brand>')
def perfumes(brand):
    products = Product.query.filter_by(brand=brand).all()
    return render_template("perfumes.html",
                           products=products,
                           brand=brand,
                           bg_image="prmnky-bg.jpg")

@views.route('/product')
def product():
    products = Product.query.all()
    return render_template('product.html', products=products)

@views.route('/search')
def search():
    q = request.args.get('q', '').strip()
    results = Product.query.filter(
        Product.name.ilike(f'%{q}%') | Product.brand.ilike(f'%{q}%')
    ).all() if q else []
    return render_template('search.html', results=results, query=q)

@views.route('/featured')
def featured():
    return render_template('featured.html')

@views.route('/cart/login-required')
def cart_login_required():
    flash('Please log in first.', 'error')
    return redirect(url_for('auth.login'))

@views.route('/cart/add/<int:product_id>')
@login_required
def add_to_cart(product_id):
    item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if item:
        item.quantity += 1
    else:
        item = CartItem(user_id=current_user.id, product_id=product_id)
        db.session.add(item)
    db.session.commit()
    flash('Item added to cart!', 'success')
    return redirect(request.referrer or url_for('views.product'))

@views.route('/cart/remove/<int:product_id>', methods=['POST'])
@login_required
def remove_from_cart(product_id):
    item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if item:
        db.session.delete(item)
        db.session.commit()
    total = sum(i.quantity for i in current_user.cart_items)
    return jsonify({'success': True, 'cart_count': total})

@views.route('/cart')
@login_required
def cart():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(i.product.price * i.quantity for i in items)
    return render_template('cart.html', items=items, total=total)
