import re

from flask_login import current_user

from sweater import app
from sweater.models import Product, Category, Gender, Country, Size, Season, User, Favorite, CartItem, ProductImage
from flask import render_template, request, redirect, flash, url_for, send_from_directory, jsonify


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
        highlighted_title = re.sub(f"({re.escape(query)})", r"<strong>\1</strong>",
                                   product.title, flags=re.IGNORECASE)
        highlighted_description = re.sub(f"({re.escape(query)})", r"<strong>\1</strong>",
                                         product.description, flags=re.IGNORECASE)
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
        products = Product.query.filter(Product.title.ilike(f"%{query}%")).all()
        suggestions = [product.title for product in products]
    else:
        suggestions = []

    return jsonify(suggestions)
