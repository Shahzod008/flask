import os.path
import re

from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename

from sweater import app, db, login_manager
from werkzeug.security import check_password_hash, generate_password_hash

from sweater.forms import SignUpForm, SignInForm, ProductForm
from sweater.models import Product, Category, Gender, Country, Size, Season, User, Favorite, CartItem, ProductImage
from flask import render_template, request, redirect, flash, url_for, send_from_directory, jsonify

from sweater.utils import get_path_for_image


@login_manager.unauthorized_handler
def unauthorized():
    flash(login_manager.login_message)
    return redirect(url_for('login_page'))


@app.route("/add-to-favorites/<int:product_id>", methods=['POST'])
@login_required
def add_to_favorites(product_id):
    favorite = Favorite(user_id=current_user.id, product_id=product_id)
    try:
        db.session.add(favorite)
        db.session.commit()
    except Exception as e:
        flash(f"Не удалось добавить в избранное: {str(e)}", "danger")
    return redirect(request.referrer)


@app.route("/remove-from-favorites/<int:product_id>", methods=['POST'])
@login_required
def remove_from_favorites(product_id):
    favorite = Favorite.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if favorite:
        try:
            db.session.delete(favorite)
            db.session.commit()
            flash("Товар удален из избранного.", "danger")
        except Exception as e:
            flash(f"Не удалось удалить из избранного: {str(e)}", "danger")
    return redirect(request.referrer)


@app.route("/add-to-cart/<int:product_id>", methods=['POST'])
@login_required
def add_to_cart(product_id):
    quantity = request.form.get('quantity', 1)
    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if cart_item:
        cart_item.quantity += int(quantity)
    else:
        cart_item = CartItem(user_id=current_user.id, product_id=product_id, quantity=int(quantity))
    try:
        db.session.add(cart_item)
        db.session.commit()
    except Exception as e:
        flash(f"Не удалось добавить в корзину: {str(e)}", "danger")
    return redirect(request.referrer)


@app.route("/update_cart/<int:cart_item_id>", methods=["POST"])
@login_required
def update_cart(cart_item_id):
    cart_item = CartItem.query.get_or_404(cart_item_id)
    quantity = request.form.get('quantity', type=int)

    if quantity and quantity > 0:
        cart_item.quantity = quantity
        db.session.commit()
    else:
        flash("Некорректное количество", "danger")

    return redirect(request.referrer)


@app.route("/remove-from-cart/<int:cart_item_id>", methods=['POST'])
@login_required
def remove_from_cart(cart_item_id):
    cart_item = CartItem.query.get_or_404(cart_item_id)
    if cart_item.user_id == current_user.id:
        try:
            db.session.delete(cart_item)
            db.session.commit()
            flash("Товар удален из корзины.", "success")
        except Exception as e:
            flash(f"Не удалось удалить из корзины: {str(e)}", "danger")
    return redirect(request.referrer)


@app.route("/cart")
@login_required
def view_cart():
    products = Product.query.order_by(Product.date.desc()).all()
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    return render_template("cart.html", cart_items=cart_items, total_price=total_price, products=products)


@app.route("/favorites")
@login_required
def view_favorites():
    favorites = Favorite.query.filter_by(user_id=current_user.id).all()
    return render_template("favorites.html", favorites=favorites)


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


@app.route("/search", methods=['GET'])
def search():
    query = request.args.get('query')

    if query:
        products = Product.query.filter(
            (Product.title.ilike(f"%{query}%")) |
            (Product.description.ilike(f"%{query}%")) |
            (Product.id == query)
        ).all()
    else:
        products = []

    num_product = len(products)
    favorite_product_ids = [fav.product_id for fav in current_user.favorites] if current_user.is_authenticated else []

    highlighted_products = []
    for product in products:
        highlighted_title = re.sub(f"({re.escape(query)})", r"<strong>\1</strong>", product.title, flags=re.IGNORECASE)
        highlighted_description = re.sub(f"({re.escape(query)})", r"<strong>\1</strong>", product.description, flags=re.IGNORECASE)
        highlighted_products.append({
            'product': product,
            'highlighted_title': highlighted_title,
            'highlighted_description': highlighted_description
        })

    return render_template(
        "search_results.html",
        products=highlighted_products,
        num_product=num_product,
        favorite_product_ids=favorite_product_ids,
        query=query
    )


@app.route("/suggestions", methods=['GET'])
def suggestions():
    query = request.args.get('query', '')
    if query:
        products = Product.query.filter(
            Product.title.ilike(f"%{query}%")
        ).all()
        suggestions = [product.title for product in products]
    else:
        suggestions = []

    return jsonify(suggestions)


@app.route("/new-product", methods=['POST', 'GET'])
@login_required
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


@app.route("/product/img/<filename>")
def product_image(filename):
    return send_from_directory(*get_path_for_image(filename, True))


@app.route('/login', methods=['POST', 'GET'])
def login_page():
    form = SignInForm()
    if form.validate_on_submit():
        login = form.data["login"]
        password = form.data["password"]

        if login and password:
            user = User.query.filter_by(login=login).first()

            if user and check_password_hash(user.password, password):
                login_user(user)
                next_page = request.args.get('next')
                return redirect(next_page or url_for('home'))
            else:
                flash('Неверный логин или пароль', "danger")
        else:
            flash('Пожалуйста, введите логин и пароль', "danger")

    return render_template('login.html', form=form)


