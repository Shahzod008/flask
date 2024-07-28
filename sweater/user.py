import os
import re

from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from sweater import app, db

if not os.path.exists(app.config['UPLOAD_IMAGE_DEST']):
    os.makedirs(app.config['UPLOAD_IMAGE_DEST'])


@app.route("/profile/", methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        login = request.form['login']
        firstname = request.form['fname']
        lastname = request.form['lname']
        phone = request.form['phone']
        email = request.form['email']
        address = request.form['address']

        phone_pattern = re.compile(r'^\+?\d{10,15}$')
        if not phone_pattern.match(phone):
            flash('Неправильный формат номера телефона. Введите правильный номер.', 'danger')
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
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_IMAGE_DEST'], filename)
                file.save(file_path)

                current_user.profile_image = filename  # Установка имени файла в атрибут profile_image
                db.session.commit()

        db.session.commit()
        flash('Профиль успешно обновлен', 'success')
        return redirect(url_for('profile'))

    return render_template("profile.html", current_user=current_user)


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
