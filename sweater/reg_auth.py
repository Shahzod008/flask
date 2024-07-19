from flask_login import login_user, login_required, logout_user

from sweater import app, db
from werkzeug.security import check_password_hash, generate_password_hash

from sweater.forms import SignUpForm, SignInForm
from sweater.models import User
from flask import render_template, request, redirect, flash, url_for


@app.route('/login', methods=['POST', 'GET'])
def login_page():
    form = SignInForm()
    if form.validate_on_submit():
        login = form.data["login"]
        password = form.data["password"]

        if login and password:
            user = User.query.filter_by(login=login).first()

            if user and check_password_hash(user.password, password):
                login_user(user)
                next_page = request.args.get('next')
                return redirect(next_page or url_for('home'))
            else:
                flash('Неверный логин или пароль', "danger")
        else:
            flash('Пожалуйста, введите логин и пароль', "danger")

    return render_template('login.html', form=form)


@app.route('/register', methods=['POST', 'GET'])
def register():
    form = SignUpForm()
    if form.validate_on_submit():
        login = form.data["login"]
        password = form.data["password"]
        is_admin = form.data["is_admin"]

        if User.query.filter_by(login=login).first():
            flash('Пользователь с таким логином уже существует', "danger")
        else:
            hash_pwd = generate_password_hash(password)
            new_user = User(login=login, password=hash_pwd, is_admin=bool(is_admin))
            db.session.add(new_user), db.session.commit()
            flash('Вы успешно зарегистрировались! Теперь войдите в систему.', "success")
            return redirect(url_for('login_page'))

    return render_template('register.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login_page'))
