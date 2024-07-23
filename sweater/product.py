from sweater.models import Product, Category, CartItem, ProductImage, Gender, Size, Season, Country
from flask import render_template, request, redirect, url_for, send_from_directory
from sweater.utils import get_path_for_image, admin_required
from werkzeug.utils import secure_filename
from sweater.forms import ProductForm
from flask_login import current_user
from sweater import app, db
import os.path


@app.route("/new-product", methods=['POST', 'GET'])
@admin_required
def new_product():
    form = ProductForm()
    if form.validate_on_submit():
        try:
            product_new = Product(
                title=form.title.data,
                price=form.price.data,
                ideal=form.ideal.data,
                warranty_date=form.warranty_date.data,
                description=form.description.data,
                category_id=form.category_id.data,
                season_id=form.season_id.data,
                size_id=form.size_id.data,
                gender_id=form.gender_id.data,
                country_id=form.country_id.data,
                color=form.color.data,
                price_discount=form.price_discount.data,
                package_size=form.package_size.data,
                brand=form.brand.data,
                keywords=form.keywords.data
            )
            db.session.add(product_new)
            db.session.commit()

            # Handling images
            images = []
            folder = get_path_for_image("a.png", True)[0]
            if not os.path.exists(folder):
                os.makedirs(folder)
            for image in form.images.data:
                secured_filename = secure_filename(image.filename)
                image_path = get_path_for_image(secured_filename)
                image.save(image_path)
                new_image = ProductImage(image=secured_filename, product_id=product_new.id)
                db.session.add(new_image)
                images.append(new_image)

            db.session.commit()
            return redirect(url_for('new_product'))

        except Exception as e:
            db.session.rollback()
            return f"Что-то пошло не так: {str(e)}"
    return render_template("new-product.html", form=form)


@app.route("/detail-product/<int:id>")
def detail_product(id):
    product = Product.query.get_or_404(id)
    favorite_product_ids = [fav.product_id for fav in current_user.favorites] if current_user.is_authenticated else []
    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=id).first() if current_user.is_authenticated else None

    return render_template(
        "detail-product.html",
        favorite_product_ids=favorite_product_ids,
        cart_item=cart_item,
        product=product
    )


@app.route("/product/img/<filename>")
def product_image(filename):
    return send_from_directory(*get_path_for_image(filename, True))


@app.route("/product")
def products():
    selected_category = request.args.get('category_id', type=int)
    selected_gender = request.args.get('gender_id', type=int)
    selected_season = request.args.get('season_id', type=int)
    selected_country = request.args.get('country_id', type=int)
    selected_size = request.args.get('size_id', type=int)

    filters = {}
    if selected_category:
        filters['category_id'] = selected_category
    if selected_gender:
        filters['gender_id'] = selected_gender
    if selected_size:
        filters['size_id'] = selected_size
    if selected_country:
        filters['country_id'] = selected_country
    if selected_season:
        filters['season_id'] = selected_season

    products = Product.query.filter_by(**filters).all()

    # Получаем только связанные объекты для текущих фильтров
    category_ids = {p.category_id for p in products}
    gender_ids = {p.gender_id for p in products}
    size_ids = {p.size_id for p in products}
    country_ids = {p.country_id for p in products}
    season_ids = {p.season_id for p in products}

    categories = Category.query.filter(Category.id.in_(category_ids)).all()
    genders = Gender.query.filter(Gender.id.in_(gender_ids)).all()
    sizes = Size.query.filter(Size.id.in_(size_ids)).all()
    countries = Country.query.filter(Country.id.in_(country_ids)).all()
    seasons = Season.query.filter(Season.id.in_(season_ids)).all()

    num_products = len(products)
    favorite_product_ids = [fav.product_id for fav in current_user.favorites] if current_user.is_authenticated else []

    return render_template(
        "products.html",
        favorite_product_ids=favorite_product_ids,
        products=products,
        sizes=sizes,
        categories=categories,
        countries=countries,
        seasons=seasons,
        genders=genders,
        selected_category=selected_category,
        selected_size=selected_size,
        selected_country=selected_country,
        selected_season=selected_season,
        selected_gender=selected_gender,
        num_product=num_products
    )



@app.route('/delete-product/<int:id>')
@admin_required
def delete_product(id):
    product = Product.query.get(id)
    if product:
        try:
            db.session.delete(product)
            db.session.commit()
            return redirect(url_for('home'))
        except Exception as e:
            return f"Не удалось удалить продукт причина:{str(e)}"
    else:
        return "Категория не найдена."
