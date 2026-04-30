from flask import Blueprint, render_template

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
    return render_template('product.html')

@views.route('/featured')
def featured():
    return render_template('featured.html')


