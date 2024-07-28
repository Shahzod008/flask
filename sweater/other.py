from sweater import app
from flask import render_template


@app.route("/faq")
def faq():
    return render_template("faq.html")


@app.route("/politics")
def politics():
    return render_template(
        template_name_or_list="politics.html",
        shop_name="Мой стиль",
        shop_phone="+79966636043",
        return_email="shahzodergashev2555@gmail.com"
    )


@app.route("/terms")
def terms():
    return render_template(
        template_name_or_list="terms.html",
        shop_name="Мой стиль",
        shop_website="http://127.0.0.1:5000/",
        shop_phone="+79966636043",
        shop_email="shahzodergashev2555@gmail.com"
    )
