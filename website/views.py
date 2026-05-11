from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import current_user, login_required
from website.models import Product, Brand, CartItem, Favorite, Order, OrderItem, Review
from website.extensions import db

views = Blueprint('views', __name__)

@views.route('/')
def home():
    brands = Brand.query.all()
    return render_template('home.html', brands=brands)

@views.route('/perfumes/<brand>')
def perfumes(brand):
    products = Product.query.filter_by(brand=brand).all()
    brand_obj = Brand.query.filter_by(name=brand).first()
    favorited_ids = [f.product_id for f in current_user.favorites] if current_user.is_authenticated else []
    ratings = {}
    for p in products:
        reviews = Review.query.filter_by(product_id=p.id).all()
        ratings[p.id] = {'avg': round(sum(r.rating for r in reviews) / len(reviews), 1) if reviews else 0, 'count': len(reviews)}
    return render_template("perfumes.html",
                           products=products,
                           brand=brand,
                           brand_obj=brand_obj,
                           bg_image="prmnky-bg.jpg",
                           favorited_ids=favorited_ids,
                           ratings=ratings)

@views.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    favorited = False
    can_review = False
    if current_user.is_authenticated:
        favorited = Favorite.query.filter_by(user_id=current_user.id, product_id=product_id).first() is not None
        can_review = db.session.query(Order).filter(
            Order.user_id == current_user.id,
            Order.status == 'Completed',
            Order.items.any(OrderItem.product_id == product_id)
        ).first() is not None
    reviews = Review.query.filter_by(product_id=product_id).order_by(Review.created_at.desc()).all()
    avg_rating = round(sum(r.rating for r in reviews) / len(reviews), 1) if reviews else 0
    user_reviewed = Review.query.filter_by(user_id=current_user.id, product_id=product_id).first() if current_user.is_authenticated else None
    return render_template('product_detail.html', product=product, favorited=favorited, reviews=reviews, avg_rating=avg_rating, user_reviewed=user_reviewed, can_review=can_review)

@views.route('/review/<int:product_id>', methods=['POST'])
@login_required
def add_review(product_id):
    if Review.query.filter_by(user_id=current_user.id, product_id=product_id).first():
        return jsonify({'success': False, 'message': 'You already reviewed this product.'})
    rating = int(request.json.get('rating', 5))
    comment = request.json.get('comment', '').strip()
    review = Review(user_id=current_user.id, product_id=product_id, rating=rating, comment=comment)
    db.session.add(review)
    db.session.commit()
    reviews = Review.query.filter_by(product_id=product_id).all()
    avg = round(sum(r.rating for r in reviews) / len(reviews), 1)
    return jsonify({'success': True, 'username': current_user.username, 'rating': rating, 'comment': comment, 'avg_rating': avg, 'count': len(reviews)})

@views.route('/product')
def product():
    products = Product.query.all()
    favorited_ids = [f.product_id for f in current_user.favorites] if current_user.is_authenticated else []
    ratings = {}
    for p in products:
        reviews = Review.query.filter_by(product_id=p.id).all()
        ratings[p.id] = {'avg': round(sum(r.rating for r in reviews) / len(reviews), 1) if reviews else 0, 'count': len(reviews)}
    return render_template('product.html', products=products, favorited_ids=favorited_ids, ratings=ratings)

@views.route('/search')
def search():
    q = request.args.get('q', '').strip()
    results = Product.query.filter(
        Product.name.ilike(f'%{q}%') | Product.brand.ilike(f'%{q}%')
    ).all() if q else []
    favorited_ids = [f.product_id for f in current_user.favorites] if current_user.is_authenticated else []
    ratings = {}
    for p in results:
        reviews = Review.query.filter_by(product_id=p.id).all()
        ratings[p.id] = {'avg': round(sum(r.rating for r in reviews) / len(reviews), 1) if reviews else 0, 'count': len(reviews)}
    return render_template('search.html', results=results, query=q, favorited_ids=favorited_ids, ratings=ratings)

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

    # Count already in cart for this product+size
    in_cart = db.session.query(db.func.sum(CartItem.quantity)).filter_by(
        user_id=current_user.id, product_id=product_id, size=size
    ).scalar() or 0

    stock = (product.stock_50ml or 0) if size == '50ml' else (product.stock_100ml or 0)
    if stock == 0:
        return jsonify({'success': False, 'message': f'{product.name} ({size}) is currently out of stock.'})
    if in_cart + quantity > stock:
        msg = f'{product.name} ({size}) only has {stock} left.' if in_cart == 0 else f'{product.name} ({size}) only has {stock} left ({in_cart} already in cart).'
        return jsonify({'success': False, 'message': msg})

    base_price = product.price_100ml if size == '100ml' and product.price_100ml else product.price
    price_paid = round(base_price * (1 - (product.discount or 0) / 100), 2)
    item = CartItem(user_id=current_user.id, product_id=product_id, size=size, quantity=quantity, price_paid=price_paid)
    db.session.add(item)
    db.session.commit()
    total = sum(i.quantity for i in current_user.cart_items)
    return jsonify({'success': True, 'cart_count': total})

