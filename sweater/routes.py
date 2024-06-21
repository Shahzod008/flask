import os.path

from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename

from sweater import app, db, login_manager
from werkzeug.security import check_password_hash, generate_password_hash

from sweater.forms import SignUpForm, SignInForm, ProductForm
from sweater.models import Product, Category, User, Favorite, CartItem, ProductImage
from flask import render_template, request, redirect, flash, url_for, send_from_directory

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
        flash(f"Не удалось добавить в избранное: {str(e)}")
    return redirect(request.referrer)


@app.route("/remove-from-favorites/<int:product_id>", methods=['POST'])
@login_required
def remove_from_favorites(product_id):
    favorite = Favorite.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if favorite:
        try:
            db.session.delete(favorite)
            db.session.commit()
            flash("Товар удален из избранного.")
        except Exception as e:
            flash(f"Не удалось удалить из избранного: {str(e)}")
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
        flash(f"Не удалось добавить в корзину: {str(e)}")
    return redirect(request.referrer)


@app.route("/update_cart/<int:cart_item_id>", methods=["POST"])
@login_required
def update_cart(cart_item_id):
    cart_item = CartItem.query.get_or_404(cart_item_id)
    quantity = request.form.get('quantity', type=int)

    if quantity and quantity > 0:
        cart_item.quantity = quantity
        db.session.commit()
        flash("Количество товара обновлено", "success")
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
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    return render_template("cart.html", cart_items=cart_items, total_price=total_price)


@app.route("/favorites")
@login_required
def view_favorites():
    favorites = Favorite.query.filter_by(user_id=current_user.id).all()
    return render_template("favorites.html", favorites=favorites)


@app.route("/detail-product/<int:id>")
@login_required
def detail_product(id):
    product = Product.query.get(id)
    if not product:
        flash("Товар не найден.", "danger")
        return redirect(url_for('products'))

    favorite_product_ids = [fav.product_id for fav in current_user.favorites]
    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=id).first()

    return render_template(
        template_name_or_list="detail-product.html",
        favorite_product_ids=favorite_product_ids,
        cart_item=cart_item, product=product
    )


@app.route("/new-product", methods=['POST', 'GET'])
@login_required
def new_product():
    form = ProductForm()
    if form.validate_on_submit():
        title = form.data['title']
        price = form.data['price']
        size = form.data['size']
        ideal = form.data['ideal']
        intro = form.data['intro']
        description = form.data['description']
        category_id = form.data['category_id']

        product_new = Product(
            title=title, price=price, size=size,
            ideal=ideal, intro=intro, description=description,
            category_id=category_id
        )

        images = []
        try:
            db.session.add(product_new)
            db.session.commit()
            folder = get_path_for_image("a.png", True)[0]
            if not os.path.exists(folder):
                os.makedirs(folder)
            for image in form.images.data:
                secured_filename = secure_filename(image.filename)
                image_path = get_path_for_image(secured_filename)
                image.save(image_path)
                # filename = str(image_num) + "_pr_" + str(product_new.id)
                new_image = ProductImage(image=secured_filename, product_id=product_new.id)
                db.session.add(new_image)
                db.session.commit()
                images.append(new_image)
            return redirect(request.referrer)
        except Exception as e:
            db.session.delete(product_new)
            db.session.commit()
            for i in images:
                db.session.delete(i)
                db.session.commit()
            return f"Что-то пошло не так: {str(e)}"
    return render_template(
        template_name_or_list="new-product.html",
        # categories=Category.query.all(),
        form=form
    )


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
                flash('Неверный логин или пароль')
        else:
            flash('Пожалуйста, введите логин и пароль')

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
            flash('Пользователь с таким логином уже существует')
        else:
            hash_pwd = generate_password_hash(password)
            new_user = User(login=login, password=hash_pwd, is_admin=bool(is_admin))
            db.session.add(new_user), db.session.commit()
            flash('Вы успешно зарегистрировались! Теперь войдите в систему.')
            return redirect(url_for('login_page'))

    return render_template('register.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы.')
    return redirect(url_for('login_page'))


@app.route("/product")
@login_required
def products():
    category_id = request.args.get('category_id')
    if category_id:
        products = Product.query.filter_by(category_id=category_id).order_by(Product.date.desc()).all()
    else:
        products = Product.query.order_by(Product.date.desc()).all()

    num_product = len(products)
    categories = Category.query.join(Product).group_by(Category.id).all()
    favorite_product_ids = [fav.product_id for fav in current_user.favorites]
    return render_template(
        template_name_or_list="products.html",
        favorite_product_ids=favorite_product_ids,
        products=products,
        categories=categories,
        num_product=num_product,
        selected_category=category_id
    )


@app.route("/")
@login_required
def home():
    products = Product.query.order_by(Product.date.desc()).limit(9).all()
    favorite_product_ids = [fav.product_id for fav in current_user.favorites]
    num_product = len(products)
    return render_template(
        favorite_product_ids=favorite_product_ids,
        template_name_or_list="index.html",
        products=products,
        num_product=num_product
    )


@app.route("/about")
@login_required
def about():
    return render_template("about.html")


@app.route("/categories", methods=['POST', 'GET'])
@login_required
def manage_categories():
    if request.method == "POST":
        name = request.form['name']

        try:
            db.session.add(Category(name=name))
            db.session.commit()
            return redirect('/categories')
        except Exception as e:
            return f"Что-то пошло не так: {str(e)}"
    else:
        categories = Category.query.all()
        num_categories = len(categories)
        return render_template(
            template_name_or_list="categories.html",
            categories=categories,
            num_categories=num_categories
        )


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
