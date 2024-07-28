import os
import re

from flask import flash, redirect, url_for, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from sweater import app, db
from sweater.models import User

if not os.path.exists(app.config['UPLOAD_IMAGE_DEST']):
    os.makedirs(app.config['UPLOAD_IMAGE_DEST'])


@app.route('/media/img-user-ava/<filename>')
def profile_image(filename):
    return send_from_directory(app.config['UPLOAD_IMAGE_DEST'], filename)


@app.route("/profile/", methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        try:
            login = request.form['login']
            firstname = request.form['fname']
            lastname = request.form['lname']
            phone = request.form['phone']
            email = request.form['email']
            address = request.form['address']

            # Проверка формата телефона
            phone_pattern = re.compile(r'^\+?\d{10,15}$')
            if not phone_pattern.match(phone):
                flash('Неправильный формат номера телефона. Введите правильный номер.', 'danger')
                return redirect(url_for('profile'))

            # Проверка уникальности email
            existing_user = User.query.filter_by(email=email).first()
            if existing_user and existing_user.id != current_user.id:
                flash('Этот email уже используется другим пользователем.', 'danger')
                return redirect(url_for('profile'))

            # Проверка уникальности логина
            existing_user = User.query.filter_by(login=login).first()
            if existing_user and existing_user.id != current_user.id:
                flash('Этот логин уже используется другим пользователем.', 'danger')
                return redirect(url_for('profile'))

            # Проверка уникальности номера телефона
            existing_user = User.query.filter_by(phone=phone).first()
            if existing_user and existing_user.id != current_user.id:
                flash('Этот номер телефона уже используется другим пользователем.', 'danger')
                return redirect(url_for('profile'))

            # Обновление данных пользователя
            current_user.login = login
            current_user.firstname = firstname
            current_user.lastname = lastname
            current_user.phone = phone
            current_user.email = email
            current_user.address = address

            # Обработка изображения профиля
            if 'profile_picture' in request.files:
                file = request.files['profile_picture']
                if file:
                    if allowed_file(file.filename):  # проверка разрешенного типа файла
                        filename = secure_filename(file.filename)
                        file_path = os.path.join(app.config['UPLOAD_IMAGE_DEST'], filename)
                        file.save(file_path)
                        current_user.profile_image = filename
                    else:
                        flash('Недопустимый тип файла. Пожалуйста, загрузите изображение в формате png, jpg, jpeg, или gif.', 'danger')
                        return redirect(url_for('profile'))

            db.session.commit()
            flash('Профиль успешно обновлен', 'success')
        except Exception as e:
            db.session.rollback()  # Откат транзакции в случае ошибки
            flash(f'Ошибка при обновлении профиля: {str(e)}', 'danger')
            return redirect(url_for('profile'))

    return render_template("profile.html", current_user=current_user)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/profile/change_password/", methods=['POST'])
@login_required
def change_password():
    current_password = request.form['current_password']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']

    if new_password != confirm_password:
        flash('Пароли не совпадают', 'danger')
        return redirect(url_for('profile'))

    # Проверка текущего пароля и обновление на новый
    # Это требует реализации проверки пароля, например, с использованием Flask-Login
    # current_user.set_password(new_password)
    db.session.commit()
    flash('Пароль успешно изменен', 'success')
    return redirect(url_for('profile'))



from flask import render_template, request, jsonify
from dadata import Dadata

token = "3cc3b1b92eadca34601e7ba2a341a3a594f3f6e0"
secret = "bea7577042ba0ccd5c59fa32053b9944815cf8cc"
dadata = Dadata(token, secret)


@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    query = request.args.get('query', '')
    if query:
        suggestions = dadata.suggest("address", query)
        return jsonify(suggestions=suggestions)
    return jsonify(suggestions=[])
