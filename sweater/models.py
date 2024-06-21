from datetime import datetime

from flask_login import UserMixin

from sweater import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), nullable=False)
    ideal = db.Column(db.String)
    material = db.Column(db.String)
    washing_temperature = db.Column(db.String)
    ironing_temperature = db.Column(db.String)
    equipment = db.Column(db.String)
    warranty_date = db.Column(db.Integer)
    price = db.Column(db.Integer, nullable=False)
    size = db.Column(db.Integer)
    intro = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.now)

    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    category = db.relationship('Category', back_populates='products')

    images = db.relationship('ProductImage', backref='products', lazy=True, cascade="all, delete-orphan")


class ProductImage(db.Model):
    __tablename__ = "product_images"

    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)


class Favorite(db.Model):
    __tablename__ = 'favorites'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)

    user = db.relationship('User', back_populates='favorites')
    product = db.relationship('Product')


class CartItem(db.Model):
    __tablename__ = 'cart_items'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)

    user = db.relationship('User', back_populates='cart_items')
    product = db.relationship('Product')


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    products = db.relationship('Product', back_populates='category')


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    login = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    is_admin = db.Column(db.Boolean, default=False)

    date = db.Column(db.DateTime, default=datetime.now)

    favorites = db.relationship('Favorite', back_populates='user')
    cart_items = db.relationship('CartItem', back_populates='user', lazy='dynamic')