@app.after_request
def redirect_to_signin(response):
    if response.status_code == 401:
        return redirect(url_for('login_page') + '?next=' + request.url)
    return response


@app.route('/register', methods=['POST', 'GET'])
def register():
    form = SignUpForm()
    if form.validate_on_submit():
        login = form.data["login"]
        password = form.data["password"]
        is_admin = form.data["is_admin"]

        if User.query.filter_by(login=login).first():
            flash('Пользователь с таким логином уже существует', "danger")
        else:
            hash_pwd = generate_password_hash(password)
            new_user = User(login=login, password=hash_pwd, is_admin=bool(is_admin))
            db.session.add(new_user), db.session.commit()
            flash('Вы успешно зарегистрировались! Теперь войдите в систему.', "success")
            return redirect(url_for('login_page'))

    return render_template('register.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login_page'))


@app.route("/product")
def products():
    category_id = request.args.get('category_id')
    if category_id:
        products = Product.query.filter_by(category_id=category_id).order_by(Product.date.desc()).all()
    else:
        products = Product.query.order_by(Product.date.desc()).all()

    num_product = len(products)
    categories = Category.query.join(Product).group_by(Category.id).all()
    favorite_product_ids = [fav.product_id for fav in current_user.favorites] if current_user.is_authenticated else []
    return render_template(
        template_name_or_list="products.html",
        favorite_product_ids=favorite_product_ids,
        products=products,
        categories=categories,
        num_product=num_product,
        selected_category=category_id
    )


@app.route("/")
def home():
    category_id = request.args.get('category_id')
    if category_id:
        products = Product.query.filter_by(category_id=category_id).order_by(Product.date.desc()).all()
    else:
        products = Product.query.order_by(Product.date.desc()).limit(9).all()
    categories = Category.query.join(Product).group_by(Category.id).all()
    favorite_product_ids = [fav.product_id for fav in current_user.favorites] if current_user.is_authenticated else []
    num_product = len(products)

    return render_template(
        "index.html",
        favorite_product_ids=favorite_product_ids,
        products=products,
        categories=categories,
        selected_category=category_id,
        num_product=num_product
    )


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/categories", methods=['POST', 'GET'])
@login_required
def manage_categories():
    error_message = None
    if request.method == "POST":
        entity_type = request.form['entity_type']
        name = request.form['name']

        try:
            if entity_type == 'category':
                if not Category.query.filter_by(name=name).first():
                    db.session.add(Category(name=name))
                else:
                    error_message = "Категория с таким именем уже существует."
            elif entity_type == 'gender':
                if not Gender.query.filter_by(name=name).first():
                    db.session.add(Gender(name=name))
                else:
                    error_message = "Пол с таким именем уже существует."
            elif entity_type == 'size':
                if not Size.query.filter_by(name=name).first():
                    db.session.add(Size(name=name))
                else:
                    error_message = "Размер с таким именем уже существует."
            elif entity_type == 'season':
                if not Season.query.filter_by(name=name).first():
                    db.session.add(Season(name=name))
                else:
                    error_message = "Сезон с таким именем уже существует."
            elif entity_type == 'country':
                if not Country.query.filter_by(name=name).first():
                    db.session.add(Country(name=name))
                else:
                    error_message = "Страна с таким именем уже существует."

            if not error_message:
                db.session.commit()
                return redirect('/categories')
        except Exception as e:
            error_message = f"Что-то пошло не так: {str(e)}"

    categories = Category.query.all()
    genders = Gender.query.all()
    sizes = Size.query.all()
    countrys = Country.query.all()
    seasons = Season.query.all()
    num_categories = len(categories)
    return render_template(
        template_name_or_list="categories.html",
        genders=genders,
        sizes=sizes,
        countrys=countrys,
        seasons=seasons,
        categories=categories,
        num_categories=num_categories,
        error_message=error_message
    )


@app.route("/delete_country/<int:id>")
@login_required
def delete_country(id):
    country = Country.query.get_or_404(id)
    try:
        db.session.delete(country)
        db.session.commit()
        return redirect('/categories')
    except Exception as e:
        return f"Не удалось удалить пол: {str(e)}"


@app.route("/delete_gender/<int:id>")
@login_required
def delete_gender(id):
    gender = Gender.query.get_or_404(id)
    try:
        db.session.delete(gender)
        db.session.commit()
        return redirect('/categories')
    except Exception as e:
        return f"Не удалось удалить пол: {str(e)}"


@app.route("/delete_size/<int:id>")
@login_required
def delete_size(id):
    size = Size.query.get_or_404(id)
    try:
        db.session.delete(size)
        db.session.commit()
        return redirect('/categories')
    except Exception as e:
        return f"Не удалось удалить размер: {str(e)}"


@app.route("/delete_season/<int:id>")
@login_required
def delete_season(id):
    season = Season.query.get_or_404(id)
    try:
        db.session.delete(season)
        db.session.commit()
        return redirect('/categories')
    except Exception as e:
        return f"Не удалось удалить сезон: {str(e)}"


@app.route("/delete-category/<int:id>")
@login_required
def delete_category(id):
    category = Category.query.get(id)
    if category:
        if not category.products:
            try:
                db.session.delete(category)
                db.session.commit()
                return redirect('/categories')
            except Exception as e:
                return f"Не удалось удалить категорию: {str(e)}"
        else:
            return "Категория не может быть удалена, так как она содержит продукты."
    else:
        return "Категория не найдена."
