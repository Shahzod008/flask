import os.path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__, static_folder='media', static_url_path='/media')
login_manager = LoginManager(app)
login_manager.login_view = 'login_page'
app.secret_key = ('ьлотрипмасвкеанпгршоьBgvr5e4s56e57r6t7y8u-k=]90ijbdn0emowucw1!@#$%^&*()_)')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///online-store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['UPLOAD_IMAGE_DEST'] = os.path.join(BASE_DIR, 'media', 'img-user-ava')
app.config["TEMPLATES_AUTO_RELOAD"] = True
login_manager.login_view = 'login_page'
login_manager.login_message = 'Пожалуйста, войдите, чтобы получить доступ к этой странице.'


db = SQLAlchemy(app)

from sweater import models, routes

with app.app_context():
    db.create_all()