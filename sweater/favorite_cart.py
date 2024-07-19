from flask import render_template, request, redirect, flash
from sweater.models import Product, Favorite, CartItem
from flask_login import login_required, current_user
from sweater import app, db


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
