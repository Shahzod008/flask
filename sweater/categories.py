from sweater import app, db
from sweater.models import Category, Gender, Country, Size, Season
from flask import render_template, request, redirect

from sweater.utils import admin_required


@app.route("/categories", methods=['POST', 'GET'])
@admin_required
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
@admin_required
def delete_country(id):
    country = Country.query.get_or_404(id)
    try:
        db.session.delete(country)
        db.session.commit()
        return redirect('/categories')
    except Exception as e:
        return f"Не удалось удалить пол: {str(e)}"


@app.route("/delete_gender/<int:id>")
@admin_required
def delete_gender(id):
    gender = Gender.query.get_or_404(id)
    if gender:
        try:
            db.session.delete(gender)
            db.session.commit()
            return redirect('/categories')
        except Exception as e:
            return f"Не удалось удалить пол: {str(e)}"
    else:
        return "Категория не найдена."


@app.route("/delete_size/<int:id>")
@admin_required
def delete_size(id):
    size = Size.query.get_or_404(id)
    if size:
        try:
            db.session.delete(size)
            db.session.commit()
            return redirect('/categories')
        except Exception as e:
            return f"Не удалось удалить размер: {str(e)}"
    else:
        return "Категория не найдена."


@app.route("/delete_season/<int:id>")
@admin_required
def delete_season(id):
    season = Season.query.get_or_404(id)
    if season:
        try:
            db.session.delete(season)
            db.session.commit()
            return redirect('/categories')
        except Exception as e:
            return f"Не удалось удалить сезон: {str(e)}"
    else:
        return "Категория не найдена."


@app.route("/delete-category/<int:id>")
@admin_required
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
