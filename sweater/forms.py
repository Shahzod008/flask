from flask_wtf import FlaskForm
from wtforms.fields.choices import SelectField
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.fields import MultipleFileField
from wtforms.validators import DataRequired, EqualTo

from sweater.models import Category


class SignUpForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField('Подтверждение пароля', validators=[DataRequired(), EqualTo('password')])
    is_admin = BooleanField('Администратор')
    submit = SubmitField('Зарегистрироваться')


class SignInForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')


class ProductForm(FlaskForm):
    title = StringField('Название товара', validators=[DataRequired()])
    price = IntegerField('Цена товара', validators=[DataRequired()])
    ideal = StringField('Для чего подходит', validators=[DataRequired()])
    material = StringField('Материал', validators=[DataRequired()])
    size = StringField('Размер', validators=[DataRequired()])
    washing_temperature = StringField('Температура стирки', validators=[DataRequired()])
    ironing_temperature = StringField('Температура глажки', validators=[DataRequired()])
    equipment = StringField('Комплектация', validators=[DataRequired()])
    warranty_date = StringField('Срок гарантии (месяцы)', validators=[DataRequired()])
    intro = TextAreaField('Микро описание', validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[DataRequired()])
    category_id = SelectField('Категория', choices=[], validators=[DataRequired()])
    images = MultipleFileField('Изображения товара', validators=[DataRequired()], render_kw={'multiple': True})

    # Пример получения категорий из базы данных (вам нужно будет реализовать это)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.category_id.choices = [(category.id, category.name)
                                    for category in Category.query.all()]

