from sweater.categories import *
from sweater.favorite_cart import *
from sweater.reg_auth import *
from sweater.product import *
from sweater.search import *
from sweater.user import *
from sweater.other import *


@app.route("/")
def home():
    category_id = request.args.get('category_id')
    if category_id:
        products = Product.query.filter_by(category_id=category_id).order_by(Product.date.desc()).all()
    else:
        products = Product.query.order_by(Product.date.desc()).limit(9).all()
    # categories = Category.query.join(Product).group_by(Category.id).all()
    categories = Category.query.all()
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
