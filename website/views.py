from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import current_user, login_required
from website.models import Product, Brand, CartItem, Favorite
from website.extensions import db

views = Blueprint('views', __name__)

@views.route('/')
def home():
    brands = Brand.query.all()
    return render_template('home.html', brands=brands)

@views.route('/perfumes/<brand>')
def perfumes(brand):
    products = Product.query.filter_by(brand=brand).all()
    favorited_ids = [f.product_id for f in current_user.favorites] if current_user.is_authenticated else []
    return render_template("perfumes.html",
                           products=products,
                           brand=brand,
                           bg_image="prmnky-bg.jpg",
                           favorited_ids=favorited_ids)

@views.route('/product')
def product():
    products = Product.query.all()
    favorited_ids = [f.product_id for f in current_user.favorites] if current_user.is_authenticated else []
    return render_template('product.html', products=products, favorited_ids=favorited_ids)

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

@views.route('/favorites/panel')
@login_required
def favorites_panel():
    items = Favorite.query.filter_by(user_id=current_user.id).all()
    return jsonify({'items': [{
        'id': i.product_id,
        'name': i.product.name,
        'brand': i.product.brand,
        'price': i.product.price,
        'image': i.product.image
    } for i in items]})

@views.route('/cart/panel')
@login_required
def cart_panel():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum((i.price_paid if i.price_paid else i.product.price) * i.quantity for i in items)
    return jsonify({'items': [{
        'name': i.product.name,
        'brand': i.product.brand,
        'image': i.product.image,
        'size': i.size,
        'quantity': i.quantity,
        'subtotal': (i.price_paid if i.price_paid else i.product.price) * i.quantity
    } for i in items], 'total': total})

@views.route('/favorites')
@login_required
def favorites():
    items = Favorite.query.filter_by(user_id=current_user.id).all()
    return render_template('favorites.html', items=items)

@views.route('/cart/login-required')
def cart_login_required():
    flash('Please log in first.', 'error')
    return redirect(url_for('auth.login'))

@views.route('/favorite/toggle/<int:product_id>')
@login_required
def toggle_favorite(product_id):
    fav = Favorite.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if fav:
        db.session.delete(fav)
        db.session.commit()
        return jsonify({'favorited': False, 'count': len(current_user.favorites)})
    else:
        fav = Favorite(user_id=current_user.id, product_id=product_id)
        db.session.add(fav)
        db.session.commit()
        return jsonify({'favorited': True, 'count': len(current_user.favorites)})

@views.route('/cart/add/<int:product_id>')
@login_required
def add_to_cart(product_id):
    size = request.args.get('size', '50ml')
    quantity = int(request.args.get('quantity', 1))
    product = Product.query.get_or_404(product_id)
    base_price = product.price_100ml if size == '100ml' and product.price_100ml else product.price
    price_paid = round(base_price * (1 - (product.discount or 0) / 100), 2)
    item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id, size=size).first()
    if item:
        item.quantity += quantity
        item.price_paid = price_paid
    else:
        item = CartItem(user_id=current_user.id, product_id=product_id, size=size, quantity=quantity, price_paid=price_paid)
        db.session.add(item)
    db.session.commit()
    total = sum(i.quantity for i in current_user.cart_items)
    return jsonify({'success': True, 'cart_count': total})

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
    total = sum((i.price_paid if i.price_paid else i.product.price) * i.quantity for i in items)
    return render_template('cart.html', items=items, total=total)
