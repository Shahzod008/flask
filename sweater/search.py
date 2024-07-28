import re

from sweater import app
from sweater.models import Product
from flask import render_template, request, jsonify


@app.route("/search", methods=['GET'])
def search():
    query = request.args.get('query')

    if query:
        products = Product.query.filter((Product.keywords.ilike(f"%{query}%")) | (Product.title.ilike(f"%{query}%")) | (Product.id == query)).all()
    else:
        products = []

    highlighted_products = []
    for product in products:
        highlighted_keywords = re.sub(f"({re.escape(query)})", r"<strong>\1</strong>", product.keywords, flags=re.IGNORECASE)
        highlighted_title = re.sub(f"({re.escape(query)})", r"<strong>\1</strong>", product.title, flags=re.IGNORECASE)
        highlighted_products.append({'product': product, 'highlighted_keywords': highlighted_keywords, 'highlighted_title': highlighted_title})

    return render_template(template_name_or_list="search_results.html", products=highlighted_products, query=query)