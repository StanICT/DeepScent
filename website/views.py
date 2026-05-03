from flask import Blueprint, render_template, request

from website.models import Product

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template('home.html')

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


