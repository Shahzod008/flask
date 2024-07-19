from flask_login import current_user
from functools import wraps
from sweater import app, login_manager
from flask import abort, flash, redirect, url_for, request, render_template
import os


def get_path_for_image(secured_filename, separate=False):
    folder = app.config["UPLOAD_IMAGE_DEST"]
    if separate:
        return folder, secured_filename
    return os.path.join(folder, secured_filename)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Пожалуйста, войдите в систему", "danger")
            return redirect(url_for('login_page'))
        if not current_user.is_admin:
            flash("У вас нет прав доступа к этому ресурсу", "danger")
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


@app.after_request
def redirect_to_signin(response):
    if response.status_code == 401:
        return redirect(url_for('login_page') + '?next=' + request.url)
    return response


@login_manager.unauthorized_handler
def unauthorized():
    flash(login_manager.login_message)
    return redirect(url_for('login_page'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404


@app.errorhandler(403)
def page_not_found(e):
    return render_template('errors/403.html'), 403


@app.errorhandler(500)
def page_not_found(e):
    return render_template('errors/500.html'), 500