@views.route('/cart/update/<int:item_id>', methods=['POST'])
@login_required
def update_cart_quantity(item_id):
    item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    quantity = int(request.json.get('quantity', 1))
    if quantity < 1:
        quantity = 1
    item.quantity = quantity
    db.session.commit()
    subtotal = round((item.price_paid if item.price_paid else item.product.price) * quantity, 2)
    total_count = sum(i.quantity for i in current_user.cart_items)
    return jsonify({'success': True, 'subtotal': subtotal, 'cart_count': total_count})

@views.route('/cart/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first()
    if item:
        db.session.delete(item)
        db.session.commit()
    total = sum(i.quantity for i in current_user.cart_items)
    return jsonify({'success': True, 'cart_count': total})

@views.route('/checkout', methods=['POST'])
@login_required
def checkout():
    item_ids = request.json.get('item_ids', [])
    if not item_ids:
        return jsonify({'success': False, 'message': 'No items selected.'})

    items = CartItem.query.filter(CartItem.id.in_(item_ids), CartItem.user_id == current_user.id).all()
    if not items:
        return jsonify({'success': False, 'message': 'No valid items found.'})

    # Check stock
    for item in items:
        if item.size == '50ml':
            if (item.product.stock_50ml or 0) < item.quantity:
                return jsonify({'success': False, 'message': f'{item.product.name} ({item.size}) is out of stock.'})
        else:
            if (item.product.stock_100ml or 0) < item.quantity:
                return jsonify({'success': False, 'message': f'{item.product.name} ({item.size}) is out of stock.'})

    total = sum((i.price_paid if i.price_paid else i.product.price) * i.quantity for i in items)
    order = Order(user_id=current_user.id, total=total)
    db.session.add(order)
    db.session.flush()

    for item in items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            size=item.size,
            price_paid=item.price_paid if item.price_paid else item.product.price
        )
        db.session.add(order_item)
        # Decrease stock
        if item.size == '50ml':
            item.product.stock_50ml = (item.product.stock_50ml or 0) - item.quantity
        else:
            item.product.stock_100ml = (item.product.stock_100ml or 0) - item.quantity
        db.session.delete(item)

    db.session.commit()
    cart_count = sum(i.quantity for i in current_user.cart_items)
    return jsonify({'success': True, 'order_id': order.id, 'cart_count': cart_count})

@views.route('/orders/panel')
@login_required
def orders_panel():
    user_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).limit(10).all()
    return jsonify({'orders': [{
        'id': o.id,
        'date': o.created_at.strftime('%b %d, %Y'),
        'status': o.status,
        'total': o.total,
        'items': [{'name': i.product.name, 'image': i.product.image, 'size': i.size, 'quantity': i.quantity} for i in o.items]
    } for o in user_orders]})

@views.route('/orders')
@login_required
def orders():
    user_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    reviewed_ids = [r.product_id for r in Review.query.filter_by(user_id=current_user.id).all()]
    return render_template('orders.html', orders=user_orders, reviewed_ids=reviewed_ids)

@views.route('/cart')
@login_required
def cart():
    items = CartItem.query.filter_by(user_id=current_user.id).order_by(CartItem.id.desc()).all()
    total = sum((i.price_paid if i.price_paid else i.product.price) * i.quantity for i in items)
    return render_template('cart.html', items=items, total=total)
