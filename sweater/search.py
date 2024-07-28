import re

from flask_login import current_user

from sweater import app
from sweater.models import Product
from flask import render_template, request, jsonify


@app.route("/search", methods=['GET'])
def search():
    query = request.args.get('query')

    if query:
        products = Product.query.filter(
            (Product.keywords.ilike(f"%{query}%")) |
            (Product.id == query)
        ).all()
    else:
        products = []

    product = products
    favorite_product_ids = [fav.product_id for fav in current_user.favorites] if current_user.is_authenticated else []

    highlighted_products = []
    for product in products:
        highlighted_keywords = re.sub(f"({re.escape(query)})", r"<strong>\1</strong>", product.keywords, flags=re.IGNORECASE)

        highlighted_products.append({
            'product': product,
            'highlighted_keywords': highlighted_keywords,
        })

    return render_template(
        "search_results.html",
        products=highlighted_products,
        num_product=product,
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
