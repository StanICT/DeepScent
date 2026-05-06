from .extensions import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    avatar = db.Column(db.String(150), nullable=True)
    fullname = db.Column(db.String(150), default='')
    cart_items = db.relationship('CartItem', backref='user', lazy=True)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    size = db.Column(db.String(10), default='50ml')
    product = db.relationship('Product')

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock_50ml = db.Column(db.Integer, default=0)
    stock_100ml = db.Column(db.Integer, default=0)
    price_100ml = db.Column(db.Float, nullable=True)
    image = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(20), default='UNISEX')

class Brand(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    logo = db.Column(db.String(150), nullable=True)
