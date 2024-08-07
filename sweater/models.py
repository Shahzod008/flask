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
    price = db.Column(db.Integer, nullable=False)
    ideal = db.Column(db.String, nullable=False)
    warranty_date = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)
    color = db.Column(db.String(7), nullable=False)
    price_discount = db.Column(db.Integer, nullable=False)
    package_size = db.Column(db.Text, nullable=False)
    brand = db.Column(db.Text, nullable=False)
    keywords = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    category = db.relationship('Category', back_populates='products')
    season_id = db.Column(db.Integer, db.ForeignKey('season.id'), nullable=False)
    season = db.relationship('Season', back_populates='products')
    country_id = db.Column(db.Integer, db.ForeignKey('country.id'), nullable=False)
    country = db.relationship('Country', back_populates='products')
    gender_id = db.Column(db.Integer, db.ForeignKey('gender.id'), nullable=False)
    gender = db.relationship('Gender', back_populates='products')
    size_id = db.Column(db.Integer, db.ForeignKey('size.id'), nullable=False)
    size = db.relationship('Size', back_populates='products')
    images = db.relationship('ProductImage', backref='products', lazy=True, cascade="all, delete-orphan")
    date = db.Column(db.DateTime, default=datetime.now)


class Country(db.Model):
    __tablename__ = 'country'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), unique=True, nullable=False)

    products = db.relationship('Product', back_populates='country')


class Size(db.Model):
    __tablename__ = 'size'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), unique=True, nullable=False)

    products = db.relationship('Product', back_populates='size')


class Gender(db.Model):
    __tablename__ = 'gender'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    products = db.relationship('Product', back_populates='gender')


class Season(db.Model):
    __tablename__ = 'season'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    products = db.relationship('Product', back_populates='season')


class ProductImage(db.Model):
    __tablename__ = "product_images"

    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    products = db.relationship('Product', back_populates='category')


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


class UserImage(db.Model):
    __tablename__ = "user_image"

    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    login = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=True)

    address = db.Column(db.String, nullable=True)
    phone = db.Column(db.String(15), nullable=True)
    firstname = db.Column(db.String(50), nullable=True)
    lastname = db.Column(db.String(50), nullable=True)

    is_admin = db.Column(db.Boolean, default=False)

    date = db.Column(db.DateTime, default=datetime.now)

    favorites = db.relationship('Favorite', back_populates='user')
    cart_items = db.relationship('CartItem', back_populates='user', lazy='dynamic')

    profile_image = db.Column(db.String(255), nullable=True)