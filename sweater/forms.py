from wtforms.fields.simple import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, ColorField
from sweater.models import Category, Season, Gender, Size, Country
from wtforms.validators import DataRequired, EqualTo
from wtforms.fields.numeric import IntegerField
from wtforms.fields.choices import SelectField
from wtforms.fields import MultipleFileField
from flask_wtf import FlaskForm


class ProductForm(FlaskForm):
    title = StringField('Название товара', validators=[DataRequired()])
    price = IntegerField('Цена товара', validators=[DataRequired()])
    ideal = StringField('Для чего подходит', validators=[DataRequired()])
    warranty_date = StringField('Срок гарантии (месяцы)', validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[DataRequired()])
    color = ColorField('Цвет', validators=[DataRequired()])
    price_discount = IntegerField('Цена со скидкой', validators=[DataRequired()])
    package_size = StringField('Размер и вес упаковки в граммах и в миллиметрах: длина, ширина, высота, вес',
                               validators=[DataRequired()])
    brand = StringField('Бренд', validators=[DataRequired()])
    keywords = TextAreaField('ключевые слова для поиска', validators=[DataRequired()])
    category_id = SelectField('Категория', choices=[], validators=[DataRequired()])
    season_id = SelectField('В какой сезон лучше подойдет товар', choices=[], validators=[DataRequired()])
    country_id = SelectField('Страна', choices=[], validators=[DataRequired()])
    gender_id = SelectField('Пол', choices=[], validators=[DataRequired()])
    size_id = SelectField('Размер', choices=[], validators=[DataRequired()])
    images = MultipleFileField('Изображения товара', validators=[DataRequired()], render_kw={'multiple': True})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.category_id.choices = [(category.id, category.name) for category in Category.query.all()]
        self.size_id.choices = [(size.id, size.name) for size in Size.query.all()]
        self.season_id.choices = [(season.id, season.name) for season in Season.query.all()]
        self.gender_id.choices = [(gender.id, gender.name) for gender in Gender.query.all()]
        self.country_id.choices = [(country.id, country.name) for country in Country.query.all()]


class SignInForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')


class SignUpForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField('Подтверждение пароля', validators=[DataRequired(), EqualTo('password')])
    is_admin = BooleanField('Администратор')
    submit = SubmitField('Зарегистрироваться')
